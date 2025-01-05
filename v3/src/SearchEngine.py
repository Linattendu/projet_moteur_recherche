# SearchEngine.py
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from scipy.linalg import norm
import os
import pickle

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

    def __init__(self, corpus):
        """
        @brief Initialise le moteur de recherche avec un corpus.
        @param corpus Instance de la classe Corpus.
        """
        self.corpus = corpus
        self.matrice = MatriceDocuments(corpus)

        # Chemins de sauvegarde spécifiques au thème
        self.tf_pickle_path = DATA_DIR+f"/matrice_TF_{corpus.nom_corpus}.pkl"
        self.tfidf_pickle_path = DATA_DIR+f"/matrice_TFxIDF_{corpus.nom_corpus}.pkl"

        # Charger ou construire les matrices
        self.matrice.mat_TF, self.matrice.mat_TFxIDF = self.charger_ou_construire_matrices()
        
       
    # ========================================
    # 🔄 CHARGER OU CONSTRUIRE LES MATRICES
    # ========================================
    def charger_ou_construire_matrices(self):
        """
        @brief Charge les matrices TF et TFxIDF à partir de fichiers Pickle ou les reconstruit si nécessaire.
        """
        # Vérifier si les matrices existent
        if os.path.exists(self.tf_pickle_path) and os.path.exists(self.tfidf_pickle_path):
            with open(self.tf_pickle_path, 'rb') as f:
                tf = pickle.load(f)
            with open(self.tfidf_pickle_path, 'rb') as f:
                tfidf = pickle.load(f)
            print(f"📂 Matrices TF et TFxIDF chargées pour le corpus : {self.corpus.nom_corpus}")
            return tf, tfidf

        # Sinon, reconstruire et sauvegarder
        print(f"🔧 Construction des matrices TF et TFxIDF pour le corpus : {self.corpus.nom_corpus}...")
        tf = self.matrice.construire_vocab_et_matrice_TF()
        tfidf = self.matrice.construire_matrice_TFxIDF()

        with open(self.tf_pickle_path, 'wb') as f:
            pickle.dump(tf, f)
        with open(self.tfidf_pickle_path, 'wb') as f:
            pickle.dump(tfidf, f)

        print(f"💾 Matrices sauvegardées pour le corpus : {self.corpus.nom_corpus}")
        return tf, tfidf

    # ========================================
    # 🔍 RECHERCHE PAR MOTS-CLÉS
    # ========================================
    def search(self, mots_cles, n_resultats=20, auteur=None, date_debut=None, date_fin=None):
        """
        Recherche de documents avec gestion des expressions exactes et filtrage.
        """
        if self.matrice.mat_TFxIDF is None:
            raise ValueError("La matrice TFxIDF n'a pas été construite.")
            
        # Découper les mots-clés (gestion des expressions complexes)
        mots_cles_split = mots_cles.lower().split()
        
        # Vérification rapide avec vocabulaire pour chaque mot (évite des calculs inutiles)
        mots_non_trouves = [mot for mot in mots_cles_split if mot not in self.matrice.vocab]
        
        if mots_non_trouves:
            print(f"⚠️ Les mots suivants n'existent pas dans le vocabulaire : {', '.join(mots_non_trouves)}")
            return pd.DataFrame(columns=["Titre", "Extrait", "URL", "Score"])  # DataFrame vide
        
        # Créer un vecteur de la requête
        vecteur_requete = self.matrice.vecteur_aligne_matrice(mots_cles)

        # Calcul des scores par produit matriciel
        scores = self.matrice.mat_TFxIDF.dot(vecteur_requete)

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
