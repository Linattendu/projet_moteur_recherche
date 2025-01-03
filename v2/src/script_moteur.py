import os
import pickle
from src.CorpusSingleton import CorpusSingleton
from src.SearchEngine import SearchEngine
from dotenv import load_dotenv
from src.CorpusMatrixManager1 import CorpusMatrixManager1

DATA_DIR_PKL = "../data100"
load_dotenv()

def charger_corpus_et_matrices(nom_corpus):
    """
    Charge le corpus et les matrices TF/TFxIDF pour un corpus donné.
    """
    chemin_corpus = os.path.join(DATA_DIR_PKL, f"corpus_{nom_corpus}.pkl")
    chemin_TF = os.path.join(DATA_DIR_PKL, f"matriceTF_{nom_corpus}.pkl")
    chemin_TFxIDF = os.path.join(DATA_DIR_PKL, f"matriceTFIDF_{nom_corpus}.pkl")

    if not os.path.exists(chemin_corpus):
        print(f"Corpus introuvable : {chemin_corpus}")
        return None, None, None
    
    # Charger le corpus
    print(f"Chargement du corpus : {nom_corpus}")
    corpus = CorpusSingleton(nom_corpus).load(chemin_corpus)
    
    # Charger les matrices
    if os.path.exists(chemin_TF) and os.path.exists(chemin_TFxIDF):
        with open(chemin_TF, 'rb') as f:
            mat_TF = pickle.load(f)
        with open(chemin_TFxIDF, 'rb') as f:
            mat_TFxIDF = pickle.load(f)
        print(f"Matrices chargées pour : {nom_corpus}")
    else:
        print("❌ Matrices non trouvées. Reconstruisez-les.")
        return None, None, None

    return corpus, mat_TF, mat_TFxIDF


def tester_moteur_recherche(nom_corpus, mots_cles, n_resultats=10):
    """
    Teste le moteur de recherche avec un corpus donné.
    """
    corpus, mat_TF, mat_TFxIDF = charger_corpus_et_matrices(nom_corpus)

    if corpus is None:
        print("Impossible de continuer : Corpus manquant.")
        return
    
    moteur = SearchEngine(corpus)
    moteur.matrice.mat_TF = mat_TF
    moteur.matrice.mat_TFxIDF = mat_TFxIDF
    
    print(f"🔍 Recherche pour : '{mots_cles}'")
    resultats = moteur.search(mots_cles, n_resultats)

    if not resultats.empty:
        print("\nRésultats de la recherche :")
        print(resultats[['Titre', 'Auteur', 'Score']])
    else:
        print("⚠️ Aucun résultat trouvé.")


if __name__ == "__main__":
    manager = CorpusMatrixManager1()
    
    print("🛠️ Test du moteur de recherche (Reddit/Arxiv).")
    
    theme = input("Entrez le thème du corpus à créer (ex : politics, science, technology) : ")
    theme = theme.replace(" ", "").lower()
    nom_corpus = f"RedditArxiv{theme}"
    
    # Créer le corpus
    print(f"Création du corpus pour le thème : {theme}")
    manager.creer_corpus_reddit_arxiv(theme)

    while True:
        mot_cle = input("\n🔍 Entrez les mots-clés de recherche (ou appuyez sur Entrée pour quitter) : ")
        if not mot_cle.strip():
            print("Fin du test.")
            break
        
        try:
            n_resultats = int(input("Nombre de résultats souhaités (1-50, par défaut 10) : ") or 10)
            n_resultats = min(max(n_resultats, 1), 50)
        except ValueError:
            print("Veuillez entrer un nombre valide.")
            continue
        
        tester_moteur_recherche(nom_corpus, mot_cle, n_resultats)
