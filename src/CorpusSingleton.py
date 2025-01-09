from src.Corpus import Corpus  # Import de la classe Corpus

class CorpusSingleton(Corpus):
    """
    @brief Singleton gérant un corpus unique de documents.

    @details
    Permet de stocker et d'afficher des documents en s'assurant qu'une seule instance du corpus existe.
    """
    _instance = None

    def __new__(cls, nom_corpus="corpus_reddit_arxiv"):
        if cls._instance is None:
            cls._instance = super(CorpusSingleton, cls).__new__(cls)
            Corpus.__init__(cls._instance, nom_corpus)  # Appelle __init__ de Corpus sur l'instance
        return cls._instance

    def ajouter_document(self, doc):
        """
        @brief Ajoute un document au corpus.
        @param doc Document à ajouter.
        """
        self.id2doc[doc.url] = doc  # Utilisation de id2doc au lieu de documents
        self.ndoc += 1
    
    def afficher_documents(self):
        """
        @brief Affiche tous les documents du corpus.
        """
        for doc in self.id2doc.values():
            print(doc)
