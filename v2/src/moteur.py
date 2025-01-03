import os
import pickle
from src.CorpusSingleton import CorpusSingleton
from src.SearchEngine import SearchEngine
from dotenv import load_dotenv
from src.constantes import *
import pandas as pd
from CorpusMatrixManager import CorpusMatrixManager
# ============================================================
# CONFIGURATION
# ============================================================
#pd.set_option('display.max_colwidth', None)
DATA_DIR = "../data1"
load_dotenv()

# ============================================================
# CHARGEMENT DU CORPUS ET DES MATRICES
# ============================================================
def charger_corpus_et_matrices(corpus_name):
    """
    Charge le corpus, les matrices TF/TFxIDF et le vocabulaire depuis le disque.
    """
    # Définir les chemins de sauvegarde
    chemin_corpus = os.path.join(DATA_DIR, f"corpus_{corpus_name}.pkl")
    chemin_TF = os.path.join(DATA_DIR, f"matrice_TF_{corpus_name}.pkl")
    chemin_TFxIDF = os.path.join(DATA_DIR, f"matrice_TFxIDF_{corpus_name}.pkl")

    # Charger le corpus
    if os.path.exists(chemin_corpus):
        print(f"📂 Chargement du corpus existant : {corpus_name}")
        corpus = CorpusSingleton(corpus_name).load(chemin_corpus)
        print(f"corpus  {corpus_name} chargé !!")
    else:
        print(f"❌ Corpus introuvable : {chemin_corpus}")
        return None, None, None
    
    # Charger les matrices TF et TFxIDF
    if os.path.exists(chemin_TF) and os.path.exists(chemin_TFxIDF):
        with open(chemin_TF, 'rb') as f:
            mat_TF = pickle.load(f)
        with open(chemin_TFxIDF, 'rb') as f:
            mat_TFxIDF = pickle.load(f)
        print(f"📊 Matrices chargées pour le corpus : {corpus_name}")
    else:
        print("❌ Matrices non trouvées. Veuillez exécuter 'construire_matrices.py' avant de tester.")
        return None, None, None

    return corpus, mat_TF, mat_TFxIDF


# ============================================================
# TEST DU MOTEUR DE RECHERCHE
# ============================================================
def tester_moteur_recherche(corpus_name, mots_cles, n_resultats=20):
    """
    Teste le moteur de recherche avec des mots-clés donnés.
    """
    # Charger le corpus et les matrices
    corpus, mat_TF, mat_TFxIDF = charger_corpus_et_matrices(corpus_name)

    if corpus is None:
        print("❌ Impossible de continuer : Corpus manquant.")
        return
    
    # Initialiser le moteur de recherche
    moteur = SearchEngine(corpus)
    moteur.matrice.mat_TF = mat_TF
    moteur.matrice.mat_TFxIDF = mat_TFxIDF
    
    
    # Exécuter la recherche
    print(f"🔍 Recherche pour : '{mots_cles}'")
    resultats = moteur.search(mots_cles, n_resultats)

    # Afficher les résultats
    if not resultats.empty:
        print("\n📋 Résultats de la recherche :")
        # Afficher quelques mots du vocab
        print(list(moteur.matrice.vocab.items())[:50])

        print(resultats)
    else:
        print("⚠️ Aucun résultat trouvé.")


# ============================================================
# CHOIX DU CORPUS
# ============================================================
if __name__ == "__main__":
    boucle = True
    print("🛠️ Test du moteur de recherche avec des corpus existants.")

    # Demander le nom du corpus
    corpus_name = input("\n📂 Entrez le nom du corpus à utiliser (par défaut 'mon_corpus') : ") or "mon_corpus"
    
    while boucle:
        mot_cle = input("\n🔍 Entrez les mots-clés de recherche (ou appuyez sur Entrée pour quitter) : ")
        
        # Sortie du programme si aucun mot-clé n'est saisi
        if not mot_cle.strip():
            print("👋 Fin de la recherche. À bientôt !")
            boucle = False
            break  # Sort de la boucle interne
        
        # Nombre de résultats avec une valeur par défaut (10)
        try:
            n_resultats = int(input("Combien de résultats souhaitez-vous afficher ? (1-100, par défaut 10) : ") or 10)
            n_resultats = min(max(n_resultats, 1), 100)  # Assure que n_resultats est entre 1 et 100
        except ValueError:
            print("⚠️ Veuillez entrer un nombre valide.")
            continue  # Reboucle si la saisie est incorrecte

        print("\n🔑 Mot clé principal :", mot_cle)
        tester_moteur_recherche(corpus_name, mot_cle, n_resultats)

