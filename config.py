import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTATS_DIR = os.path.join(BASE_DIR, 'resultats')

# Assurez-vous que ces répertoires existent
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTATS_DIR, exist_ok=True)