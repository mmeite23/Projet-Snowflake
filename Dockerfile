# Dockerfile (Version améliorée)

# --- ÉTAPE 1: "Builder" ---
# On utilise une image complète pour construire nos dépendances.
FROM python:3.10-slim as builder
WORKDIR /app

# On copie uniquement ce qui est nécessaire pour installer les dépendences.
COPY requirements.txt .

# Installer des paquets système utiles pour compiler certaines dépendances Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libbz2-dev \
    liblzma-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer une version de numpy compatible (<2) puis pandas et pyarrow avant
# d'installer le reste des dépendances. Cela évite les erreurs de compatibilité
# binaire lors de l'installation des roues précompilées.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "numpy<2" pandas==2.1.1 pyarrow==14.0.1 && \
    pip install --no-cache-dir -r requirements.txt

# On copie le reste du code source.
COPY . .

# --- ÉTAPE 2: "Final" ---
# On repart d'une image propre et légère.
FROM python:3.10-slim

# On crée un utilisateur non-root pour la sécurité.
RUN addgroup --system app && adduser --system --group app
WORKDIR /app

# Copier le code source
COPY . /app

# Copier les packages Python et binaires installés dans l'étape builder
# Cela évite de réinstaller les paquets compilés dans la couche finale et
# prévient les problèmes de compatibilité binaire entre numpy/pandas/pyarrow.
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Donner la propriété des fichiers à notre utilisateur non-root.
RUN chown -R app:app /app /usr/local/lib/python3.10/site-packages /usr/local/bin || true

# Changer d'utilisateur. Le conteneur ne tournera plus en root.
USER app

# La commande sera définie dans docker-compose.yml