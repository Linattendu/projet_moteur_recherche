import sqlite3
import pickle
from src.SearchEngine import SearchEngine
from src.Corpus import Corpus
import streamlit as st
import os
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix

DB_PATH = "../db/corpus_matrix.sqlite"
RESULTS_PATH = "../db/classified_results.pkl"

class ThemeClassifier:
    def __init__(self):
        self.keywords_par_theme = {
            "science": ["research", "experiment", "innovation", "climate", "discovery", "laboratory", "physics"],
            "health": ["hospital", "medicare", "vaccine", "healthcare", "doctor", "nurse", "therapy"],
            "technology": ["AI", "data", "digital", "robotics", "cybersecurity", "software", "hardware"],
            "climatechange": ["carbon", "renewable", "environment", "sustainability", "warming", "greenhouse", "pollution"],
            "education": ["school", "university", "student", "teacher", "curriculum", "learning", "lecture"]
        }
        
  
    def charger_corpus_depuis_db(self, nom_corpus):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT corpus_pkl, matrice_TF_pkl, matrice_TFxIDF_pkl, vocab_pkl FROM corpus WHERE nom_corpus = ?
        ''', (nom_corpus,))
        result = cursor.fetchone()
        conn.close()

        if result:
            corpus = pickle.loads(result[0]) if result[0] else None
            tfidf = pickle.loads(result[2]) if result[2] else None
            vocab = pickle.loads(result[3]) if result[3] else None
            return corpus, tfidf, vocab
        else:
            print("❌ Corpus non trouvé !")
            return None, None, None

    def classifier_document_par_themes(self, doc_index, vocab, tfidf):
        if isinstance(tfidf, coo_matrix):
            tfidf = tfidf.tocsr()
        scores_par_theme = {}
        for theme, mots in self.keywords_par_theme.items():
            score = 0
            for mot in mots:
                if mot in vocab:
                    mot_index = vocab[mot]['id']
                    score += tfidf[doc_index, mot_index]  # Utilisation de la matrice TF-IDF
            if score > 0:
                scores_par_theme[theme] = score
        return scores_par_theme

    def creer_sous_corpus(self, corpus, vocab, tfidf):
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

    def sauvegarder_resultats(self, resultats):
        with open(RESULTS_PATH, 'wb') as f:
            pickle.dump(resultats, f)
        print(f"✅ Résultats sauvegardés dans {RESULTS_PATH}")

    def analyser_csvpolitics(self):
        corpus, tfidf, vocab = self.charger_corpus_depuis_db("csvdiscours")
        if corpus is None or tfidf is None or vocab is None:
            print("Corpus, TF-IDF ou vocabulaire non disponible.")
            return

        print(f"Nombre de documents : {len(corpus.id2doc)}")
        sous_corpus = self.creer_sous_corpus(corpus, vocab, tfidf)
        self.sauvegarder_resultats(sous_corpus)
        
        for theme, docs in sous_corpus.items():
            print(f"\nThème : {theme}")
            for doc, score in docs:
                print(f"- Titre : {doc.titre}")
                print(f"  Auteur : {doc.auteur}")
                print(f"  Date : {doc.date}")
                print(f"  Score : {score:.2f}")

if __name__ == "__main__":
    classifier = ThemeClassifier()
    classifier.analyser_csvpolitics()
