 # Fichier Utils.py
import re
import unicodedata
import string


class Utils:
    @staticmethod
    def nettoyer_texte(texte):
        """
        Nettoie un texte en supprimant les apostrophes, ponctuations et en mettant en minuscule.

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
        
        """ texte = texte.lower()  # Convertir en minuscule
         # Remplacement spécifique pour ne pas perdre les formes comme L'IA
        texte = re.sub(r"(\b[a-z])'([a-z])", r"\1 \2", texte)  # L'IA -> l ia (sans perte du "ia")

        # Suppression de la ponctuation restante
        texte = re.sub(r"[\.,’]", "", texte)  # Retirer points et virgules
        return texte
        """
        
    @staticmethod
    def concatener_textes(corpus):
        texte_brut = ' '.join(doc.texte for doc in corpus.id2doc.values())
        texte_nettoye = Utils.nettoyer_texte(texte_brut)
        print("✅ Texte concaténé et nettoyé.")
        return texte_nettoye


    @staticmethod
    def dictionnaire_vocab(corpus):
        """
        @brief Construit le dictionnaire de vocabulaire à partir des documents du corpus.
        @details
        Il s'agit d'un dictionnaire des mots présents dans les documents du corpus avec leur index unique.
        Utilisé pour transformer les requêtes (vecteur de recherche).
        """
        index = 0
        vocabulaire = {}
        for doc in corpus.id2doc.values():
            texte = Utils.nettoyer_texte(doc.texte)
            mots = texte.lower().split()
            for mot in mots:
                if mot not in vocabulaire:
                    vocabulaire[mot] = index
                    index += 1
        return vocabulaire
    

    