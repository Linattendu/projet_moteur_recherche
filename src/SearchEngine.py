# SearchEngine.py
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from scipy.linalg import norm
import os
import pickle
import sqlite3
from collections import defaultdict

from src.Corpus import Corpus
from src.MatriceDocuments import MatriceDocuments
from src.Utils import Utils
from datetime import datetime
from src.constantes import *


#pd.set_option('display.max_colwidth', None)


class SearchEngine:
    """
    @brief Moteur de recherche utilisant des matrices TF et TFxIDF pour effectuer des recherches par mots-clés.
    """

    def __init__(self, nom_corpus):
        """
        @brief Initialise le moteur de recherche avec un corpus.
        @param corpus Instance de la classe Corpus.
        """
        self.corpus = None
        self.mat_TF = None
        self.mat_TFxIDF = None
        self.vocab = {}
        self.frequence_mot = defaultdict(int)
        
        # Chargement automatique des matrices et vocab
        self._charger_matrices_depuis_db(nom_corpus)
        
        
    # TRANSFORMATION DE REQUÊTE EN VECTEUR
    def vecteur_aligne_matrice(self, mots_cles):
        """
        Transforme une requête utilisateur en vecteur aligné avec la matrice TFxIDF.
        """
        #print("frequence mot vecteur : ",self.frequence_mot )
        vecteur_requete = np.zeros(len(self.vocab))
        mots = mots_cles.lower().split()

        for mot in mots:
            if mot in self.vocab:
                vecteur_requete[self.vocab[mot]['id']] += 1
            else:
                print(f"Mot absent du vocabulaire : {mot}")
        
        # Appliquer l'IDF pour chaque mot
        for mot in mots:
            if mot in self.vocab:
                idf = np.log((len(self.corpus.id2doc) + 1) / (1 + self.frequence_mot[mot])) + 1
                vecteur_requete[self.vocab[mot]['id']] *= idf

        return vecteur_requete


    # RECHERCHE PAR MOTS-CLÉS  
    def search(self, mots_cles, n_resultats=20, auteur=None, date_debut=None, date_fin=None):
        """
        Recherche de documents avec gestion des expressions exactes et filtrage.
        """
        if self.mat_TFxIDF is None:
            raise ValueError("La matrice TFxIDF n'a pas été construite.")
            
        # Découper les mots-clés (gestion des expressions complexes)
        mots_cles_split = mots_cles.lower().split()
        
        # Vérification rapide avec vocabulaire pour chaque mot (évite des calculs inutiles)
        mots_non_trouves = [mot for mot in mots_cles_split if mot not in self.vocab]
        
        if mots_non_trouves:
            print(f"⚠️ Les mots suivants n'existent pas dans le vocabulaire : {', '.join(mots_non_trouves)}")
            return pd.DataFrame(columns=["Titre", "Extrait", "URL", "Score"])  # DataFrame vide
        
        # Créer un vecteur de la requête
        vecteur_requete = self.vecteur_aligne_matrice(mots_cles)

        if self.mat_TFxIDF .shape[1] != len(self.vocab):
            raise ValueError("La taille du vocabulaire ne correspond pas à la matrice TF-IDF. Veuillez régénérer les matrices.")
        
        # Calcul des scores par produit matriciel
        scores = self.mat_TFxIDF.dot(vecteur_requete)

        # Associer les scores aux documents
        resultats = list(zip(self.corpus.id2doc.values(), scores))
        
        
        # Filtrer les résultats par pertinence (score > 0) ET expression exacte
        # auteur, date
        resultats_filtres = [
        (doc, score) for doc, score in resultats
        if mots_cles.lower() in doc.texte.lower() and 
        score > 0 and
        (not auteur or doc.auteur == auteur) and
        (not date_debut or doc.date >= date_debut) and
        (not date_fin or doc.date <= date_fin) 
        ]

        # Si aucun document n'est trouvé avec l'expression exacte
        if not resultats_filtres:
            print("⚠️ Aucun document trouvé contenant l'expression exacte.")
            return pd.DataFrame(columns=["Titre", "Extrait", "URL", "Score"])  

        # Trier par score décroissant
        resultats_filtres = sorted(resultats_filtres, key=lambda x: x[1], reverse=True)

        # Construire le DataFrame des résultats
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

    # CHARGER OU CONSTRUIRE LES MATRICES
    def _charger_matrices_depuis_db(self,nom_corpus):
        conn = sqlite3.connect("./db/corpus_matrix.sqlite")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT corpus_pkl, matrice_TF_pkl, matrice_TFxIDF_pkl, vocab_pkl, frequence_mots_pkl
            FROM corpus WHERE nom_corpus = ?
        ''', (nom_corpus,))
        result = cursor.fetchone()
        conn.close()

        if result:
            # Vérification si des éléments sont manquants
            if not all(result):
                fichiers_absents = [
                    "corpus" if result[0] is None else "",
                    "matrice TF" if result[1] is None else "",
                    "matrice TF-IDF" if result[2] is None else "",
                    "vocabulaire" if result[3] is None else "",
                    "fréquence mots" if result[4] is None else "",
                ]
                fichiers_absents = [f for f in fichiers_absents if f]
                print(f"⚠️ Fichiers manquants pour {self.corpus.nom_corpus} : {', '.join(fichiers_absents)}")
                #self._construire_matrices_si_absentes()  # Construire si nécessaire
                return
            
            # Chargement des matrices et du vocabulaire
            self.corpus = pickle.loads(result[0])
            self.mat_TF = pickle.loads(result[1])
            self.mat_TFxIDF = pickle.loads(result[2])
            self.vocab = pickle.loads(result[3])
            self.frequence_mot = pickle.loads(result[4])
           
           
            print(f"✅ Corpus '{self.corpus.nom_corpus}' chargé avec succès.")
        else:
            raise ValueError(f"❌ Corpus '{self.corpus.nom_corpus}' introuvable dans la base de données.")
    
