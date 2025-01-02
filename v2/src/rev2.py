import os
from dotenv import load_dotenv
from src.CorpusSingleton import CorpusSingleton
from src.RecuperationDocs import RedditScrap, ArxivScrap
from src.GestionErreurs import GestionErreurs
from src.SearchEngine import SearchEngine
from src.constantes import * 




"""
@file rev2.py
@brief Point d'entrée principal pour la version 2 du moteur de recherche.

@details
Cette version introduit la création d'une matrice TFxIDF et la recherche de documents par similarité cosinus.

Classes et Modules Utilisés :
- CorpusSingleton : Gestion du corpus unique de documents (pattern Singleton).
- RedditScrap : Scraping de Reddit.
- ArxivScrap : Scraping d'Arxiv.
- SearchEngine : Construction de la matrice TFxIDF et recherche par mots-clés.
- GestionErreurs : Gestion des erreurs.

Exécution :
    python -m src.rev2

Sortie :
- Affiche les résultats de la recherche à partir d'une requête.
"""

if __name__ == "__main__":
    """
    @brief Point d'entrée de l'application version 2.

    @details
    Cette version met en place le scraping suivi de la recherche par mots-clés 
    avec le moteur de recherche basé sur TFxIDF.
    """
    
    # Charger les variables d'environnement (Reddit API)
    load_dotenv()

    erreur = GestionErreurs(log_file="app_errors.log")
    
    theme = 'medicine'
    # Chemin de sauvegarde dans le dossier 'data'
    dossier_data = "../data1"
    theme_sans_espace= theme.replace(" ", "")
    nom_corpus = f"corpus_{theme_sans_espace}"
    nom_fichier = nom_corpus + ".pkl"
    chemin_sauvegarde = os.path.join(dossier_data, nom_fichier)
    
    corpus = CorpusSingleton(nom_corpus)
    
    # Créer le dossier 'data' s'il n'existe pas
    if not os.path.exists(dossier_data):
        os.makedirs(dossier_data)
    
    # Charger ou créer un nouveau corpus
    if os.path.exists(chemin_sauvegarde):
        print("📂 Chargement du corpus existant...")
        #corpus = CorpusSingleton(nom_corpus=nom_corpus)
        corpus = corpus.load(chemin_sauvegarde)
    else:
        print("📁 Aucune sauvegarde n'est trouvée, téléchargement à nouveau")
        
                
        # Scraping Reddit et Arxiv
        erreur = GestionErreurs(log_file="app_errors.log")
        reddit_scraper = RedditScrap(corpus, erreur)
        reddit_scraper.recuperer_posts(theme, limit=50)

        arxiv_scraper = ArxivScrap(corpus, erreur)
        arxiv_scraper.recuperer_articles(theme, max_results=50)

        # Sauvegarder le corpus
        corpus.save(chemin_sauvegarde)
        print(f"💾 Corpus sauvegardé dans {chemin_sauvegarde}")
    
    # Afficher les documents récupérés
    print(f"Taille du corpus : {len(corpus.id2doc)} documents")
    #for doc in corpus.id2doc:
    #    print(doc)
    
    # statistiques:
    
    
    # Construire le moteur de recherche
    moteur = SearchEngine(corpus)

    # Construire la matrice TFxIDF
    moteur.matrice.construire_matrice_TF()
    moteur.matrice.construire_matrice_TFxIDF()

    # Effectuer une recherche
    #requete = "patients"
    requete = "disease"
    resultats = moteur.search(requete, n_resultats=100)

    # Afficher les résultats
    print(f"\nRésultats de la recherche pour la requête : '{requete}'")
    print(resultats)    
    
    

    
    # theme = 'climate change'
    # requete : "climate"
    '''
    Résultats de la recherche pour la requête : 'climate'
                                                Titre                                                URL     Score
0                 The structure of the climate debate                  http://arxiv.org/abs/1608.05597v1  0.192209
1   Hurricanes Increase Climate Change Conversatio...                  http://arxiv.org/abs/2305.07529v1  0.134954
2   You are right. I am ALARMED -- But by Climate ...                  http://arxiv.org/abs/2004.14907v1  0.128723
3   What shapes climate change perceptions in Afri...                  http://arxiv.org/abs/2105.07867v1  0.107300
4   Financial climate risk: a review of recent adv...                  http://arxiv.org/abs/2404.07331v1  0.101012
5   Trend and Thoughts: Understanding Climate Chan...                  http://arxiv.org/abs/2111.14929v1  0.098732
6   A Climate Change Vulnerability Assessment Fram...                  http://arxiv.org/abs/2108.09762v1  0.097227
7   Climate Change Conspiracy Theories on Social M...                  http://arxiv.org/abs/2107.03318v1  0.090939
8                            Baumol's Climate Disease                  http://arxiv.org/abs/2312.00160v1  0.084403
9                           Climate change journals?   https://www.reddit.com/r/climatechange/comment...  0.075681
10  Indexing and Visualization of Climate Change N...                  http://arxiv.org/abs/2408.01745v1  0.071675
11  Harris win would be a 'big relief' for climate...          https://www.dailymotion.com/video/x976tya  0.068834
12              I hope this is the right place to ask  https://www.reddit.com/r/climatechange/comment...  0.065984
13  Donald Trump’s pick for energy secretary says ...  https://www.theverge.com/2024/11/18/24299573/d...  0.065503
14  $266 Trillion in Climate Spending Is a No-Brai...  https://www.bloomberg.com/opinion/articles/202...  0.055939
15  Trump would be an "Extinction-Level Event" for...  https://www.juancole.com/2024/11/extinction-tu...  0.052749
16  My grandpa sent me this. A lot of Bjorne stats...  https://unherd.com/newsroom/bjorn-lomborg-7-my...  0.049937
17   Data Science applied to Climate Change Solutions  https://www.reddit.com/r/climatechange/comment...  0.037481
18  New study reveals how stray dogs in Chernobyl ...  https://sinhalaguide.com/new-study-reveals-how...  0.034495
19  Billions of crabs went missing around Alaska. ...  https://www.yahoo.com/news/billions-crabs-went...  0.032971 
    '''
    
    
    
    
    
