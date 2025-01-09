import pytest
from src.CorpusMatrixManager import CorpusMatrixManager
from src.SearchEngine import SearchEngine
from src.analyse_discours import ThemeClassifier
from src.Corpus import Corpus
from src.Document import Document
from datetime import datetime
from scipy.sparse import csr_matrix
from datetime import datetime

def test_creer_corpus_discours():
    manager = CorpusMatrixManager()
    manager.creer_corpus_discours()
    # Vérifiez que le corpus a été créé correctement
    assert manager.cursor.execute("SELECT COUNT(*) FROM corpus WHERE theme='discours'").fetchone()[0] > 0

def test_stocker_en_base_de_donnees():
    manager = CorpusMatrixManager()
    manager.stocker_en_base_de_donnees()
    # Vérifiez que les matrices TF et TFxIDF sont bien stockées
    result = manager.cursor.execute("SELECT matrice_TF_pkl, matrice_TFxIDF_pkl FROM corpus WHERE theme='discours'").fetchone()
    assert result is not None
    assert result[0] is not None  # matrice_TF
    assert result[1] is not None  # matrice_TFxIDF


def test_search_with_database():
    moteur = SearchEngine("csvdiscours")
    resultats = moteur.search("climate", n_resultats=10)
    assert len(resultats) > 0
    for _, row in resultats.iterrows():
        assert "climate" in row['Extrait'].lower()


# Convertir les dates des documents
date1 = datetime.strptime("2021-01-01", "%Y-%m-%d").date()
date2 = datetime.strptime("2022-01-02", "%Y-%m-%d").date()



def test_creer_sous_corpus():
    classifier = ThemeClassifier()
    corpus = Corpus("csvdiscours")

    # Ajouter des documents avec le thème "climatechange"
    corpus.ajouter_document(Document(
        "Doc1",
        "Barack Obama",
        datetime(2021, 1, 1),  # Utilisation directe de datetime pour simplifier
        "https://www.reddit.com/r/",
        "Climate change is a pressing issue.",
        "Document reddit",
        "climatechange"
    ))
    corpus.ajouter_document(Document(
        "Doc2",
        "Donald Trump",
        datetime(2022, 1, 2),  # Utilisation directe de datetime
        "https://www.reddit.com/r/",
        "Global warming is a major challenge.",
        "Document reddit",
        "climatechange"
    ))

    # Vocabulaire minimal
    vocab = {"climate": {"id": 0}, "warming": {"id": 1}}

    # Matrice TF-IDF simplifiée (2 documents, 2 mots)
    tfidf_data = [1.0, 0.8]  # Scores TF-IDF pour chaque document
    tfidf_rows = [0, 1]  # Indices des documents
    tfidf_cols = [0, 1]  # Indices des mots
    tfidf = csr_matrix((tfidf_data, (tfidf_rows, tfidf_cols)), shape=(2, 2))

    # Appeler la méthode pour créer le sous-corpus
    sous_corpus = classifier.creer_sous_corpus(corpus, vocab, tfidf)
    # Vérifier que le sous-corpus contient le thème "climatechange"
    assert "climatechange" in sous_corpus

    # Vérifier que les deux documents sont bien présents
    assert len(sous_corpus) == 2
