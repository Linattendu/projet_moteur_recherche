import os
from dotenv import load_dotenv
from src.CorpusSingleton import CorpusSingleton
from src.RecuperationDocs import RedditScrap, ArxivScrap
from src.GestionErreurs import GestionErreurs
from src.constantes import *
"""
@file rev1.py
@brief Point d'entrée principal du moteur de recherche documentaire.

@details
Ce fichier orchestre l'exécution du scraping Reddit et Arxiv afin de constituer un corpus de documents.

Classes et Modules Utilisés :
- CorpusSingleton : Gestion du corpus unique de documents (pattern Singleton).
- RedditScrap : Scraping de la plateforme Reddit pour récupérer des posts.
- ArxivScrap : Scraping de la plateforme Arxiv pour récupérer des articles scientifiques.
- GestionErreurs : Gestion centralisée des erreurs et écriture dans un fichier log.

Exécution :
    python rev1.py

Sortie :
- Affiche la taille du corpus final et les documents extraits depuis Reddit et Arxiv.
- Les erreurs rencontrées sont loggées dans "app_errors.log".
"""

if __name__ == "__main__":
    """
    @brief Point d'entrée de l'application.

    @details
    Ce bloc initialise les composants principaux de l'application :
    - Initialisation de la gestion des erreurs.
    - Scraping de Reddit et Arxiv.
    - Affichage du corpus final.
    """
    
    # Charger les variables d'environnement
    load_dotenv()
    print("load_dotenv() : ",REDDIT_CLIENT_ID)  # Affiche la valeur de .env
    
    erreur = GestionErreurs(log_file="app_errors.log")
    
    theme = 'climate change'
    # Chemin de sauvegarde dans le dossier 'data'
    dossier_data = "../data"
    theme_sans_espace= theme.replace(" ", "")
    nom_corpus = f"corpus_{theme_sans_espace}"
    nom_fichier = nom_corpus + ".pkl"
    chemin_sauvegarde = os.path.join(dossier_data, nom_fichier)
    print(f" {nom_corpus} {nom_fichier} {chemin_sauvegarde}")
    
    corpus = CorpusSingleton(nom_corpus=nom_corpus)

    # Créer le dossier 'data' s'il n'existe pas
    if not os.path.exists(dossier_data):
        os.makedirs(dossier_data)
    
    # Charger ou créer un nouveau corpus
    if os.path.exists(chemin_sauvegarde):
        print("📂 Chargement du corpus existant...")
        corpus = corpus.load(chemin_sauvegarde)
    else:
        print("📁 Aucune sauvegarde n'est trouvée, téléchargement à nouveau")
                
        # Scraping Reddit et Arxiv
        erreur = GestionErreurs(log_file="app_errors.log")
        reddit_scraper = RedditScrap(corpus, erreur)
        reddit_scraper.recuperer_posts(theme, limit=10)

        arxiv_scraper = ArxivScrap(corpus, erreur)
        arxiv_scraper.recuperer_articles(theme, max_results=10)

        # Sauvegarder le corpus
        corpus.save(chemin_sauvegarde)
        print(f"💾 Corpus sauvegardé dans {chemin_sauvegarde}")
        
    
    # Afficher les documents récupérés
    print(f"Taille du corpus : {len(corpus.id2doc)} documents")
    for doc in corpus.id2doc:
        print(doc)

    