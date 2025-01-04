import subprocess
from datetime import datetime
from src.Document import Document, RedditDocument, ArxivDocument, DocumentFactory
from src.RecuperationDocs import RedditScrap, ArxivScrap
from src.GestionErreurs import GestionErreurs 
from src.CorpusSingleton import CorpusSingleton

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
""" def test_ajout_document_corpus():
    corpus = Corpus("Test Corpus")
    doc = Document("Titre Test", "Auteur Test", datetime(2024, 1, 1), "https://adress_fictive.com", "Texte de test")
    corpus.ajouter_document(doc)
    assert len(corpus.id2doc) == 1
    assert corpus.id2doc[doc.identifiant_unique].titre == "Titre Test"
    assert corpus.ndoc == 1
    assert corpus.naut == 1 """


def test_ajouter_document():
    # Initialisation du corpus
    corpus = Corpus("Test Corpus")

    # Création d'un document avec tous les arguments nécessaires
    doc = Document(
        titre="Titre Test",
        auteur="Auteur Test",
        date=datetime(2024, 1, 1),
        url="https://exemple.com",  # Ajoutez l'URL si elle est requise
        texte="  Texte de test avec espaces   "
    )
    
    # Ajout du document au corpus
    corpus.ajouter_document(doc)

    # Vérifications
    assert corpus.ndoc == 1
    assert len(corpus.id2doc) == 1




'''
 Tests pour MatriceDocuments : Construction des matrices TF 
'''
def test_construction_matrice_TF():
    corpus = Corpus("Test Corpus")
    corpus.ajouter_document(Document("Doc1", "Auteur", datetime.now(), "url1", "Python est puissant"))
    corpus.ajouter_document(Document("Doc2", "Auteur", datetime.now(), "url2", "Python pour le machine learning"))
    
    matrice = MatriceDocuments(corpus)
    matrice_TF = matrice.construire_vocab_et_matrice_TF()
    
    # Vérifications
    assert matrice_TF is not None, "La matrice TF ne doit pas être None."
    assert matrice_TF.shape == (2, len(matrice.vocab)), "La matrice TF a des dimensions incorrectes."
    assert matrice.vocab["python"]["freq"] > 0, "Le mot 'python' doit apparaître dans le vocabulaire."


'''
 Tests pour MatriceDocuments : Construction des matrices TFxIDF.
'''
def test_construction_matrice_TFxIDF():
    corpus = Corpus("Test Corpus")
    corpus.ajouter_document(Document("Doc1", "Auteur", datetime.now(), "url1", "Python est puissant"))
    corpus.ajouter_document(Document("Doc2", "Auteur", datetime.now(), "url2", "Python pour le machine learning"))
    
    matrice = MatriceDocuments(corpus)
    matrice.construire_vocab_et_matrice_TF()
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
    corpus.ajouter_document(Document(
        "Doc1", "Author1", "2024-01-01", 
        "https://www.reddit.com/r/", 
        "Water resources are vital for agriculture", 
        "Document reddit",
        "water"
        ))
    corpus.ajouter_document(Document(
        "Doc2",
        "Author2", 
        "2024-01-02", 
        "https://www.reddit.com/r/", 
        "Monitoring water quality is essential for ecosystems", 
        "Document reddit",
        "water"
        ))
    corpus.ajouter_document(Document(
        "Doc3", 
        "Author3", 
        "2024-01-03", 
        "https://www.reddit.com/r/", 
        "The preservation of water resources helps prevent droughts", 
        "Document reddit",
        "water"
        ))

    moteur = SearchEngine(corpus)
    moteur.matrice.construire_vocab_et_matrice_TF()
    moteur.matrice.construire_matrice_TFxIDF()

    print("corpus", corpus)

    resultats = moteur.search("Water", n_resultats=3)
    print(resultats)
    assert len(resultats) == 3
    assert resultats.iloc[0]['contenu'] == "Water resources are vital for agriculture".lower()

'''
Test du Programme Principal (Simulation via subprocess) rev2
'''

def test_main_execution_v2():
    result = subprocess.run(
        ["python", "-m", "src.Verifier_moteur_recherche"],
        capture_output=True,
        text=True
    )
    assert "medicine" in result.stdout, f"Expected 'medicine' in stdout, but got: {result.stdout}"
