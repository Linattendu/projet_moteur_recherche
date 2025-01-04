import os
import pickle
import pandas as pd
from src.CorpusSingleton import CorpusSingleton
from src.MatriceDocuments import MatriceDocuments
from src.RecuperationDocs import RedditScrap, ArxivScrap
from src.GestionErreurs import GestionErreurs
from dotenv import load_dotenv
from tqdm import tqdm
from src.Utils import Utils
from src.Document import Document
from datetime import datetime
from src.constantes import *



load_dotenv()


class CorpusMatrixManager1:
    """
    @brief Gère la création d'un corpus et la construction des matrices associées.

    Cette classe permet de créer un corpus à partir de données Reddit et ArXiv, 
    de construire les matrices TF et TFxIDF, et de sauvegarder les résultats au format PKL.
    """
    def __init__(self):
        """
        @brief Initialise une instance de CorpusMatrixManager1.
        """
        pass
        

    # Creation corpus REDDIT/ARXIV (SCRAPER)
    def creer_corpus_reddit_arxiv(self, theme):
        """
        @brief Crée un corpus à partir des données de Reddit et ArXiv.

        @param theme Le thème de recherche pour récupérer les données.
        
        @details Cette fonction utilise des scrapers pour récupérer des articles depuis Reddit et ArXiv 
                 basés sur un thème donné. Le corpus est ensuite sauvegardé et les matrices TF/TFxIDF sont construites.
        """      
       
        source = "RedditArxiv"
        theme = theme.replace(" ","")
        nom_corpus = source + theme
        nom_fichier_corpus = f"corpus_{nom_corpus}"
        erreur = GestionErreurs(log_file="app_errors.log")   
        
        print("theme creer_corpus_reddit_arxiv : ", theme)     
        
        corpus = CorpusSingleton(nom_corpus, theme)

        reddit_scraper = RedditScrap(corpus, erreur)
        reddit_scraper.recuperer_posts(theme, limit=10)
        arxiv_scraper = ArxivScrap(corpus, erreur)
        arxiv_scraper.recuperer_articles(theme, max_results=10)

        self._sauvegarder_pkl(corpus, nom_fichier_corpus)
        self._construire_matrices(nom_corpus)
        print(f"corpus {nom_corpus} sauvegardé et matrices construites.")
     

    # Construction des matrices TF / TFxIDF
    def _construire_matrices(self, nom_corpus):
        """
        @brief Construit les matrices TF et TFxIDF pour un corpus donné.

        @param nom_corpus Le nom du corpus pour lequel les matrices doivent être construites.

        @details Charge le corpus depuis le disque, construit les matrices TF et TFxIDF, 
                 puis sauvegarde ces matrices dans des fichiers PKL.
        """
        chemin_corpus = os.path.join(DATA_DIR, f"corpus_{nom_corpus}.pkl")
        chemin_TF = os.path.join(DATA_DIR, f"matriceTF_{nom_corpus}.pkl")
        chemin_TFxIDF = os.path.join(DATA_DIR, f"matriceTFIDF_{nom_corpus}.pkl")
        chemin_VOCAB = os.path.join(DATA_DIR, f"vocab_{nom_corpus}.pkl")
        
        if os.path.exists(chemin_corpus):
            print(f"Chargement du corpus existant : {nom_corpus}")
            corpus = CorpusSingleton(nom_corpus).load(chemin_corpus)
        else:
            print(f"Corpus introuvable : {chemin_corpus}")
            return

        matrice = MatriceDocuments(corpus)

        print(f"Construction de la matrice TF pour : {nom_corpus}")
        matrice_TF = matrice.construire_vocab_et_matrice_TF()
        print(f"Taille de la matrice TF : {matrice_TF.shape}")

        print(f"Construction de la matrice TFxIDF pour : {nom_corpus}")
        matrice_TFxIDF = matrice.construire_matrice_TFxIDF()
        print(f"Taille de la matrice TFxIDF : {matrice_TFxIDF.shape}")

        with open(chemin_TF, 'wb') as f:
            pickle.dump(matrice_TF, f)
        with open(chemin_TFxIDF, 'wb') as f:
            pickle.dump(matrice_TFxIDF, f)

        print(f"Matrices TF et TFxIDF sauvegardées pour : {nom_corpus}")
    

    # Sauvegarde PKL
    def _sauvegarder_pkl(self, objet, nom_fichier):
        """
        @brief Sauvegarde un objet Python au format PKL.

        @param objet L'objet à sauvegarder.
        @param nom_fichier Le nom du fichier dans lequel sauvegarder l'objet.

        @details Cette méthode sérialise un objet Python et le sauvegarde sur le disque
                 dans le répertoire défini par `DATA_DIR`.
        """
        chemin = os.path.join(DATA_DIR, f"{nom_fichier}.pkl")
        with open(chemin, 'wb') as f:
            pickle.dump(objet, f)
        print(f"Sauvegarde PKL : {chemin}")

  
   