import os
from dotenv import load_dotenv
from src.CorpusSingleton import CorpusSingleton
from src.RecuperationDocs import RedditScrap, ArxivScrap
from src.GestionErreurs import GestionErreurs
from src.SearchEngine import SearchEngine
from src.constantes import * 
import pandas as pd
from src.constantes import *

"""
@file Verifier_moteur_recherche.py
@brief Point d'entrée principal pour la version 2 du moteur de recherche.

@details
Cette version introduit la création d'une matrice TFxIDF et la recherche de documents par similarité cosinus.

Classes et Modules Utilisés :
- CorpusSingleton : Gestion du corpus unique de documents (pattern Singleton).
- RedditScrap : Scraping de Reddit.
- ArxivScrap : Scraping d'Arxiv.
- SearchEngine : Construction de la matrice TFxIDF et recherche par mots-clés.
- GestionErreurs : Gestion des erreurs.

Exécution :
    python -m src.Verifier_moteur_recherche

Sortie :
- Affiche les résultats de la recherche à partir d'une requête.
"""

if __name__ == "__main__":
    """
    @brief Point d'entrée de l'application version 2.

    @details
    Cette version met en place le scraping suivi de la recherche par mots-clés 
    avec le moteur de recherche basé sur TFxIDF.
    """
    
    # Charger les variables d'environnement (Reddit API)
    load_dotenv()

    erreur = GestionErreurs(log_file="app_errors.log")
    
    theme = 'medicine'
    theme_sans_espace= theme.replace(" ", "")
    nom_corpus = f"corpus_{theme_sans_espace}"
    nom_fichier = nom_corpus + ".pkl"
    chemin_sauvegarde = os.path.join(DATA_DIR, nom_fichier)
    
    corpus = CorpusSingleton(nom_corpus)
    
    # Créer le dossier 'data_v2' s'il n'existe pas
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Charger ou créer un nouveau corpus
    if os.path.exists(chemin_sauvegarde):
        print("📂 Chargement du corpus existant...")
        corpus = corpus.load(chemin_sauvegarde)
    else:
        print("📁 Aucune sauvegarde n'est trouvée, téléchargement à nouveau")
                
        # Scraping Reddit et Arxiv
        erreur = GestionErreurs(log_file="app_errors.log")
        reddit_scraper = RedditScrap(corpus, erreur)
        reddit_scraper.recuperer_posts(theme, limit=30)

        arxiv_scraper = ArxivScrap(corpus, erreur)
        arxiv_scraper.recuperer_articles(theme, max_results=30)

        # Sauvegarder le corpus
        corpus.save(chemin_sauvegarde)
        print(f"💾 Corpus sauvegardé dans {chemin_sauvegarde}")
    
    # Construire le moteur de recherche
    moteur = SearchEngine(corpus)

    # Construire la matrice TFxIDF
    moteur.matrice.construire_vocab_et_matrice_TF()
    moteur.matrice.construire_matrice_TFxIDF()

    # Effectuer une recherche
    #requete = "patients"
    requete = "disease"
    resultats = moteur.search(requete, n_resultats=10)

    # Afficher les résultats
    print(f"\nRésultats de la recherche pour la requête : '{requete}'")
    print(resultats)    
    
    
    
    
    
