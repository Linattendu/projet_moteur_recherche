# MatricDocuments.py

import numpy as np
from scipy.sparse import csr_matrix
from collections import defaultdict
from src.Utils import Utils

class MatriceDocuments:
    """
    @brief Classe pour construire et gérer la matrice Document x Mots (TF et TFxIDF).

    @details
    Cette classe construit une matrice creuse (sparse matrix) représentant la fréquence des termes (TF)
    pour chaque document du corpus. La classe peut également calculer la version TFxIDF.
    """
    def __init__(self, corpus):
        """
        @brief Initialise la classe avec un corpus de documents.
        @param corpus Instance de la classe Corpus.
        """
        self.corpus = corpus
        self.vocab = {}  # Dictionnaire des mots (clé = mot, valeur = index)
        self.mat_TF = None  # Matrice TF (sparse)
        self.mat_TFxIDF = None
        self.frequence_mot = defaultdict(int)  # Document Frequency (DF) pour TFxIDF
       

    def construire_matrice_TF(self):
        """
        @brief Construit la matrice TF (Term Frequency) sparse pour le corpus.
        
        @details
        Remplit la matrice avec la fréquence des termes pour chaque document.
        Utilise csr_matrix de scipy pour optimiser la gestion de la matrice creuse.
        
        @return Matrice TF (sparse).
        """
        
        rows, cols, data = [], [], []

        # Étape 1 : Construire le vocabulaire à partir des documents (au lieu de `dictionnaire_vocab`)
        self.vocab = Utils.dictionnaire_vocab(self.corpus)

        
        #print("self.vocab ", self.vocab)
        if not self.vocab:
            print("Le vocabulaire est vide après traitement des documents.")
            return None
        
        # Étape 2 : Remplir la matrice TF (Term Frequency)
        for doc_id, doc in enumerate(self.corpus.id2doc.values()): # pour chaque document
            texte = Utils.nettoyer_texte(doc.texte)
            mots = texte.lower().split()
            compteur = defaultdict(int) # initialisation du dico 
            #print("compteur avant ", compteur)

            # construction du compteur à partir des mots du document
            for mot in mots:
                if mot in self.vocab:  # Utiliser le vocabulaire mis à jour
                    compteur[mot] += 1
            #print("compteur apres ", compteur)

            for mot, count in compteur.items():
                rows.append(doc_id) # indice de chaque document
                cols.append(self.vocab[mot])  # Index du mot dans le vocabulaire
                data.append(count)
                self.frequence_mot[mot] += 1  # Fréquence du mot dans le corpus
        
        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(len(self.corpus.id2doc), len(self.vocab)))
        #print("self.mat_TF  ",self.mat_TF  )
        return self.mat_TF


    def construire_matrice_TFxIDF(self):
        """
        @brief Construit la matrice TFxIDF à partir de la matrice TF existante.
        
        @details
        Applique la pondération IDF (Inverse Document Frequency) pour ajuster la matrice TF.
        """
        if self.mat_TF is None:
            raise ValueError("La matrice TF doit être construite avant TFxIDF.")

        n_docs = len(self.corpus.id2doc)
        idf = np.log((n_docs + 1) / (np.array([self.frequence_mot[mot] for mot in self.vocab]) + 1)) + 1
        self.mat_TFxIDF = self.mat_TF.multiply(idf)
    
        return self.mat_TFxIDF
    
    def vecteur_aligne_matrice(self, mots_cles):
        """
        Transforme une requête utilisateur en vecteur aligné avec la matrice TFxIDF.
        """
        mat_TFxIDF = self.construire_matrice_TFxIDF()
        
        vecteur_requete = np.zeros(len(self.vocab))
        #print("vecteur_requete : ", vecteur_requete)
        mots = mots_cles.lower().split()
        
        for mot in mots:
            if mot in self.vocab:
                vecteur_requete[self.vocab[mot]] += 1  # Incrémenter seulement si le mot existe
            else:
                print(f"Mot non trouvé dans le vocabulaire : {mot}")

        # Appliquer la pondération IDF pour les mots du vocabulaire existant
        for mot, index in self.vocab.items():
            if vecteur_requete[index] > 0:
                vecteur_requete[index] *= np.log((len(self.corpus.id2doc) + 1) / (1 + self.frequence_mot[mot])) + 1

        #print("vecteur_requete : ",vecteur_requete)
        return vecteur_requete


    def afficher_matrice(self):
        """
        @brief Affiche la matrice TF sous forme dense (pour visualisation).
        
        @details
        Cette méthode est utile pour le débogage ou la visualisation de petites matrices.
        """
        #print("mat_TF : ", self.mat_TF.toarray())
        #print("matrice_TFxIDF : ",self.mat_TFxIDF.toarray())

# Exemple d'utilisation (Test rapide)
if __name__ == "__main__":
    from src.Corpus import Corpus
    from src.Document import Document
    
    # Créer un petit corpus de test
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

    # Construire la matrice
    matrice = MatriceDocuments(corpus)
    matrice.construire_matrice_TF()
    matrice.construire_matrice_TFxIDF()
    matrice.afficher_matrice()
    
    '''
    resultat : 
    [[1 1 1 0 0 0 0]
    [0 1 0 1 1 0 0]
    [1 0 1 0 0 1 1]] 
    '''