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
Tests de documents
'''

''' 
Tests de la classe Corpus (version 2)
'''

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
    corpus.ajouter_document(Document("Doc1", "Auteur1", datetime.now(), "url1", "Water resources are vital"))
    corpus.ajouter_document(Document("Doc2", "Auteur2", datetime.now(), "url2", "Monitoring water quality is essential for ecosystems"))
    
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
    corpus.ajouter_document(Document("Doc1", "Auteur1", datetime.now(), "url1", "Water resources are vital"))
    corpus.ajouter_document(Document("Doc2", "Auteur2", datetime.now(), "url2", "Monitoring water quality is essential for ecosystems"))
    
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
    corpus.ajouter_document(Document("Doc1", "Auteur", datetime.now(), "url1", "Water resources are vital"))
    vocabulaire = Frequence.construire_vocabulaire(corpus.id2doc.values())
    
    assert 'water' in vocabulaire
    assert 'resources' in vocabulaire
    assert len(vocabulaire) == 4  # "Water", "resources", "are", "vital"

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

    # Initialisation du moteur de recherche
    moteur = SearchEngine(corpus)

    # Recherche pour le mot-clé "water"
    resultats = moteur.search("water", n_resultats=3)

    # Vérifications
    assert len(resultats) == 3, f"Expected 3 results, but got {len(resultats)}"

    # Normalisation des contenus attendus et des résultats pour la comparaison
    contenus_attendus = [
        "Water resources are vital for agriculture",
        "Monitoring water quality is essential for ecosystems",
        "The preservation of water resources helps prevent droughts"
    ]
    contenus_attendus_normalized = set([contenu.lower() for contenu in contenus_attendus])
    resultats_normalized = set([contenu.lower() for contenu in resultats['contenu'].values])

    assert resultats_normalized == contenus_attendus_normalized, \
        f"Expected contents {contenus_attendus}, but got {resultats['contenu'].values}"

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
