# Fichier SearchEngine.py

import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from scipy.linalg import norm

from src.Corpus import Corpus
from src.MatriceDocuments import MatriceDocuments 
from src.Utils import Utils
#pd.set_option('display.max_colwidth', None)
import re
#pd.set_option('display.max_colwidth', None)

class SearchEngine:
    """
    @brief Moteur de recherche utilisant des matrices TF et TFxIDF pour effectuer des recherches par mots-clés.
    """

    def __init__(self, corpus):
        """
        @brief Initialise le moteur de recherche avec un corpus.
        @param corpus Instance de la classe Corpus.
        """
        self.corpus = corpus
        self.matrice = MatriceDocuments(corpus)
        self.matrice.construire_matrice_TF()
        self.matrice.construire_matrice_TFxIDF()
        #self.vocab = Utils.dictionnaire_vocab(self.corpus) # Construire et synchroniser le vocabulaire
        #self.matrice.vocab = self.vocab  # Transmettre le vocabulaire à MatriceDocuments
            

    def search(self, mots_cles, n_resultats=50):
        """
        @brief Recherche des documents correspondant aux mots-clés donnés.
        @param mots_cles Requête utilisateur (chaîne de caractères).
        @param n_resultats Nombre de documents à retourner.
        @return DataFrame avec les résultats triés par pertinence.
        """
        
        if self.matrice.mat_TFxIDF is None:
            raise ValueError("La matrice TFxIDF n'a pas été construite.")
    
        # Convertir la matrice TFxIDF en csr_matrix pour permettre l'indexation par ligne
        mat_TFxIDF_csr = self.matrice.mat_TFxIDF.tocsr()

        # Transformer la requête
        vecteur_requete = self.matrice.vecteur_aligne_matrice(mots_cles)
             
        scores = []
        for doc_id, doc in enumerate(self.corpus.id2doc.values()):
            vecteur_doc = mat_TFxIDF_csr[doc_id].toarray().flatten()          

            # Si vecteur_doc est vide, crée un vecteur de 0
            if vecteur_doc.shape[0] == 0:
                vecteur_doc = np.zeros_like(vecteur_requete)
            
            # Vérification des normes (éviter les divisions par zéro)
            if norm(vecteur_requete) == 0 or norm(vecteur_doc) == 0:
                score = 0  # Aucun mot en commun, score nul
            else:
                score = 1 - cosine(vecteur_requete, vecteur_doc)
            
           
            txt = self.extraire_extrait(doc.texte, mots_cles, taille_contexte=10)
            
            scores.append((doc.titre, doc.auteur, txt, doc.url, score))
        
        # Trier par score décroissant
        scores = sorted(scores, key=lambda x: x[4], reverse=True)
        
        # Créer un DataFrame avec les résultats
        #resultats = pd.DataFrame(scores[:n_resultats], columns=["Titre", "URL", "Score"])
        resultats = pd.DataFrame([
            (titre,auteur, txt, url, score) for (titre,auteur, txt,  url, score) in scores[:n_resultats]
            if (url.startswith("https://www.reddit.com/r/") or url.startswith("http://arxiv.org")) and score > 0
        ], columns=["Titre", "auteur", "contenu", "URL", "Score"])
        
        return resultats
    
    @staticmethod
    def extraire_extrait(texte, mot_cle, taille_contexte=15):
        # 1. Nettoyage et préparation du texte
        texte = texte.lower()
        mot_cle = mot_cle.lower()
        
        
        
        # 2. Expression régulière pour capturer le mot-clé avec 10 mots avant et après
        pattern = r'(\b\w+\b\s*){0,' + str(5) + r'}' + re.escape(mot_cle) + r'(\s*\b\w+\b){0,' + str(5) + r'}'
        
        matches = re.finditer(pattern, texte, re.MULTILINE)
        
        for matchNum, match in enumerate(matches, start=1):
            if match:
                return match.group()  # Retourne l'extrait complet (mot-clé + contexte)
                return "Extrait non disponible"

        

# ===========================
# Exemple d'utilisation (Test)
# ===========================
if __name__ == "__main__":
    from src.Document import Document
    
    # Créer un corpus simple
    corpus = Corpus("Test Corpus")
    doc1 = Document("Doc1", "Alice", "2024-01-01", "url1", "Python is great")
    doc2 = Document("Doc2", "Bob", "2024-01-02", "url2", "Python for machine learning")
    doc3 = Document("Doc3", "Charlie", "2024-01-03", "url3", "Python is used in IA")
    doc4 = Document("Doc4", "David", "2024-01-05", "url4", "IA transformes Python for data science")
    
    ajout_doc1 = corpus.ajouter_document(doc1)
    ajout_doc2 = corpus.ajouter_document(doc2)
    ajout_doc3 = corpus.ajouter_document(doc3)
    ajout_doc4 = corpus.ajouter_document(doc4)

    print(ajout_doc1, ajout_doc2,ajout_doc3,ajout_doc4)
    # Créer et tester le moteur de recherche
    moteur = SearchEngine(corpus)
    resultats = moteur.search("Python", n_resultats=4)
    print(resultats)
    
    ''' 
    resultat :
    Titre   URL     Score
    0  Doc3  url3  0.571617
    1  Doc1  url1  0.175428
    2  Doc2  url2  0.122345
    '''

