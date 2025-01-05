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
# A faire prochainement