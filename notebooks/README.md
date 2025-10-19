# 📓 Jupyter Notebooks

Educational and exploratory notebooks for **Les Caves d'Albert** project.

## 📁 Files

```
notebooks/
└── Git_Basics.ipynb    # Git fundamentals and workflow
```

## 📖 Available Notebooks

### `Git_Basics.ipynb`
Introduction to Git version control basics:
- Git configuration
- Basic commands (add, commit, push, pull)
- Branching and merging
- Working with remote repositories

**Usage:**
```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
jupyter notebook

# Open Git_Basics.ipynb
```

## 🚀 Running Notebooks

### Local Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install jupyter pandas matplotlib snowflake-connector-python

# Launch Jupyter
jupyter notebook
```

### VS Code

1. Install **Jupyter extension** for VS Code
2. Open notebook file (`.ipynb`)
3. Click **Select Kernel** → Choose Python interpreter
4. Run cells with `Shift + Enter`

## 📝 Adding New Notebooks

When creating new notebooks, consider:

1. **Clear documentation** - Add markdown cells explaining each step
2. **Cell organization** - Group related code logically
3. **Output examples** - Include sample outputs
4. **Requirements** - Document required packages

### Template Structure

```python
# Cell 1: Title and Description
"""
# Notebook Title
Description of what this notebook does
Author: Your Name
Date: YYYY-MM-DD
"""

# Cell 2: Imports
import pandas as pd
import snowflake.connector

# Cell 3: Configuration
# Configuration and constants

# Cell 4+: Analysis
# Your analysis code
```

## 🔗 Useful Resources

- [Jupyter Documentation](https://jupyter.org/documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Snowflake Python Connector](https://docs.snowflake.com/en/user-guide/python-connector)

---

**🍷 Les Caves d'Albert** - Jupyter Notebooks
