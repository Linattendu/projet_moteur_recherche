class Author:
    """
    @brief Représente un auteur dans le système de gestion documentaire.
    
    @details
    Cette classe gère les informations d'un auteur, incluant le nom, le nombre de documents publiés,
    et une liste des documents associés.
    
    @param name Nom de l'auteur.
    """
    def __init__(self, name):
        """
        @brief Initialise un auteur avec son nom.
        @param name Nom de l'auteur.
        """
        self.name = name
        self.ndoc = 0 # nombre de documents publies
        self.production = {} # dictionnaire des documents ecrits par l’auteur
        
    def add(self, document_id,document):
        """
        @brief Ajoute un document à la production de l'auteur.
        @param document_id Identifiant unique du document.
        @param document Instance de la classe Document associée.
        @details
        Cette méthode incrémente également le nombre de documents de l'auteur.
        """
        self.production[document_id] = document
        self.ndoc += 1
  
    def __repr__(self):
        """
        @brief Retourne une représentation textuelle de l'auteur.
        @return Chaîne représentant l'auteur (nom et nombre de documents).
        """
        return f"Author :  {self.name}, Nombre de documents : {self.ndoc}"


