import subprocess
from datetime import datetime
from src.Document import Document, RedditDocument, ArxivDocument, CorpusSingleton, DocumentFactory
from src.RecuperationDocs import RedditScrap, ArxivScrap
from src.GestionErreurs import GestionErreurs 

from src.Corpus import Corpus
from src.SearchEngine import SearchEngine
from src.MatriceDocuments import MatriceDocuments
from src.Frequence import Frequence


''' 
Tests de dcuments
'''

# rev2

''' 
Tests de la classe Corpus (version 2)
'''
def test_ajout_document_corpus():
    corpus = Corpus("Test Corpus")
    doc = Document("Titre Test", "Auteur Test", datetime(2024, 1, 1), "https://adress_fictive.com", "Texte de test")
    corpus.ajouter_document(doc)
    assert len(corpus.id2doc) == 1
    assert corpus.id2doc[doc.url].titre == "Titre Test"
    assert corpus.ndoc == 1
    assert corpus.naut == 1

'''
 Tests pour MatriceDocuments : Construction des matrices TF 
'''
def test_construction_matrice_TF():
    corpus = Corpus("Test Corpus")
    corpus.ajouter_document(Document("Doc1", "Auteur", datetime.now(), "url1", "Python est puissant"))
    corpus.ajouter_document(Document("Doc2", "Auteur", datetime.now(), "url2", "Python pour le machine learning"))
    
    matrice = MatriceDocuments(corpus)
    matrice.construire_matrice_TF()
    
    assert matrice.mat_TF is not None
    assert matrice.mat_TF.shape == (2, len(matrice.vocab))  # 2 documents, taille du vocabulaire
    assert matrice.df['python'] > 0

'''
 Tests pour MatriceDocuments : Construction des matrices TFxIDF.
'''
def test_construction_matrice_TFxIDF():
    corpus = Corpus("Test Corpus")
    corpus.ajouter_document(Document("Doc1", "Auteur", datetime.now(), "url1", "Python est puissant"))
    corpus.ajouter_document(Document("Doc2", "Auteur", datetime.now(), "url2", "Python pour le machine learning"))
    
    matrice = MatriceDocuments(corpus)
    matrice.construire_matrice_TF()
    tfidf_matrix = matrice.construire_matrice_TFxIDF()

    assert tfidf_matrix is not None
    assert tfidf_matrix.shape == matrice.mat_TF.shape

'''
 Tests pour Frequence : Nettoyage de texte et vocabulaire.
'''
def test_nettoyage_texte():
    texte = "Water resources are essential for the environment and human life."
    resultat = Frequence.nettoyer_texte(texte)
    assert resultat == "water resources are essential for the environment and human life"  # Vérifie suppression de la ponctuation et des chiffres

'''
 Tests construction vocabulaire
'''
def test_construction_vocabulaire():
    corpus = Corpus("Test Corpus")
    corpus.ajouter_document(Document("Doc1", "Auteur", datetime.now(), "url1", "Python est puissant"))
    vocabulaire = Frequence.construire_vocabulaire(corpus.id2doc.values())
    
    assert 'python' in vocabulaire
    assert 'puissant' in vocabulaire
    assert len(vocabulaire) == 3  # "Python", "est", "puissant"

'''
Tests pour SearchEngine : Vérification de la recherche par mots-clés et des résultats pertinents. 
'''
def test_search_engine():
    corpus = Corpus("Test Corpus")
    corpus.ajouter_document(Document("Doc1", "Author", datetime.now(), "url1", "Water resources are vital for agriculture"))
    corpus.ajouter_document(Document("Doc2", "Author", datetime.now(), "url2", "Monitoring water quality is essential for ecosystems"))
    corpus.ajouter_document(Document("Doc3", "Author", datetime.now(), "url3", "The preservation of water resources helps prevent droughts"))

    moteur = SearchEngine(corpus)
    moteur.matrice.construire_matrice_TF()
    moteur.matrice.construire_matrice_TFxIDF()

    resultats = moteur.search("water", n_resultats=2)
    assert len(resultats) == 2
    assert resultats.iloc[0]['Titre'] == "Doc1"

'''
Test du Programme Principal (Simulation via subprocess) rev2
'''
def test_main_execution_v2():
    result = subprocess.run(
        ["python", "-m", "src.rev2"], 
        capture_output=True, 
        text=True
    )
    assert "water" in result.stdout
    assert "Titre" in result.stdout
    assert result.returncode == 0
