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
"""
@var LOCAL_URL
@brief URL locale pour l'application.
@details Peut être utilisée pour tester des fonctionnalités locales.
"""

CSV_DISCOURS_PATH = "./data_discours/discours_US.csv"
"""
@var CSV_DISCOURS_PATH
@brief Chemin du fichier CSV contenant les discours.
"""

CSV_DISCOURS_CLASSIFIE_PATH = "./discours_classifie"
"""
@var CSV_DISCOURS_CLASSIFIE_PATH
@brief Chemin du dossier pour les discours classifiés.
"""

DATA_DIR_PKL=  "./DataPkl"   
"""
@var DATA_DIR_PKL
@brief Chemin du dossier contenant les fichiers pickle.
"""

DB_PATH = "./db/corpus_matrix.sqlite"
"""
@var DB_PATH
@brief Chemin de la base de données SQLite utilisée par l'application.
"""

THEMESCORPUS = {
            "politics": ["RedditArxivpolitics", "csvdiscours"],
            "technology": ["RedditArxivtechnology", "csvtechnology"],
            "education": ["RedditArxiveducation", "csveducation"],
            "climatechange": ["RedditArxivclimatechange", "csvclimatechange"],
            "science": ["RedditArxivscience", "csvscience"],
            "health": ["RedditArxivhealth", "csvhealth"]
        }
"""
@var THEMESCORPUS
@brief Dictionnaire des thèmes disponibles dans l'application.
@details Chaque thème est associé à deux listes : une pour Reddit/Arxiv et une pour les sources CSV.
"""