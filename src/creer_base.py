from src.CorpusMatrixManager import CorpusMatrixManager

def main():
    manager = CorpusMatrixManager()

    print("Lancement du processus de création des corpus...")

    
    manager.creer_corpus_discours()
    manager.creer_corpus_reddit_arxiv()

    reponse = input("Voulez-vous stocker les PKL dans la base de données ? (o/n) : ")
    if reponse.lower() == "o":
        manager.stocker_en_base_de_donnees()
        print("📂 Stockage terminé.")
    else:
        print("🔔 Stockage annulé.")

    manager.fermer_connexion()

if __name__ == "__main__":
    main()
