from datetime import datetime 
"""
@file Document.py
@brief Définition des classes représentant des documents et leur gestion.

@details
Ce fichier définit plusieurs classes pour modéliser des documents génériques, des posts Reddit et des articles Arxiv.
- Document : Classe de base pour tous les documents.
- RedditDocument : Classe dérivée pour les posts Reddit.
- ArxivDocument : Classe dérivée pour les articles Arxiv.
- DocumentFactory : Factory permettant de créer des documents selon leur type.
- CorpusSingleton : Singleton pour gérer un corpus unique de documents.
"""
class Document:
    """
    @brief Classe de base représentant un document générique.

    @details
    Cette classe modélise un document avec des attributs comme le titre, l'auteur,
    la date de publication, l'URL source et le texte du document.
    """
    def __init__(self, titre, auteur, date, url, texte,type_doc="Document"):
        """
        @brief Initialise un document générique.
        @param titre Titre du document.
        @param auteur Nom de l'auteur.
        @param date Date de publication (datetime).
        @param url URL source du document.
        @param texte Contenu textuel du document.
        @param type_doc Type de document (par défaut "Document").
        """
        self.titre = titre  # le titre du document
        self.auteur = auteur # le nom de l’auteur
        self.date = date  if isinstance(date, datetime) else datetime.now() # la date de publication
        self. url = url   # l’url source
        self.texte = texte  #le contenu textuel du document
        self.type_doc = type_doc
    
    def getType(self):
        """
        @brief Retourne le type du document.
        @return Chaîne indiquant le type de document.
        """
        return self.type_doc
    
    def __repr__(self):
        """
        @brief Représentation textuelle d'un document.
        @return Chaîne représentant l'instance du document.
        """
        return f"Document(titre='{self.titre}', auteur='{self.auteur}', date='{self.date}', url='{self.url}', texte='{self.texte}')"

class RedditDocument(Document):
    """
    @brief Classe représentant un document spécifique à Reddit.

    @details
    Cette classe étend la classe Document pour inclure des attributs supplémentaires
    comme le nombre de commentaires associés à un post Reddit.
    """
    def __init__(self, titre, auteur, date, url, texte, commentaires):
        """
        @brief Initialise un document Reddit.
        @param titre Titre du post Reddit.
        @param auteur Auteur du post.
        @param date Date de publication.
        @param url URL du post.
        @param texte Contenu du post.
        @param commentaires Nombre de commentaires sur le post.
        """
        super().__init__(titre, auteur, date, url, texte, type_doc="Reddit")
        self.commentaires = commentaires

    def getType(self):
        """
        @brief Retourne le type du document.
        @return Chaîne indiquant le type de document.
        """
        return self.type_doc

    def __str__(self):
        """
        @brief Représentation textuelle d'un post Reddit.
        @return Chaîne décrivant le document Reddit avec son nombre de commentaires.
        """
        return f"Reddit Document: {self.titre} - {self.auteur} - {self.commentaires} commentaires"

    def get_commentaires(self):
        """
        @brief Retourne le nombre de commentaires.
        @return Nombre de commentaires.
        """
        return self.commentaires

    def set_commentaires(self, commentaires):
        """
        @brief Met à jour le nombre de commentaires.
        @param commentaires Nouveau nombre de commentaires.
        """
        self.commentaires = commentaires

class ArxivDocument(Document):
    """
    @brief Classe représentant un article scientifique Arxiv.

    @details
    Cette classe ajoute la gestion des co-auteurs aux attributs de base d'un document.
    """
    def __init__(self, titre, auteurs, date, url, texte, coauteurs):
        """
        @brief Initialise un document Arxiv.
        @param titre Titre de l'article.
        @param auteurs Auteur principal.
        @param date Date de publication.
        @param url URL de l'article.
        @param texte Résumé de l'article.
        @param coauteurs Liste des co-auteurs.
        """
        super().__init__(titre, auteurs, date, url, texte, type_doc="Arxiv")
        self.coauteurs = coauteurs

    def __str__(self):
        """
        @brief Représentation textuelle d'un article Arxiv.
        @return Chaîne décrivant l'article Arxiv avec ses co-auteurs.
        """
        return f"Arxiv Document: {self.titre} - {self.auteur} - Coauteurs: {', '.join(self.coauteurs)}"

    def get_coauteurs(self):
        """
        @brief Retourne la liste des co-auteurs.
        @return Liste des co-auteurs.
        """
        return self.coauteurs

    def set_coauteurs(self, coauteurs):
        """
        @brief Met à jour la liste des co-auteurs.
        @param coauteurs Nouvelle liste de co-auteurs.
        """
        self.coauteurs = coauteurs

    def getType(self):
        """
        @brief Retourne le type du document.
        @return Chaîne indiquant le type de document.
        """
        return self.type_doc


class DocumentFactory:
    """
    @brief Factory pour créer des documents selon leur type. Cette classe utilitaire utilise uniquement une méthode statique creer_document().

    @details
    Cette classe génère des objets RedditDocument, ArxivDocument ou Document générique en fonction du type spécifié.
    """
    @staticmethod
    def creer_document(type_doc, titre, auteur, date, url, texte, extra=None):
        """
        @brief Crée un document en fonction de son type.
        @param type_doc Type du document ("Reddit" ou "Arxiv").
        @param titre Titre du document.
        @param auteur Auteur du document.
        @param date Date de publication.
        @param url URL du document.
        @param texte Contenu textuel du document.
        @param extra Information supplémentaire (commentaires ou co-auteurs).
        @return Instance de Document, RedditDocument ou ArxivDocument.
        """
        if type_doc == "Reddit":
            return RedditDocument(titre, auteur, date, url, texte, extra)
        elif type_doc == "Arxiv":
            return ArxivDocument(titre, auteur, date, url, texte, extra)
        else:
            return Document(titre, auteur, date, url, texte)


''' 
test pour créer et afficher des instances de RedditDocument et ArxivDocument en utilisant le polymorphisme. Chaque document est affiché avec son type (Reddit ou Arxiv)
'''
# Test de l'ajout de documents et affichage avec polymorphisme
if __name__ == "__main__":
    docs = [
        RedditDocument("Post Reddit 1", "Alice", datetime(2024, 1, 10), "https://reddit.com/post1", "Contenu Reddit 1", 15),
        ArxivDocument("Article Arxiv 1", "Bob", datetime(2023, 12, 5), "https://arxiv.org/1234", "Résumé Arxiv 1", ["Coauteur1", "Coauteur2"]),
        RedditDocument("Post Reddit 2", "Charlie", datetime(2024, 2, 15), "https://reddit.com/post2", "Contenu Reddit 2", 45)
    ]

    for doc in docs:
        print(f"{doc.getType()} - {doc}")
