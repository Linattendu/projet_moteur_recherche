 # Fichier Utils.py
import re
import unicodedata
import string
import os
import pickle

class Utils:
    """
    @brief Classe utilitaire contenant diverses fonctions pour le traitement de texte, 
           la manipulation de corpus, et la gestion des fichiers.
    """
    @staticmethod
    def decouper_en_phrases(texte):
        """
        @brief Découpe un texte en phrases.

        @param texte : str
            Le texte à découper.
        @return : list
            Une liste contenant les phrases extraites du texte.
        """
        return re.findall(r"[^.]+(?:\.(?:\s|\n))?", texte)

    
    @staticmethod
    def nettoyer_texte(texte):
        """
        @brief Nettoie un texte en supprimant les apostrophes, ponctuations et en mettant en minuscule.

        @param texte : str
            Le texte à nettoyer.
        @return : str
            Texte nettoyé et normalisé.
        """
        # 1. Conversion en minuscules
        texte = texte.lower()
        
        # 2. Suppression des accents
        texte = ''.join((c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn'))
        
        # 3. Gestion des contractions anglaises (don't -> dont, l'apostrophe est retirée)
        texte = re.sub(r"(\w)'(\w)", r"\1\2", texte)  # don't -> dont, I'm -> im
        
        # 4. Suppression de la ponctuation
        texte = texte.translate(str.maketrans('', '', string.punctuation))
        
        # 5. Suppression des espaces multiples
        texte = ' '.join(texte.split())
        return texte
        
    
    @staticmethod
    def concatener_textes(corpus):
        """
        @brief Concatène les textes de tous les documents dans un corpus.

        @param corpus : Corpus
            Le corpus contenant les documents à concaténer.
        @return : str
            Texte concaténé et nettoyé.
        """
        texte_brut = ' '.join(doc.texte for doc in corpus.id2doc.values())
        texte_nettoye = Utils.nettoyer_texte(texte_brut)
        print("✅ Texte concaténé et nettoyé.")
        return texte_nettoye
   
    
    @staticmethod
    def load(path):
        """
        @brief Charge un objet sérialisé depuis un fichier pickle.

        @param path : str
            Chemin vers le fichier pickle.
        @return : object
            Objet chargé depuis le fichier.
        """
        with open(path, 'rb') as f:
            return pickle.load(f)
    
     
    @staticmethod
    def extraire_extrait(texte, mot_cle):
        """
        @brief Extrait un passage d'un texte contenant un mot-clé et un contexte de mots autour.

        @param texte : str
            Le texte à analyser.
        @param mot_cle : str
            Le mot-clé à rechercher.
        @return : str
            Extrait contenant le mot-clé et son contexte, ou "Extrait non disponible" si non trouvé.
        """
        # Mettre en minuscule
        mot_cle = mot_cle.lower()

        # Expression régulière pour capturer le mot-clé avec 5 mots avant et 5 après
        pattern = r'(\b\w+\b\s*){0,' + str(15) + r'}' + re.escape(mot_cle) + r'(\s*\b\w+\b){0,' + str(15) + r'}'
        
        matches = re.finditer(pattern, texte, re.MULTILINE)
        
        for _, match in enumerate(matches, start=1):
            if match:
                return match.group()  # Retourne l'extrait complet (mot-clé + contexte)
        return "Extrait non disponible"
    
