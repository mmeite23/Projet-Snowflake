# kafka_consumer_snowflake_PROD.py

import os
import json
import time
import signal
import logging
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv

# --- 1. CONFIGURATION AMÉLIORÉE ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

# Kafka Settings
TOPIC_NAME = os.getenv("KAFKA_TOPIC_NAME", "events")
DLQ_TOPIC_NAME = f"{TOPIC_NAME}_dlq"  # Dead-Letter Queue pour les messages invalides
BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")

# Snowflake Settings
# ... (tes configurations Snowflake restent les mêmes) ...
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
TARGET_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')

# --- 2. SCHÉMA SNOWFLAKE OPTIMISÉ POUR LE STREAMING (ELT) ---

def setup_snowflake_schema(engine):
    """
    Crée une table unique pour ingérer TOUS les événements bruts au format JSON.
    C'est la pierre angulaire de l'approche ELT. La transformation se fera DANS Snowflake.
    """
    RAW_TABLE_NAME = "RAW_EVENTS_STREAM"
    try:
        # Utiliser engine.begin() pour avoir un contexte transactionnel compatible
        # avec SQLAlchemy 1.4 (Engine.begin fournit une connexion transactionnelle).
        with engine.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TARGET_SCHEMA};"))
            connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {TARGET_SCHEMA}.{RAW_TABLE_NAME} (
                    EVENT_METADATA OBJECT NOT NULL, -- Stocke les métadonnées Kafka (offset, partition)
                    EVENT_CONTENT VARIANT NOT NULL, -- Stocke le JSON brut de l'événement
                    INGESTION_time TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP() -- Horodatage de l'ingestion
                );
            """))
        logging.info(f"Schéma Snowflake et table '{RAW_TABLE_NAME}' prêts pour l'ingestion.")
    except Exception as e:
        logging.critical(f"🛑 Erreur critique lors de la configuration du schéma Snowflake: {e}")
        raise

# --- 3. LOGIQUE D'INGESTION ROBUSTE (APPROCHE ELT) ---

def ingest_raw_events_batch(conn, batch):
    """
    Ingère un lot d'événements bruts dans la table de destination unique.
    Cette fonction est simple, rapide et fiable.
    """
    if not batch:
        return

    df = pd.DataFrame(batch)
    # Convertir en JSON string pour le chargement dans la table de staging VARCHAR
    df['EVENT_CONTENT'] = df['EVENT_CONTENT'].apply(lambda x: json.dumps(x) if not isinstance(x, str) else x)
    df['EVENT_METADATA'] = df['EVENT_METADATA'].apply(lambda x: json.dumps(x) if not isinstance(x, str) else x)

    # Nom de la table de staging temporaire (VARCHAR columns)
    # Utiliser un nom en minuscules pour éviter les problèmes de casse
    # signalés par pandas.to_sql sur certains dialectes (voir warning).
    STAGING_TABLE = "stg_raw_events_stream"
    full_staging = f"{TARGET_SCHEMA}.{STAGING_TABLE}"

    # Déterminer l'Engine nécessaire pour pandas.to_sql.
    # La fonction accepte soit une Engine, soit une Connection SQLAlchemy.
    if isinstance(conn, Engine):
        engine = conn
        exec_conn = None
    else:
        engine = getattr(conn, 'engine', None)
        exec_conn = conn
    if engine is None:
        raise RuntimeError("La connexion fournie n'expose pas 'engine' nécessaire pour pandas.to_sql")

    # Créer la table de staging si elle n'existe pas (deux colonnes VARCHAR)
    conn.execute(text(f"CREATE TABLE IF NOT EXISTS {full_staging} (EVENT_METADATA_V VARCHAR, EVENT_CONTENT_V VARCHAR);"))

    # Charger les données dans la table de staging (VARCHAR)
    df_stg = df[['EVENT_METADATA', 'EVENT_CONTENT']].rename(columns={
        'EVENT_METADATA': 'EVENT_METADATA_V', 'EVENT_CONTENT': 'EVENT_CONTENT_V'
    })

    # Utiliser l'engine pour to_sql (pandas nécessite une Engine)
    df_stg.to_sql(
        name=STAGING_TABLE,
        con=engine,
        schema=TARGET_SCHEMA,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )

    # Insérer dans la table finale en convertissant les VARCHAR en OBJECT/VARIANT via PARSE_JSON
    insert_sql = text(f"""
        INSERT INTO {TARGET_SCHEMA}.RAW_EVENTS_STREAM (EVENT_METADATA, EVENT_CONTENT)
        SELECT PARSE_JSON(EVENT_METADATA_V), PARSE_JSON(EVENT_CONTENT_V)
        FROM {full_staging};
    """)

    # Exécuter les opérations DDL/DML en utilisant la connexion active si fournie,
    # sinon ouvrir une connexion transactionnelle depuis l'Engine.
    if exec_conn is not None:
        exec_conn.execute(insert_sql)
        exec_conn.execute(text(f"TRUNCATE TABLE {full_staging};"))
    else:
        with engine.begin() as tx_conn:
            tx_conn.execute(insert_sql)
            tx_conn.execute(text(f"TRUNCATE TABLE {full_staging};"))

# --- 4. BOUCLE PRINCIPALE DU CONSOMMATEUR (PRÊTE POUR LA PRODUCTION) ---

# Variable globale pour gérer l'arrêt propre
running = True

def handle_shutdown(signum, frame):
    """Permet un arrêt propre sur SIGINT (Ctrl+C) ou SIGTERM."""
    global running
    logging.warning("Signal d'arrêt reçu. Fin du traitement du lot en cours...")
    running = False

def main():
    """Point d'entrée principal du consommateur."""
    global running
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Connexions aux services
    snowflake_engine = create_engine(URL(**{
        "user": SNOWFLAKE_USER, "password": SNOWFLAKE_PASSWORD, "account": SNOWFLAKE_ACCOUNT,
        "database": SNOWFLAKE_DATABASE, "warehouse": SNOWFLAKE_WAREHOUSE, "schema": TARGET_SCHEMA
    }))
    setup_snowflake_schema(snowflake_engine)

    # Le producteur est utilisé uniquement pour la Dead-Letter Queue (DLQ)
    dlq_producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVER,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id='snowflake-ingestion-group-v1', # Utiliser un group_id est une bonne pratique
        value_deserializer=lambda x: x.decode('utf-8') # Décoder en string, le JSON est géré après
    )

    logging.info(f"Consumer démarré. Écoute du topic '{TOPIC_NAME}'.")

    batch = []
    last_commit = time.time()
    BATCH_SIZE = 100
    COMMIT_INTERVAL_SECONDS = 10

    try:
        while running:
            # poll() avec un timeout permet de ne pas bloquer indéfiniment
            messages = consumer.poll(timeout_ms=1000, max_records=BATCH_SIZE)
            
            if not messages:
                # Si aucun message, vérifier si on doit commiter le lot en cours à cause du temps écoulé
                if batch and (time.time() - last_commit > COMMIT_INTERVAL_SECONDS):
                    pass # Le commit se fera plus bas
                else:
                    continue

            for topic_partition, msgs in messages.items():
                for msg in msgs:
                    try:
                        event_content = json.loads(msg.value)
                        event_metadata = {
                            "topic": msg.topic, "partition": msg.partition,
                            "offset": msg.offset, "timestamp_ms": msg.timestamp
                        }
                        batch.append({
                            "EVENT_METADATA": event_metadata,
                            "EVENT_CONTENT": event_content
                        })
                    except json.JSONDecodeError:
                        logging.error(f"Erreur de décodage JSON pour le message à l'offset {msg.offset}. Envoi vers la DLQ.")
                        dlq_producer.send(DLQ_TOPIC_NAME, value={"raw_message": msg.value, "error": "JSONDecodeError"})
                        continue
            
            # Condition de commit : taille du lot ou intervalle de temps atteint
            if batch and (len(batch) >= BATCH_SIZE or time.time() - last_commit > COMMIT_INTERVAL_SECONDS):
                with snowflake_engine.connect() as conn:
                    transaction = conn.begin()
                    try:
                        ingest_raw_events_batch(conn, batch)
                        transaction.commit()
                        consumer.commit()
                        logging.info(f"Lot de {len(batch)} événements ingéré avec succès.")
                        batch = []
                        last_commit = time.time()
                    except SQLAlchemyError as e:
                        logging.error(f"Erreur de base de données. Annulation de la transaction. {e}")
                        transaction.rollback()
                        # Ne pas commiter l'offset Kafka pour que les messages soient retraités
    
    finally:
        logging.info("Arrêt du consommateur. Fermeture des connexions.")
        consumer.close()
        dlq_producer.close()
        snowflake_engine.dispose()

if __name__ == "__main__":
    main()