import re
from collections import Counter

"""
@file Frequence.py
@brief Classe utilitaire pour l'analyse et le traitement des textes.

@details
La classe Frequence fournit des méthodes statiques pour nettoyer le texte, 
construire un vocabulaire unique, et compter les occurrences des mots dans un corpus.
"""

class Frequence:
    """
    @brief Classe utilitaire pour gérer la fréquence des mots dans les documents.
    """

    @staticmethod
    def nettoyer_texte(texte):
        """
        @brief Nettoie une chaîne de texte.
        @details 
        * Convertit tout le texte en minuscules.
        * Supprime toute la ponctuation (remplacée par des espaces).
        * Retire les chiffres.
        * Gère les espaces multiples et nettoie les bords (strip).
                
        @param texte Chaîne à nettoyer.
        @return Texte nettoyé en minuscules, sans ponctuation ni chiffres.
        """
        texte = texte.lower()  # Mise en minuscules
        texte = re.sub(r'[^\w\s]', ' ', texte)  # Suppression de la ponctuation
        texte = re.sub(r'\d+', '', texte)  # Suppression des chiffres
        texte = re.sub(r'\s+', ' ', texte).strip()  # Suppression des espaces multiples
        return texte

    @staticmethod
    def construire_vocabulaire(documents):
        """
        @brief Construit un vocabulaire unique à partir des documents du corpus.
        @details
        * Parcourt tous les documents, nettoie leur texte et ajoute chaque mot unique à un ensemble (set).
        * L'utilisation de set élimine automatiquement les doublons.
        @param documents Liste des documents à analyser.
        @return Ensemble contenant tous les mots uniques du corpus.
        """
        vocabulaire = set()
        for doc in documents:
            texte_propre = Frequence.nettoyer_texte(doc.texte)
            mots = texte_propre.split()
            vocabulaire.update(mots)
        return vocabulaire

    @staticmethod
    def compter_occurrences(documents):
        """
        @brief Compte les occurrences de chaque mot dans les documents.
        @details
        Parcourt tous les documents, nettoie leur texte et compte la fréquence de chaque mot à l'aide de Counter de la bibliothèque collections.
        @param documents Liste des documents à analyser.
        @return Counter contenant la fréquence de chaque mot.
        """
        compteur = Counter()
        for doc in documents:
            texte_propre = Frequence.nettoyer_texte(doc.texte)
            mots = texte_propre.split()
            compteur.update(mots)
        return compteur
