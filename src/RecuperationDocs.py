import praw
import urllib.request
import xmltodict
from datetime import datetime
from src.Document import DocumentFactory
from src.constantes import *

"""
@file RecuperationDocs.py
@brief Scraping des données à partir de Reddit et Arxiv.

@details
Ce fichier contient deux classes principales :
- RedditScrap : Pour extraire des posts depuis Reddit.
- ArxivScrap : Pour récupérer des articles scientifiques depuis Arxiv.

Les résultats sont ajoutés au corpus de documents.
Les erreurs sont gérées et loguées via GestionErreurs.
"""
class RedditScrap:
    """
    @brief Classe pour le scraping de données depuis Reddit.

    @details
    Cette classe utilise la bibliothèque PRAW (Python Reddit API Wrapper) pour
    interagir avec l'API de Reddit. Les posts sont récupérés par différentes sections :
    - hot : Tendances actuelles.
    - new : Posts les plus récents.
    - top : Posts les mieux notés.
    - rising : Posts gagnant en popularité.
    """
    def __init__(self,corpus, erreur):
        """
        @brief Initialise la classe RedditScrap.
        @param corpus Instance de CorpusSingleton pour stocker les documents récupérés.
        @param erreur Instance de GestionErreurs pour gérer les erreurs pendant le scraping.
        """
                
        # créer une instance Reddit en lecture seule qui représente la connexion à l'API de Reddit
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=USER_AGENT
        )
        self.corpus = corpus
        self.erreur = erreur
        
    
    def chercher_section_hot(self, nom_communaute_reddit, limit):
        """
        @brief Récupère les posts populaires (hot) d'une communauté Reddit.
        @param nom_communaute_reddit Nom de la communauté (subreddit).
        @param limit Nombre maximal de posts à récupérer.
        @return Générateur de posts Reddit.
        """
        return nom_communaute_reddit.hot(limit=limit)
    
  
    def chercher_section_new(self, nom_communaute_reddit, limit):
        """
        @brief Récupère les posts les plus récents (new).
        @param nom_communaute_reddit Nom de la communauté (subreddit).
        @param limit Nombre maximal de posts à récupérer.
        @return Générateur de posts Reddit.
        """
        return nom_communaute_reddit.new(limit=limit)
    
   
    def chercher_section_top(self, nom_communaute_reddit, limit):
        """
        @brief Récupère les posts les mieux notés (top).
        @param nom_communaute_reddit Nom de la communauté (subreddit).
        @param limit Nombre maximal de posts à récupérer.
        @return Générateur de posts Reddit.
        """
        return nom_communaute_reddit.top(limit=limit)

  
    def chercher_section_rising(self, nom_communaute_reddit, limit):
        """
        @brief Récupère les posts en montée de popularité (rising).
        @param nom_communaute_reddit Nom de la communauté (subreddit).
        @param limit Nombre maximal de posts à récupérer.
        @return Générateur de posts Reddit.
        """
        return nom_communaute_reddit.rising(limit=limit)

    
    def recuperer_posts(self, nom_communaute_reddit, limit=20):
        """
        @brief Récupère et ajoute les posts Reddit d'une communauté donnée au corpus.
        @param nom_communaute_reddit Nom de la communauté Reddit.
        @param limit Nombre maximal de posts à récupérer par section.
        @details
        Les posts sont récupérés par section (hot, new, top, rising). En cas d'erreur,
        elle est loguée et continue pour les autres sections.
        """
        # Liste des méthodes à exécuter
        liste_methodes = [
            (self.chercher_section_hot, 'hot'),
            (self.chercher_section_new, 'new'),
            (self.chercher_section_top, 'top'),
            (self.chercher_section_rising, 'rising')
        ]
                       
        try : 
            
            # Parcourir chaque méthode
            for methode, section in liste_methodes:
                
                # reddit n'accepete pas les mots composés avec des espaces
                nom_communaute_reddit= nom_communaute_reddit.replace(" ", "")  
                # Accèder à la communauté r/nom_communaute_reddit
                objet_subreddit = self.reddit.subreddit(nom_communaute_reddit)
                
                # Récuperer les posts par la méthode correspondante  
                posts = methode(objet_subreddit, limit)                                               
                for post in posts:
                    if post.selftext:
                        texte = post.selftext.replace('\n', ' ')
                        print(texte)
                        
                        # Créer un document Reddit
                        doc = DocumentFactory.creer_document(
                            "Reddit",
                            post.title,
                            str(post.author),
                            datetime.fromtimestamp(post.created_utc),
                            post.url,
                            texte,
                            post.num_comments
                        )
                        # Ajouter au corpus
                        self.corpus.ajouter_document(doc)
                        print("doc reddit ", doc)
                    else:
                        print("pas de post")
        
        except Exception as e:
            self.erreur.afficher_erreurs(e,context=f"Subreddit: {nom_communaute_reddit}, Section: {section}")


