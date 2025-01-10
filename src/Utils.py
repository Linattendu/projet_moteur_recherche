 # Fichier Utils.py
import re
import unicodedata
import string
import os
import pickle

class Utils:
    """
    @brief Classe utilitaire pour diverses opérations textuelles et de gestion de corpus.
    """
    
    @staticmethod
    def decouper_en_phrases(texte):
        """
        @brief Découpe un texte en phrases.
        @param texte Texte à découper.
        @return Liste des phrases extraites du texte.
        """
        return re.findall(r"[^.]+(?:\.(?:\s|\n))?", texte)

    
    @staticmethod
    def nettoyer_texte(texte):
        """
        @brief Nettoie un texte pour le normaliser.
        @details
        Supprime les accents, ponctuations, espaces multiples et met en minuscules.
        @param texte Texte à nettoyer.
        @return Texte nettoyé.
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
        
        """ texte = texte.lower()  # Convertir en minuscule
         # Remplacement spécifique pour ne pas perdre les formes comme L'IA
        texte = re.sub(r"(\b[a-z])'([a-z])", r"\1 \2", texte)  # L'IA -> l ia (sans perte du "ia")

        # Suppression de la ponctuation restante
        texte = re.sub(r"[\.,’]", "", texte)  # Retirer points et virgules
        return texte
        """
    
    @staticmethod
    def concatener_textes(corpus):
        """
        @brief Concatène et nettoie les textes de tous les documents d'un corpus.
        @param corpus Instance du corpus contenant les documents.
        @return Texte concaténé et nettoyé.
        """
        texte_brut = ' '.join(doc.texte for doc in corpus.id2doc.values())
        texte_nettoye = Utils.nettoyer_texte(texte_brut)
        print("✅ Texte concaténé et nettoyé.")
        return texte_nettoye
    
    @staticmethod
    def dictionnaire_vocab(corpus):
        """
        @brief Construit un dictionnaire de vocabulaire pour un corpus.
        @details
        Associe chaque mot unique d'un corpus à un index pour le traitement textuel.
        @param corpus Instance du corpus contenant les documents.
        @return Dictionnaire {mot: index}.
        """
        index = 0
        vocabulaire = {}
        for doc in corpus.id2doc.values():
            texte = Utils.nettoyer_texte(doc.texte)
            mots = doc.texte.lower().split()
            for mot in mots:
                if mot not in vocabulaire:
                    vocabulaire[mot] = index
                    index += 1
        return vocabulaire
    
   
    
    @staticmethod
    def load(path):
        """
        @brief Charge un corpus à partir d'un fichier pickle.
        @param path Chemin du fichier de sauvegarde.
        @return Instance de Corpus chargée.
        """
        with open(path, 'rb') as f:
            return pickle.load(f)
    
     
    @staticmethod
    def extraire_extrait(texte, mot_cle, taille_contexte=10):
        """
        @brief Extrait un passage d'un texte autour d'un mot-clé.
        @param texte Texte source.
        @param mot_cle Mot-clé à rechercher.
        @param taille_contexte Nombre de mots autour du mot-clé à inclure dans l'extrait.
        @return Extrait contenant le mot-clé et son contexte.
        """
        # Nettoyer le texte pour éviter les problèmes de casse
        mots = texte.lower().split()
        mot_cle = mot_cle.lower()

        # Expression régulière pour capturer le mot-clé avec 10 mots avant et après
        pattern = r'(\b\w+\b\s*){0,' + str(15) + r'}' + re.escape(mot_cle) + r'(\s*\b\w+\b){0,' + str(15) + r'}'
        
        matches = re.finditer(pattern, texte, re.MULTILINE)
        
        for matchNum, match in enumerate(matches, start=1):
            if match:
                return match.group()  # Retourne l'extrait complet (mot-clé + contexte)
        return "Extrait non disponible"
    
