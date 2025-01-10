import sqlite3
import os
import pickle
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from src.Corpus import Corpus
from src.Document import Document
from src.constantes import *


class ClassificateurThemesDiscours:
    """
    @class ClassificateurThemesDiscours
    @brief Classe permettant de classer les documents par thèmes en fonction de mots-clés spécifiques.
    """
    def __init__(self):
        """
        @brief Initialise les thèmes et leurs mots-clés associés.
        """
        self.keywords_par_theme = {
            "science": ["research", "experiment", "innovation", "climate", "discovery", "laboratory", "physics"],
            "health": ["hospital", "medicare", "vaccine", "healthcare", "doctor", "nurse", "therapy"],
            "technology": ["AI", "data", "digital", "robotics", "cybersecurity", "software", "hardware"],
            "climatechange": ["carbon", "renewable", "environment", "sustainability", "warming", "greenhouse", "pollution"],
            "education": ["school", "university", "student", "teacher", "curriculum", "learning", "lecture"]
        }

    def charger_corpus_depuis_db(self, nom_corpus):
        """
        @brief Charge les chemins des fichiers pickle associés à un corpus depuis la base de données.
        @param nom_corpus Nom du corpus.
        @return Tuple contenant les chemins du corpus, de la matrice TF-IDF et du vocabulaire.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chemin_corpus, chemin_TFIDF, chemin_vocab
            FROM corpus WHERE nom_corpus = ?
        ''', (nom_corpus,))
        result = cursor.fetchone()
        conn.close()

        if result:
            chemin_corpus, chemin_tfidf, chemin_vocab = result
            return chemin_corpus, chemin_tfidf, chemin_vocab
        else:
            print(f"❌ Corpus {nom_corpus} non trouvé dans la base de données.")
            return None, None, None

    def charger_fichier_pickle(self, chemin):
        """
        @brief Charge un fichier pickle à partir de son chemin.
        @param chemin Chemin du fichier pickle.
        @return Objet désérialisé depuis le fichier pickle.
        """
        with open(chemin, 'rb') as f:
            return pickle.load(f)

    def classifier_document_par_themes(self, doc_index, vocab, tfidf):
        """
        @brief Classe un document donné par thèmes en fonction des scores calculés.
        @param doc_index Index du document dans le corpus.
        @param vocab Vocabulaire contenant les mots-clés et leurs indices.
        @param tfidf Matrice TF-IDF des documents.
        @return Dictionnaire contenant les thèmes et leurs scores associés pour le document.
        """
        if isinstance(tfidf, coo_matrix):
            tfidf = tfidf.tocsr()
        scores_par_theme = {}
        for theme, mots in self.keywords_par_theme.items():
            score = 0
            for mot in mots:
                if mot in vocab:
                    mot_index = vocab[mot]['id']
                    score += tfidf[doc_index, mot_index]
            if score > 0:
                scores_par_theme[theme] = score
        return scores_par_theme

    def creer_sous_corpus(self, corpus, vocab, tfidf):
        """
        @brief Classe les documents d'un corpus par thèmes en fonction des scores calculés.
        @param corpus Corpus contenant les documents.
        @param vocab Vocabulaire contenant les mots-clés et leurs indices.
        @param tfidf Matrice TF-IDF des documents.
        @return Dictionnaire contenant les thèmes et leurs documents associés.
        """
        corpus_themes_dynamiques = {}

        for doc_id, doc in enumerate(corpus.id2doc.values()):
            scores = self.classifier_document_par_themes(doc_id, vocab, tfidf)
            for theme, score in scores.items():
                if theme not in corpus_themes_dynamiques:
                    corpus_themes_dynamiques[theme] = []
                corpus_themes_dynamiques[theme].append((doc, score))

        # Trier les documents par score décroissant pour chaque thème
        for theme in corpus_themes_dynamiques:
            corpus_themes_dynamiques[theme].sort(key=lambda x: x[1], reverse=True)

        return corpus_themes_dynamiques

    def sauvegarder_dans_bdd(self, resultats):
        """
        @brief Sauvegarde les résultats classifiés dans la base de données en incluant les chemins des documents pickle.
        @param resultats Dictionnaire contenant les thèmes et les documents classifiés.
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Créer une table pour stocker les résultats classifiés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS themes_discours (
                theme TEXT,
                chemin_document TEXT,
                score REAL
            )
        ''')

        # Insérer les résultats dans la table
        for theme, docs in resultats.items():
            for doc, score in docs:
                # Sauvegarder chaque document en pickle et enregistrer son chemin
                chemin_document = os.path.join(CSV_DISCOURS_CLASSIFIE_PATH, f"{doc.titre.replace(' ', '_')}.pkl")
                with open(chemin_document, 'wb') as f:
                    pickle.dump(doc, f)

                cursor.execute('''
                    INSERT INTO themes_discours (theme, chemin_document, score)
                    VALUES (?, ?, ?)
                ''', (theme, chemin_document, score))

        conn.commit()
        conn.close()
        print("✅ Résultats sauvegardés dans la base de données avec les chemins des documents.")

    def analyser_csvdiscours(self):
        """
        @brief Analyse le corpus des discours CSV, classe les documents par thèmes, et sauvegarde les résultats dans la base de données.
        """
        chemin_corpus, chemin_tfidf, chemin_vocab = self.charger_corpus_depuis_db("csvdiscours")
        if not chemin_corpus or not chemin_tfidf or not chemin_vocab:
            print("❌ Corpus, TF-IDF ou vocabulaire non disponible.")
            return

        # Charger les données nécessaires
        corpus = self.charger_fichier_pickle(chemin_corpus)
        tfidf = self.charger_fichier_pickle(chemin_tfidf)
        vocab = self.charger_fichier_pickle(chemin_vocab)

        # Créer les sous-corpus classifiés
        sous_corpus = self.creer_sous_corpus(corpus, vocab, tfidf)
        self.sauvegarder_dans_bdd(sous_corpus)

if __name__ == "__main__":
    classifier = ClassificateurThemesDiscours()
    classifier.analyser_csvdiscours()
