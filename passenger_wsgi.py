import sys
import os

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(__file__))

# Importa l'applicazione Flask
from src.main import app

# Configura l'applicazione per il deployment
application = app

if __name__ == "__main__":
    application.run()

