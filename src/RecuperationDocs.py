import praw
import urllib.request
import xmltodict
from datetime import datetime
from src.Document import DocumentFactory
from src.CorpusSingleton import CorpusSingleton

REDDIT_CLIENT_ID = "JEORY8A_0ZUmlz97oTwuwQ"
REDDIT_CLIENT_SECRET = "fslpV3GIVfA0S3Vh9A7Hs81NRoABvw"
USER_AGENT = "source"
URL_ARXIV = 'http://export.arxiv.org/api/query?'


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
    @brief Classe pour le scraping de données depuis Reddit avec pagination.
    """

    def __init__(self, corpus, erreur):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=USER_AGENT
        )
        self.corpus = corpus
        self.erreur = erreur


    def recuperer_posts(self, theme, limit=10):
        """
        @brief Récupère les posts récents et les commentaires associés pour compléter les textes vides.
        """
        try:
            theme = theme.replace(" ", "")
            subreddit = self.reddit.subreddit(theme)
            print("theme recuperer_posts : ", theme)
            
            # Récupérer les posts récents
            posts = subreddit.new(limit=limit)
            
            for post in posts:
                texte = post.selftext  # Texte du post
                commentaire_concatene = ""

                # Si le texte est vide, récupérer les commentaires associés
                if not texte:
                    post.comments.replace_more(limit=0)  # Pas de "More comments"
                    commentaires = post.comments.list()
                    commentaire_concatene = " ".join([comment.body for comment in commentaires if comment.body])
                    texte = commentaire_concatene if commentaire_concatene else "Pas de texte disponible."
                
                # Utiliser l'URL du post Reddit (permalink)
                url_post = f"https://www.reddit.com{post.permalink}"
                
                # Créer un document Reddit avec le texte ou les commentaires
                doc = DocumentFactory.creer_document(
                    type_doc="Reddit",
                    titre=post.title,
                    auteur= str(post.author),
                    date=datetime.fromtimestamp(post.created_utc),
                    url=url_post,
                    texte=texte,
                    theme=self.corpus.theme,
                    extra=post.num_comments
                    )

                self.corpus.ajouter_document(doc)
        except Exception as e:
            self.erreur.afficher_erreurs(e, context=f"Subreddit: {theme}")


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

    def recuperer_articles(self, theme, max_results=10):
        """
        @brief Récupère des articles depuis Arxiv en fonction d'un thème donné.
        @param theme Thème de recherche.
        @param max_results Nombre maximum d'articles à récupérer.
        @details
        Interroge l'API Arxiv, parse les résultats en XML, et ajoute les articles au corpus.
        """
        theme_nettoye = urllib.parse.quote_plus(theme)
        print("theme + netttoye recuperer_articles : ", theme, theme_nettoye)
        
        query = f"search_query=all:{theme_nettoye}&start=0&max_results={max_results}"
        url = self.base_url + query
        
        # Bloc try/except pour la requête réseau et le traitement des données
        try:
            
            # Récupérer les articles depuis Arxiv et parser en une seule fois
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                parsed_data = xmltodict.parse(data)
                
            # Extraire les articles (entrée unique ou liste)
            entries = parsed_data['feed'].get('entry', [])
            
            if isinstance(entries, dict):
                entries = [entries]

            # Traiter chaque article
            for entry in entries:
                texte = entry['summary'].replace('\n', ' ')
                auteurs = entry.get('author', [])
                
                 # Extraire l'auteur principal
                if isinstance(auteurs, list):
                    auteur_nom = ', '.join(a['name'] for a in auteurs if isinstance(a, dict) and 'name' in a)
                else:
                    auteur_nom = auteurs.get('name', 'Inconnu')

               # Extraire les co-auteurs
                co_auteurs = []

                if isinstance(auteurs, list):
                    for auteur in auteurs:
                        if isinstance(auteur, dict) and 'name' in auteur:
                            co_auteurs.append(auteur['name'])
                        else:
                            print(f"Auteur non valide: {auteur}")
                elif isinstance(auteurs, dict):
                    if 'name' in auteurs:
                        co_auteurs.append(auteurs['name'])
                    else:
                        print(f"Auteur non valide: {auteurs}")
                elif isinstance(auteurs, str):
                    co_auteurs.append(auteurs)
                else:
                    co_auteurs = ["Inconnu"]
                    print(f"Type d'auteur non pris en charge: {type(auteurs)}")  # Débogage: Afficher le type d'auteur non pris en charge

                
                # Créer un document Arxiv
                doc = DocumentFactory.creer_document(
                    "Arxiv",
                    entry.get('title', 'Sans titre'),
                    auteur_nom,
                    datetime.now(),
                    entry.get('id', 'N/A'),
                    texte,
                    theme,
                    co_auteurs
                )
                print(f"Document Arxiv créé: {doc}")

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
