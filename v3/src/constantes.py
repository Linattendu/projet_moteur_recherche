import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

"""
@file constantes.py
@brief Définition des constantes utilisées dans l'application.

@details
Ce fichier charge les constantes nécessaires à partir des variables d'environnement. 
Cela permet de protéger les informations sensibles comme les identifiants et les clés secrètes.
"""

# Constantes pour l'API Reddit
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', 'default_client_id')
"""
@var REDDIT_CLIENT_ID
Identifiant client pour l'API Reddit, chargé à partir des variables d'environnement.
"""
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', 'default_client_secret')
"""
@var REDDIT_CLIENT_SECRET
Clé secrète pour l'API Reddit, chargée à partir des variables d'environnement.
"""
USER_AGENT = os.getenv('USER_AGENT', 'Moteur de recherche:v1.0 (par /u/nom_utilisateur)')
"""
@var USER_AGENT
Agent utilisateur pour l'interaction avec l'API Reddit.
"""

# URL de l'API Arxiv (pas sensible, mais centralisé)
URL_ARXIV = 'http://export.arxiv.org/api/query?'
"""
@var URL_ARXIV
URL de base pour interroger l'API Arxiv.
"""

LOCAL_URL = "https://localhost:8080" 

# ARXIV
URL_ARXIV = "http://export.arxiv.org/api/query?"
"""
@var URL_ARXIV
URL de base pour interroger l'API Arxiv.
"""

CSV_DISCOURS_PATH = "../data/discours_US.csv"

DATA_DIR =  "../DataPkl_test"   # cas de interface_basique.py
# DATA_DIR = "../DataPkl" cas de interface_finale.py (ou interface.py)
