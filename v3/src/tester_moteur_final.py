import os
import pickle
from src.CorpusSingleton import CorpusSingleton
from src.SearchEngine import SearchEngine
from dotenv import load_dotenv
import pandas as pd

# ============================================
# CONFIGURATION
# ============================================
DATA_DIR = "../data3"
load_dotenv()

# ============================================
# CHARGEMENT DU CORPUS ET DES MATRICES
# ============================================
def charger_corpus_et_matrices(corpus_name):
    """
    Charge le corpus et les matrices TF/TFxIDF depuis les fichiers pkl.
    """
    chemin_corpus = os.path.join(DATA_DIR, f"corpus_{corpus_name}.pkl")
    chemin_TF = os.path.join(DATA_DIR, f"matrice_TF_{corpus_name}.pkl")
    chemin_TFxIDF = os.path.join(DATA_DIR, f"matrice_TFxIDF_{corpus_name}.pkl")

    # Charger le corpus
    if os.path.exists(chemin_corpus):
        print(f"📂 Chargement du corpus existant : {corpus_name}")
        corpus = CorpusSingleton(corpus_name).load(chemin_corpus)
    else:
        print(f"❌ Corpus introuvable : {chemin_corpus}")
        return None, None, None
    
    # Charger les matrices TF et TFxIDF
    if os.path.exists(chemin_TF) and os.path.exists(chemin_TFxIDF):
        with open(chemin_TF, 'rb') as f:
            mat_TF = pickle.load(f)
        with open(chemin_TFxIDF, 'rb') as f:
            mat_TFxIDF = pickle.load(f)
        print(f"📊 Matrices chargées pour : {corpus_name}")
    else:
        print(f"❌ Matrices non trouvées pour : {corpus_name}")
        return None, None, None

    return corpus, mat_TF, mat_TFxIDF

# ============================================
# TEST DU MOTEUR DE RECHERCHE
# ============================================
def tester_moteur_recherche(corpus_name, mots_cles, n_resultats=20):
    """
    Teste le moteur de recherche avec des mots-clés donnés.
    """
    corpus, mat_TF, mat_TFxIDF = charger_corpus_et_matrices(corpus_name)

    if corpus is None:
        print("❌ Impossible de continuer : Corpus manquant.")
        return
    
    moteur = SearchEngine(corpus)
    moteur.matrice.mat_TF = mat_TF
    moteur.matrice.mat_TFxIDF = mat_TFxIDF
    
    print(f"🔍 Recherche pour : '{mots_cles}'")
    resultats = moteur.search(mots_cles, n_resultats)

    if not resultats.empty:
        print("\n📋 Résultats de la recherche :")
        for index, row in resultats.iterrows():
            print(f"🔹 {index + 1}. {row['Titre']}")
            print(f"    Auteur : {row['URL']}")
            print(f"    Score : {row['Score']:.2f}")
            print(f"    Extrait : {row['Extrait']}\n")
    else:
        print("⚠️ Aucun résultat trouvé.")

# ============================================
# CHOIX DU CORPUS ET RECHERCHE
# ============================================
if __name__ == "__main__":
    
    boucle = True
    print("🛠️ Test du moteur de recherche avec des corpus existants.")
    
    while boucle:
        choix = input("Choisissez le corpus (1 = Discours, 2 = Reddit/Arxiv) : ")
        
        if choix == "1":
            corpus_name = "discours"
        elif choix == "2":
            theme = input("Entrez le nom du corpus reddit/arxiv (ex: politics) : ")
            corpus_name = theme.replace(" ", "")
        else:
            print("❌ Choix invalide.")
            continue

        while True:
            mot_cle = input("\n🔍 Entrez les mots-clés (ou appuyez sur Entrée pour quitter) : ")
            
            if not mot_cle.strip():
                print("👋 Fin de la recherche.")
                boucle = False
                break
            
            try:
                n_resultats = int(input("Nombre de résultats à afficher (1-100, par défaut 10) : ") or 10)
                n_resultats = max(1, min(n_resultats, 100))  # Limite entre 1 et 100
            except ValueError:
                print("⚠️ Entrez un nombre valide.")
                continue

            tester_moteur_recherche(corpus_name, mot_cle, n_resultats)
