from src.CorpusMatriceManager import CorpusMatriceManager

def main():
    """
    @brief Point d'entrée principal de l'application pour gérer les corpus.
    
    @details 
    - Lance la création des corpus de discours à partir de fichiers CSV.
    - Récupère les données Reddit et Arxiv pour différents thèmes.
    - Propose de stocker les informations des fichiers pickle (PKL) dans la base de données.
    """
    manager = CorpusMatriceManager()

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
    """
    @brief Exécute la fonction principale `main` si le script est lancé directement.
    """
    main()