class ArxivScrap:
    """
    @brief Classe pour le scraping de données scientifiques depuis Arxiv.

    @details
    Cette classe interroge l'API Arxiv pour récupérer des articles en utilisant urllib et xmltodict.
    """
    def __init__(self, corpus, erreur):
        """
        @brief Initialise la classe ArxivScrap.
        @param corpus Instance de CorpusSingleton pour stocker les articles récupérés.
        @param erreur Instance de GestionErreurs pour gérer les erreurs de scraping.
        """
        self.base_url = URL_ARXIV
        self.corpus = corpus
        self.erreur = erreur

    def recuperer_articles(self, theme, max_results=15):
        """
        @brief Récupère des articles depuis Arxiv en fonction d'un thème donné.
        @param theme Thème de recherche.
        @param max_results Nombre maximum d'articles à récupérer.
        @details
        Interroge l'API Arxiv, parse les résultats en XML, et ajoute les articles au corpus.
        """
        # Encoder une chaîne de caractères en remplaçant les caractères spéciaux par leur équivalent encodé en +.
        theme_nettoye = urllib.parse.quote_plus(theme)
        
        query = f"search_query=all:{theme_nettoye}&start=0&max_results={max_results}"
        url = self.base_url + query
        
        print(f"URL de requête: {url}")  # Débogage: Afficher l'URL de requête
        
        # Bloc try/except pour la requête réseau et le traitement des données
        try:
            
            # Récupérer les articles depuis Arxiv et parser en une seule fois
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                print(f"Données brutes: {data}")  # Débogage: Afficher les données brutes
                 
                parsed_data = xmltodict.parse(data)
                print(f"Données parsées: {parsed_data}")  # Débogage: Afficher les données parsées
                
            # Extraire les articles (entrée unique ou liste)
            entries = parsed_data['feed'].get('entry', [])
            print(f"Entrées: {entries}")  # Débogage: Afficher les entrées
            
            if isinstance(entries, dict):
                entries = [entries]

            # Traiter chaque article
            for entry in entries:
                texte = entry['summary'].replace('\n', ' ')
                auteurs = entry.get('author', [])
                
                print(f"Texte: {texte}")  # Débogage: Afficher le texte de l'article
                print(f"Auteurs: {auteurs}")  # Débogage: Afficher les auteurs
                
                # Extraire l'auteur principal
                if isinstance(auteurs, list):
                    auteur_nom = ', '.join(a['name'] for a in auteurs if isinstance(a, dict) and 'name' in a)
                else:
                    auteur_nom = auteurs.get('name', 'Inconnu')

                print(f"Auteur principal: {auteur_nom}")  # Débogage: Afficher l'auteur principal
                
               # Extraire les co-auteurs
                co_auteurs = []
                print(f"Auteurs bruts: {auteurs}")  # Débogage: Afficher les auteurs bruts

                if isinstance(auteurs, list):
                    for auteur in auteurs:
                        if isinstance(auteur, dict) and 'name' in auteur:
                            co_auteurs.append(auteur['name'])
                        else:
                            print(f"Auteur non valide: {auteur}")  # Débogage: Afficher les auteurs non valides
                elif isinstance(auteurs, dict):
                    if 'name' in auteurs:
                        co_auteurs.append(auteurs['name'])
                    else:
                        print(f"Auteur non valide: {auteurs}")  # Débogage: Afficher les auteurs non valides
                elif isinstance(auteurs, str):
                    co_auteurs.append(auteurs)
                else:
                    co_auteurs = ["Inconnu"]
                    print(f"Type d'auteur non pris en charge: {type(auteurs)}")  # Débogage: Afficher le type d'auteur non pris en charge

                print(f"Co-auteurs: {co_auteurs}")  # Débogage: Afficher les co-auteurs

                
                # Créer un document Arxiv
                doc = DocumentFactory.creer_document(
                    "Arxiv",
                    entry.get('title', 'Sans titre'),
                    auteur_nom,
                    datetime.now(),
                    entry.get('id', 'N/A'),
                    texte,
                    co_auteurs
                )
                print(f"Document créé: {doc}")  # Débogage: Afficher le document créé
                
                # Ajouter au corpus
                self.corpus.ajouter_document(doc)
            
        except urllib.error.URLError as e:
            # Erreur réseau (URL inaccessible)
            self.erreur.afficher_erreurs(e, context=f"Erreur réseau - URL : {url}")
        
        except xmltodict.expat.ExpatError as e:
            # Erreur lors du parsing XML (mauvais format)
            self.erreur.afficher_erreurs(e, context=f"Erreur de parsing XML - Thème : {theme}")
        
        except Exception as e:
            # Gestion des erreurs générales
            self.erreur.afficher_erreurs(e, context=f"Erreur générale - Thème : {theme}")
                