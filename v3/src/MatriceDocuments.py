# MatriceDocument.pt
import numpy as np
from scipy.sparse import csr_matrix
from collections import defaultdict
from src.Utils import Utils
import pickle
import os
from src.constantes import *


class MatriceDocuments:
    """
    @brief Classe pour construire et gérer la matrice Document x Mots (TF et TFxIDF).
    """

    def __init__(self, corpus):
        """
        Initialise la classe avec un corpus de documents.
        @param corpus Instance de la classe Corpus.
        """
        self.corpus = corpus
        self.mat_TF = None
        self.mat_TFxIDF = None
        self.vocab =  {} # Vocabulaire {mot : {id, freq, len}}
        self.frequence_mot= defaultdict(int)   # Fréquence des mots dans les documents     
        self.construire_vocab_et_matrice_TF()
        self.construire_matrice_TFxIDF()
   
    def construire_vocab_et_matrice_TF(self):
        """
        Construit simultanément le vocabulaire et la matrice TF.
        @return matrice Tf , vocab
        
        """
        rows, cols, data = [], [], []
        index = 0  # Identifiant unique des mots

        # Parcourir chaque document du corpus
        for doc_id, doc in enumerate(self.corpus.id2doc.values()):
            #print(doc)
            texte = Utils.nettoyer_texte(doc.texte)
            mots = texte.lower().split()
            compteur = defaultdict(int)
            #print("mots : ", mots)

            # Construire le vocabulaire et remplir la matrice TF
            for mot in mots:
                
                if mot not in self.vocab:
                    self.vocab[mot] = {
                    'id': index,
                    'freq': 0,
                    'len': len(mot)  # Ajouter la longueur du mot
                    }
                    index += 1
                
                # Compter les occurrences par document
                compteur[mot] += 1
            #print("compteur mots : ", compteur)
            
            # Remplir la matrice TF
            for mot, count in compteur.items():
                rows.append(doc_id)
                cols.append(self.vocab[mot]['id'])
                data.append(count)
                #print("frequence mot : ", self.frequence_mot)
                # Mise à jour de la fréquence globale (document frequency)
                self.frequence_mot[mot] += 1
                self.vocab[mot]['freq'] += count  # Total occurrences dans tout le corpus

        # Créer la matrice creuse (sparse matrix)
        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(len(self.corpus.id2doc), len(self.vocab)))

        # Sauvegarder le vocabulaire
        """ with open(self.chemin_vocab, 'wb') as f:
            pickle.dump(self.vocab, f)
        print(f"Matrice TF construite et vocab sauvegardé ({len(self.vocab)} mots).") """
        
        


    # CONSTRUCTION DE LA MATRICE TFxIDF

    def construire_matrice_TFxIDF(self ):
        """
        Construit la matrice TFxIDF à partir de la matrice TF existante.
        """
        if self.mat_TF is None:
            raise ValueError("La matrice TF doit être construite avant TFxIDF.")

        n_docs = len(self.corpus.id2doc)

        # Calculer l'IDF pour chaque mot du vocabulaire
        idf = np.log((n_docs + 1) / (np.array([self.frequence_mot[mot] for mot in self.vocab]) + 1)) + 1
        
        if self.mat_TF.shape[1] != len(idf):
            print("🚨 Incohérence entre la matrice TF et la taille du vocabulaire.")
            self.construire_vocab_et_matrice_TF()  # Reconstruire la matrice TF
            return self.construire_matrice_TFxIDF()

        # Multiplication de la matrice TF par IDF
        self.mat_TFxIDF = self.mat_TF.multiply(idf)

        print(f"Matrice TFxIDF construite (taille : {self.mat_TFxIDF.shape}).")
        
 
    # AFFICHER MATRICE (DEBUG)
 
    def afficher_matrice(self):
        """
        Affiche les matrices TF et TFxIDF pour débogage.
        """
        if self.mat_TF is not None:
            print("Matrice TF :")
            print(self.mat_TF.toarray())
        if self.mat_TFxIDF is not None:
            print("\nMatrice TFxIDF :")
            print(self.mat_TFxIDF.toarray())
