import pandas as pd
import pickle
from datetime import datetime
from src.Author import Author

"""
@file Corpus.py
@brief Gestion du corpus de documents et des auteurs.

@details
Cette classe gère un ensemble de documents (id2doc) et d'auteurs (id2aut).
Elle offre des méthodes pour ajouter des documents, trier par date ou par titre,
et sauvegarder/charger le corpus via pickle.

Exemple de structure de corpus :
id2doc est un dictionnaire des Documents permettant une recherche rapide
d'un document à partir de son identifiant unique.
id2aut regroupe les auteurs et leur production associée.

Comment ça fonctionne :
Lorsqu'un document est ajouté, il est stocké dans id2doc avec son identifiant unique.
L'auteur du document est soit ajouté (s'il n'existe pas déjà) à id2aut, soit mis à jour.
"""
class Corpus:
    """
    @brief Représente un corpus de documents et d'auteurs.
    
    @details
    Cette classe permet d'ajouter des documents et de gérer les auteurs associés.
    Elle permet également le tri des documents et la persistance du corpus via pickle.
    """
    def __init__(self, nom_corpus):
        """
        @brief Initialise un corpus.
        @details le nom corpus sert à :
        - faire la différence entre les différents corpus
        - aider dans l'affichage des logs
        - identifier le nom de la sauvegarde
        @param nom_corpus Nom du corpus.
        ECT...
        """
        self.nom_corpus = nom_corpus
        self.authors = {}
        self.id2doc = {} # dictionnaire des documents
        self.ndoc = 0 # nombre de commentaires
        self.naut = 0 # nombre d'auteurs

    def ajouter_document(self, doc):
        """
        @brief Ajoute un document au corpus.
        @param doc Instance de Document à ajouter.
        @details
        Si l'auteur du document n'existe pas, il est ajouté au dictionnaire des auteurs.
        Sinon, la production de l'auteur est mise à jour.
        """
        self.id2doc[doc.url] = doc
        self.ndoc += 1

        # Ajoute ou met à jour l'auteur
        auteur_nom = doc.auteur
        if auteur_nom not in self.authors:
            self.authors[auteur_nom] = Author(auteur_nom)
            self.naut += 1
        
        self.authors[auteur_nom].add(doc.url, doc)

    def trier_par_date(self, n=10):
        """
        @brief Trie les documents par date de publication.
        @param n Nombre de documents à retourner (par défaut 10).
        @return Liste des n documents les plus récents.
        """
        return sorted(self.id2doc.values(), key=lambda d: d.date, reverse=True)[:n]

    def trier_par_titre(self, n=10):
        """
        @brief Trie les documents par titre alphabétique.
        @param n Nombre de documents à retourner (par défaut 10).
        @return Liste des n premiers documents triés par titre.
        """
        return sorted(self.id2doc.values(), key=lambda d: d.titre)[:n]

    def __repr__(self):
        """
        @brief Retourne une représentation textuelle du corpus.
        @return Chaîne représentant le corpus (nom, nombre de documents et auteurs).
        """
        return f"Corpus: {self.nom_corpus} - {self.ndoc} documents, {self.naut} auteurs"

    def save(self, path):
        """
        @brief Retourne une représentation textuelle du corpus.
        @return Chaîne représentant le corpus (nom, nombre de documents et auteurs).
        """
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        """
        @brief Charge un corpus à partir d'un fichier pickle.
        @param path Chemin du fichier de sauvegarde.
        @return Instance de Corpus chargée.
        """
        with open(path, 'rb') as f:
            return pickle.load(f)
