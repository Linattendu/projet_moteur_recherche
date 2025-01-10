import os
import pickle
import sqlite3
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from collections import defaultdict
from src.Corpus import Corpus
from src.Utils import Utils
from datetime import datetime
from src.constantes import *

"""
@file SearchEngine.py
@brief Implémentation d'un moteur de recherche basé sur des matrices TF et TF-IDF.

@details
Ce module permet de rechercher des documents dans un corpus en utilisant des vecteurs de requêtes alignés avec une matrice TF-IDF.
Il prend également en charge le filtrage par auteur et plage de dates, et affiche les résultats triés par pertinence.
"""
class SearchEngine:
    """
    @brief Classe représentant le moteur de recherche.
    """

    def __init__(self, nom_corpus):
        """
        @brief Initialise le moteur de recherche pour un corpus donné.
        @param nom_corpus Nom du corpus à utiliser.
        """
        self.nom_corpus = nom_corpus
        self.corpus = None
        self.mat_TF = None
        self.mat_TFxIDF = None
        self.vocab = {}
        self.frequence_mot = defaultdict(int)

        self._charger_corpus_matrices()

    def _charger_corpus_matrices(self):
        """
        @brief Charge les matrices TF, TF-IDF, le vocabulaire et la fréquence des mots.
        @throws ValueError Si un fichier nécessaire est manquant.
        """
        chemins = self._charger_chemins_depuis_db()

        try:
            with open(chemins["ch_corpus"], 'rb') as f:
                self.corpus = pickle.load(f)            
            with open(chemins["ch_TF"], 'rb') as f:
                self.mat_TF = pickle.load(f)
            with open(chemins["ch_TFIDF"], 'rb') as f:
                self.mat_TFxIDF = pickle.load(f)
            with open(chemins["ch_vocab"], 'rb') as f:
                self.vocab = pickle.load(f)
            with open(chemins["ch_frequence"], 'rb') as f:
                self.frequence_mot = pickle.load(f)
      
            print(f"✅ Matrices et vocabulaire chargés pour le corpus '{self.nom_corpus}'.")

        except FileNotFoundError as e:
            raise ValueError(f"❌ Fichier manquant pour le corpus '{self.nom_corpus}': {e}")

    def _charger_chemins_depuis_db(self):
        """
        @brief Récupère les chemins des fichiers liés au corpus depuis la base de données.
        @return Dictionnaire contenant les chemins des fichiers nécessaires.
        @throws ValueError Si aucun chemin n'est trouvé dans la base de données.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
            chemin_corpus, 
            chemin_TF, 
            chemin_TFIDF, 
            chemin_vocab, 
            chemin_frequence
            FROM corpus WHERE nom_corpus = ?
        ''', (self.nom_corpus,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"❌ Aucun chemin trouvé pour le corpus '{self.nom_corpus}' dans la base de données.")

        return {
            "ch_corpus" : result[0],
            "ch_TF": result[1],
            "ch_TFIDF": result[2],
            "ch_vocab": result[3],
            "ch_frequence": result[4],
            
        }

    def vecteur_aligne_matrice(self, mots_cles):
        """
        @brief Transforme une requête en vecteur aligné avec la matrice TF-IDF.
        @param mots_cles Mots-clés de la requête.
        @return Vecteur de requête aligné avec la matrice TF-IDF.
        """
        vecteur_requete = np.zeros(len(self.vocab))
        mots = mots_cles.lower().split()

        for mot in mots:
            if mot in self.vocab:
                vecteur_requete[self.vocab[mot]['id']] += 1
            else:
                print(f"Mot absent du vocabulaire : {mot}")

        for mot in mots:
            if mot in self.vocab:
                idf = np.log((len(self.corpus.id2doc) + 1) / (1 + self.frequence_mot[mot])) + 1
                vecteur_requete[self.vocab[mot]['id']] *= idf

        return vecteur_requete

    def search(self, mots_cles, n_resultats=20, auteur=None, date_debut=None, date_fin=None):
        """
        @brief Recherche des documents en fonction des mots-clés.
        @param mots_cles Mots-clés à rechercher.
        @param n_resultats Nombre maximum de résultats à retourner.
        @param auteur Filtrer par auteur (optionnel).
        @param date_debut Date de début de la plage (optionnel).
        @param date_fin Date de fin de la plage (optionnel).
        @return DataFrame contenant les résultats triés par pertinence.
        """
        if self.mat_TFxIDF is None:
            raise ValueError("La matrice TF-IDF n'a pas été construite.")

        mots_cles_split = mots_cles.lower().split()
        mots_non_trouves = [mot for mot in mots_cles_split if mot not in self.vocab]

        if mots_non_trouves:
            print(f"⚠️ Les mots suivants n'existent pas dans le vocabulaire : {', '.join(mots_non_trouves)}")
            return pd.DataFrame(columns=["Titre", "Extrait", "URL", "Score"])

        vecteur_requete = self.vecteur_aligne_matrice(mots_cles)

        if self.mat_TFxIDF.shape[1] != len(self.vocab):
            raise ValueError("La taille du vocabulaire ne correspond pas à la matrice TF-IDF. Veuillez régénérer les matrices.")

        scores = self.mat_TFxIDF.dot(vecteur_requete)

        resultats = list(zip(self.corpus.id2doc.values(), scores))
        resultats_filtres = [
            (doc, score) for doc, score in resultats
            if mots_cles.lower() in doc.texte.lower() and \
               score > 0 and \
               (not auteur or doc.auteur == auteur) and \
               (not date_debut or doc.date >= date_debut) and \
               (not date_fin or doc.date <= date_fin)
        ]

        if not resultats_filtres:
            print("⚠️ Aucun document trouvé contenant l'expression exacte.")
            return pd.DataFrame(columns=["Titre", "Extrait", "URL", "Score"])

        resultats_filtres = sorted(resultats_filtres, key=lambda x: x[1], reverse=True)

        df_resultats = pd.DataFrame([
            {
                "Titre": doc.titre,
                "Extrait": Utils.extraire_extrait(doc.texte, mots_cles),
                "URL": doc.url,
                "Auteur": doc.auteur,
                "Date": doc.date,
                "Score": score
            }
            for doc, score in resultats_filtres[:n_resultats]
        ])
        return df_resultats

    def afficher_matrices(self):
        """
        @brief Affiche les matrices TF et TF-IDF pour débogage.
        """
        if self.mat_TF is not None:
            print("Matrice TF :")
            print(self.mat_TF.toarray())
        if self.mat_TFxIDF is not None:
            print("\nMatrice TF-IDF :")
            print(self.mat_TFxIDF.toarray())
