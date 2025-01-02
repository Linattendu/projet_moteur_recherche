import sys
import os
import subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from datetime import datetime
from src.Document import Document, RedditDocument, ArxivDocument, DocumentFactory
from src.RecuperationDocs import RedditScrap, ArxivScrap
from src.GestionErreurs import GestionErreurs
from src.CorpusSingleton import CorpusSingleton



''' 
Tests de dcuments
'''

def test_creation_document():
    doc = Document("Titre Test", "Auteur Test", datetime(2024, 1, 1), "https://adress_fictive.com", "Texte de test")
    assert doc.titre == "Titre Test"
    assert doc.auteur == "Auteur Test"
    

def test_creation_reddit_document():
    reddit_doc = RedditDocument("Post Reddit", "Alice", datetime(2024, 1, 10), "https://reddit.com/post1", "Contenu Reddit", 20)
    assert reddit_doc.getType() == "Reddit"
    assert reddit_doc.get_commentaires() == 20
    reddit_doc.set_commentaires(30)
    assert reddit_doc.get_commentaires() == 30

def test_creation_arxiv_document():
    arxiv_doc = ArxivDocument("Article Arxiv", "Bob", datetime(2024, 2, 15), "https://arxiv.org/1234", "Résumé Arxiv", ["Coauteur1", "Coauteur2"])
    assert arxiv_doc.getType() == "Arxiv"
    assert arxiv_doc.get_coauteurs() == ["Coauteur1", "Coauteur2"]
    arxiv_doc.set_coauteurs(["Coauteur1", "Coauteur3"])
    assert arxiv_doc.get_coauteurs() == ["Coauteur1", "Coauteur3"]
    

''' 
Tests Singleton (Corpus)
'''
def test_instance_singleton():
    corpus1 = CorpusSingleton("mon_corpus1")
    corpus2 = CorpusSingleton("mon_corpus2")
    assert corpus1 is corpus2  # Vérification singleton

def test_ajout_document():
    corpus = CorpusSingleton("mon_corpus")
    doc = Document("Titre Singleton", "Auteur", datetime.now(), "https://adress_fictive.com", "Texte")
    corpus.ajouter_document(doc)
    assert corpus.ndoc == 1


''' 
Tests DocumentFactory
'''

def test_creation_DocumentFactory_reddit():
    reddit_doc = DocumentFactory.creer_document("Reddit", "Post Reddit", "Alice", datetime.now(), "https://reddit.com/post", "Texte", 10)
    assert isinstance(reddit_doc, RedditDocument)
    assert reddit_doc.getType() == "Reddit"
    assert reddit_doc.get_commentaires() == 10

def test_creation_DocumentFactory_arxiv():
    arxiv_doc = DocumentFactory.creer_document("Arxiv", "Article Arxiv", "Bob", datetime.now(), "https://arxiv.org/4567", "Résumé", ["Coauteur1"])
    assert isinstance(arxiv_doc, ArxivDocument)
    assert arxiv_doc.getType() == "Arxiv"
    assert arxiv_doc.get_coauteurs() == ["Coauteur1"]

def test_creation_factory_default():
    default_doc = DocumentFactory.creer_document("Autre", "Titre Autre", "Auteur", datetime.now(), "https://adress_fictive.com", "Texte")
    assert isinstance(default_doc, Document)
    assert default_doc.getType() == "Document"

''' 
Tests Scraping (Reddit et Arxiv)
'''
def test_reddit_scrap():
    corpus = CorpusSingleton("mon_corpus")
    erreur = GestionErreurs(log_file="app_errors.log")
    scraper = RedditScrap(corpus, erreur)
    scraper.recuperer_posts("learnpython", limit=2)
    assert corpus.ndoc > 0

def test_arxiv_scrap():
    corpus = CorpusSingleton("mon_corpus")
    erreur = GestionErreurs(log_file="app_errors.log")
    scraper = ArxivScrap(corpus, erreur)
    scraper.recuperer_articles("machinelearning", max_results=2)
    assert corpus.ndoc > 0

''' 
Test du Programme Principal (Simulation via subprocess)
'''
def test_main_execution():
    
    result = subprocess.run(
        ["python", "-m", "src.rev1"], 
        capture_output=True, 
        text=True
    )

