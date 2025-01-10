import pytest
from src.CorpusMatriceManager import CorpusMatriceManager
from src.SearchEngine import SearchEngine
from src.ClassificateurThemesDiscours import ClassificateurThemesDiscours
from src.Corpus import Corpus
from src.Document import Document
from datetime import datetime
from scipy.sparse import csr_matrix
import pickle
import os

# Variables globales pour les tests
manager = CorpusMatriceManager()
corpus = Corpus("csvdiscours")
classifier = ClassificateurThemesDiscours()
moteur = SearchEngine("csvdiscours")

# Tests pour CorpusMatrixManager
def test_creer_corpus_discours():
    """
    Teste la création d'un corpus à partir des discours.
    Vérifie que le corpus est bien inséré dans la base de données.
    """
    manager.creer_corpus_discours()
    result = manager.cursor.execute("SELECT COUNT(*) FROM corpus WHERE theme='discours'").fetchone()[0]
    assert result > 0, "Le corpus des discours n'a pas été créé correctement."

def test_stocker_en_base_de_donnees():
    """
    Teste le stockage des chemins des fichiers pickle dans la base de données.
    """
    manager.stocker_en_base_de_donnees()
    result = manager.cursor.execute("SELECT chemin_TF, chemin_TFIDF FROM corpus WHERE theme='discours'").fetchone()
    assert result is not None, "Les chemins des matrices n'ont pas été stockés."
    assert result[0] is not None, "Le chemin de la matrice TF est manquant."
    assert result[1] is not None, "Le chemin de la matrice TF-IDF est manquant."


# Tests pour SearchEngine
def test_moteur_recherche():
    """
    Teste le moteur de recherche pour le mot-clé 'climate'.
    Vérifie que les résultats contiennent le mot-clé dans l'extrait.
    """
    resultats = moteur.search("climate", n_resultats=10)
    assert len(resultats) > 0, "Aucun résultat trouvé pour 'climate'."
    for _, row in resultats.iterrows():
        assert "climate" in row['Extrait'].lower(), "Le mot-clé 'climate' est absent des résultats."


# Tests pour ClassificateurThemesDiscours
def test_creer_sous_corpus():
    """
    Teste la classification des documents en sous-corpus thématiques.
    Vérifie que les documents sont correctement associés aux thèmes.
    """
    # Ajouter des documents au corpus
    corpus.ajouter_document(Document(
        "Doc1",
        "Barack Obama",
        datetime(2021, 1, 1),
        "https://www.reddit.com/r/",
        "Climate change is a pressing issue.",
        "Document reddit",
        "climatechange"
    ))
    corpus.ajouter_document(Document(
        "Doc2",
        "Donald Trump",
        datetime(2022, 1, 2),
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

    # Création du sous-corpus
    sous_corpus = classifier.creer_sous_corpus(corpus, vocab, tfidf)
    print("Sous-corpus :", sous_corpus)
    # Vérifications
    assert "climatechange" in sous_corpus, "Le thème 'climatechange' est absent du sous-corpus."
    assert len(sous_corpus) == 2, "Tous les documents n'ont pas été classifiés."
    
    # Vérifier l'ordre des documents par score
    scores = [score for _, score in sous_corpus["climatechange"]]
    assert scores == sorted(scores, reverse=True), "Les documents ne sont pas triés par score."


# Ajout de tests unitaires complémentaires
def test_charger_document_pickle():
    """
    Teste la fonctionnalité de chargement des documents à partir de fichiers pickle.
    """
    chemin_test = "test_document.pkl"
    doc = Document(
        "DocTest",
        "AuthorTest",
        datetime(2023, 1, 1),
        "http://example.com",
        "This is a test document.",
        "SourceTest",
        "test_theme"
    )

    # Sauvegarder le document en pickle
    with open(chemin_test, 'wb') as f:
        pickle.dump(doc, f)

    # Charger le document
    with open(chemin_test, 'rb') as f:
        loaded_doc = pickle.load(f)

    assert loaded_doc.titre == doc.titre, "Le titre du document chargé ne correspond pas."
    assert loaded_doc.auteur == doc.auteur, "L'auteur du document chargé ne correspond pas."

    # Nettoyer le fichier de test
    os.remove(chemin_test)


# Main pour exécuter les tests
if __name__ == "__main__":
    pytest.main()


