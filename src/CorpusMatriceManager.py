#CorpusMatriceManager
import os
import pickle
import sqlite3
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

themes_reddit_arxiv = [
            "politics",         # politique
            "technology",       # technologie
            "health",           # sante
            "education",        # education
            "climate change",   # climat
            "science",          # Sciences
                ]
theme_csv = "discours"

class CorpusMatriceManager:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.creer_table()

    def creer_table(self):
        """
        Crée la table corpus si elle n'existe pas.
        """
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS corpus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_corpus TEXT,
            theme TEXT,
            date_creation TEXT,
            chemin_corpus TEXT,
            chemin_TF TEXT,
            chemin_TFIDF TEXT,
            chemin_vocab TEXT,
            chemin_frequence TEXT
        )
        ''')
        self.conn.commit()


    # CREATION CORPUS DISCOURS (CSV)
    def creer_corpus_discours(self):
                
        source = "csv"
        nom_corpus = source + theme_csv
        nom_fichier_corpus = f"corpus_{nom_corpus}"
        
        print("Conversion du fichier CSV en corpus de discours...")

        if not os.path.exists(CSV_DISCOURS_PATH):
            print("🚨 Fichier CSV non trouvé !")
            return

        df = pd.read_csv(CSV_DISCOURS_PATH, sep='\t')
        
        # Conversion de la colonne 'date' au format datetime
        df['date'] = pd.to_datetime(df['date'], format='%B %d, %Y')
        
        corpus = CorpusSingleton(nom_corpus, theme_csv)

        for i, row in tqdm(df.iterrows(), total=df.shape[0]):
            phrases = Utils.decouper_en_phrases(row['text'])
            for phrase in phrases:                
                if len(phrase.split()) > 20:
                    doc = Document(
                        titre=row['descr'],
                        auteur=row['speaker'],
                        date=row['date'],
                        url=row['link'],
                        texte=phrase.strip(),
                        theme=theme_csv
                    )
                    corpus.ajouter_document(doc)

        self._sauvegarder_pkl(corpus, nom_fichier_corpus)
        self._construire_matrices(nom_corpus)
        print("Corpus de discours sauvegardé et matrices construites")  
                           
    # CREATION CORPUS REDDIT/ARXIV (SCRAPER)
    def creer_corpus_reddit_arxiv(self):
        
        for theme in tqdm(themes_reddit_arxiv, total=len(themes_reddit_arxiv)):
        
            source = "RedditArxiv"
            theme = theme.replace(" ","")
            nom_corpus = source + theme
            nom_fichier_corpus = f"corpus_{nom_corpus}"
            erreur = GestionErreurs(log_file="app_errors.log")   
            
            print("theme creer_corpus_reddit_arxiv : ", theme)     
            
            corpus = CorpusSingleton(nom_corpus, theme)

            reddit_scraper = RedditScrap(corpus, erreur)
            reddit_scraper.recuperer_posts(theme, limit=50)
            arxiv_scraper = ArxivScrap(corpus, erreur)
            arxiv_scraper.recuperer_articles(theme, max_results=50)

            self._sauvegarder_pkl(corpus, nom_fichier_corpus)
            self._construire_matrices(nom_corpus)
            print(f"corpus {nom_corpus} sauvegardé et matrices construites.")
     

    # CONSTRUCTION DES MATRICES TF / TFxIDF
    def _construire_matrices(self, nom_corpus):
        chemin_corpus = os.path.join(DATA_DIR_PKL, f"corpus_{nom_corpus}.pkl")
        chemin_TF = os.path.join(DATA_DIR_PKL, f"matriceTF_{nom_corpus}.pkl")
        chemin_TFxIDF = os.path.join(DATA_DIR_PKL, f"matriceTFIDF_{nom_corpus}.pkl")
        chemin_vocab = os.path.join(DATA_DIR_PKL, f"vocab_{nom_corpus}.pkl")
        chemin_frequence = os.path.join(DATA_DIR_PKL, f"frequenceMots_{nom_corpus}.pkl")
        
        if os.path.exists(chemin_corpus):
            print(f"Chargement du corpus existant : {nom_corpus}")
            corpus = CorpusSingleton(nom_corpus).load(chemin_corpus)
        else:
            print(f"Corpus introuvable : {chemin_corpus}")
            return

        matrice = MatriceDocuments(corpus)
        
        pickle.dump(matrice.mat_TF, open(chemin_TF, 'wb'))
        pickle.dump(matrice.mat_TFxIDF, open(chemin_TFxIDF, 'wb'))
        pickle.dump(matrice.vocab, open(chemin_vocab, 'wb'))
        pickle.dump(matrice.frequence_mot, open(chemin_frequence, 'wb'))
                
        print(f"Matrices TF, TFxIDF , vocab et frequenceMots sauvegardées pour : {nom_corpus}")
    
    # SAUVEGARDE PKL
    def _sauvegarder_pkl(self, fichier, nom_fichier):
        chemin = os.path.join(DATA_DIR_PKL, f"{nom_fichier}.pkl")
        with open(chemin, 'wb') as f:
            pickle.dump(fichier, f)
        print(f"Sauvegarde PKL : {chemin}")

  
    def stocker_en_base_de_donnees(self):
        """
        Parcourt les fichiers PKL et stocke les corpus et matrices dans la base de données.
        """

        fichiers_pkl = os.listdir(DATA_DIR_PKL)

        # Étape 1 : Insérer d'abord tous les corpus
        for fichier in fichiers_pkl:
            if fichier.endswith(".pkl") and fichier.startswith("corpus"):
                #chemin_fichier = os.path.join(DATA_DIR_PKL, fichier)
                nom_corpus = "_".join(fichier.split("_")[1:]).replace(".pkl", "")

                # Définir le thème
                if nom_corpus.startswith("csv"):
                    theme = nom_corpus.split("csv")[1]
                elif nom_corpus.startswith("RedditArxiv"):
                    theme = nom_corpus.split("RedditArxiv")[1]
                else:
                    theme = "inconnu"
                
                chemin_corpus = os.path.join(DATA_DIR_PKL, f"corpus_{nom_corpus}.pkl")
                chemin_TF = os.path.join(DATA_DIR_PKL, f"matriceTF_{nom_corpus}.pkl")
                chemin_TFxIDF = os.path.join(DATA_DIR_PKL, f"matriceTFIDF_{nom_corpus}.pkl")
                chemin_vocab = os.path.join(DATA_DIR_PKL, f"vocab_{nom_corpus}.pkl")
                chemin_frequence = os.path.join(DATA_DIR_PKL, f"frequenceMots_{nom_corpus}.pkl")
                theme = "discours" if "csv" in nom_corpus else nom_corpus.replace("RedditArxiv", "")
                
                # Lire le fichier PKL
                """ with open(chemin_fichier, 'rb') as f:
                    contenu_pkl = f.read() """

                # Insérer le corpus dans la base
                self.cursor.execute('''
                INSERT OR REPLACE INTO corpus (
                    nom_corpus, 
                    theme, 
                    date_creation, 
                    chemin_corpus, 
                    chemin_TF, 
                    chemin_TFIDF, 
                    chemin_vocab, 
                    chemin_frequence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nom_corpus, theme, datetime.now(), chemin_corpus, chemin_TF, chemin_TFxIDF, chemin_vocab, chemin_frequence))

                 #self.conn.commit()
                print(f"Corpus inséré : {nom_corpus}")

                # Étape 2 : Insérer les matrices et vocab
                """ for fichier in fichiers_pkl:
            if fichier.endswith(".pkl") and not fichier.startswith("corpus"):
                chemin_fichier = os.path.join(DATA_DIR_PKL, fichier)
                
                # Déterminer le type de fichier
                if fichier.startswith("matriceTFIDF"):
                    type_fichier = "TFxIDF"
                elif fichier.startswith("matriceTF"):
                    type_fichier = "TF"
                elif fichier.startswith("vocab"):
                    type_fichier = "vocab"
                elif fichier.startswith("frequenceMots"):
                    type_fichier = "frequence"
                else:
                    continue

                nom_corpus = "_".join(fichier.split("_")[1:]).replace(".pkl", "")

                # Lire le fichier PKL
                with open(chemin_fichier, 'rb') as f:
                    contenu_pkl = f.read()

                # Vérifier si le corpus existe
                self.cursor.execute('''
                SELECT * FROM corpus WHERE nom_corpus = ?
                ''', (nom_corpus,))
                existe = self.cursor.fetchone()

                # Mettre à jour les matrices ou vocab si le corpus existe déjà
                if existe:
                    if type_fichier == "TF":
                        self.cursor.execute('''
                        UPDATE corpus SET matrice_TF_pkl = ? WHERE nom_corpus = ?
                        ''', (contenu_pkl, nom_corpus))
                        print(f"TF mis à jour pour : {nom_corpus}")

                    elif type_fichier == "TFxIDF":
                        self.cursor.execute('''
                        UPDATE corpus SET matrice_TFxIDF_pkl = ? WHERE nom_corpus = ?
                        ''', (contenu_pkl, nom_corpus))
                        print(f"TFxIDF mis à jour pour : {nom_corpus}")

                    elif type_fichier == "vocab":
                        self.cursor.execute('''
                        UPDATE corpus SET vocab_pkl = ? WHERE nom_corpus = ?
                        ''', (contenu_pkl, nom_corpus))
                        print(f"Vocab mis à jour pour : {nom_corpus}")
                    
                    elif type_fichier == "frequence":
                        self.cursor.execute('''
                        UPDATE corpus SET frequence_mots_pkl = ? WHERE nom_corpus = ?
                        ''', (contenu_pkl, nom_corpus))
                        print(f"Frequence mots mis à jour pour : {nom_corpus}") """

        self.conn.commit()

    def fermer_connexion(self):
        self.conn.close()