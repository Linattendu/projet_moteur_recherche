import logging
import praw

"""
@file GestionErreurs.py
@brief Classe pour la gestion centralisée des erreurs dans l'application.

@details
Cette classe :
- Capture et gère toutes les erreurs de l'application.
- Centralise la logique de gestion des exceptions.
- Permet de loguer les erreurs ou d'effectuer des actions personnalisées (par exemple, relancer certaines tâches ou envoyer des notifications).
- S'intègre facilement dans toutes les parties du code (RecuperationDocs, Document, etc.).

Elle utilise la bibliothèque standard logging pour écrire les erreurs dans un fichier de log.
"""

class GestionErreurs:
    """
    @brief Classe de gestion des erreurs.

    @details
    Cette classe configure un logger pour capturer et enregistrer les erreurs dans un fichier log.
    Elle permet une gestion simple et cohérente des erreurs dans toute l'application.
    """
    def __init__(self, log_file="errors.log"):
        """
        @brief Initialise le logger pour la gestion des erreurs.
        @param log_file Chemin du fichier de log pour l'enregistrement des erreurs.
        """
        # Configuration du logger
        logging.basicConfig(
            filename=log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def afficher_erreurs(self, exception, context=""):
        """
        @brief Capture et enregistre une erreur dans le fichier de log.
        @param exception Instance de l'exception capturée.
        @param context Contexte supplémentaire pour identifier l'erreur (facultatif).
        @details
        Cette méthode prend en charge plusieurs types d'erreurs :
        - Erreurs PRAW (liées à Reddit).
        - Erreurs d'attribut (AttributeError).
        - Erreurs de valeur (ValueError).
        - Autres erreurs génériques.
        
        Enregistre les détails de l'erreur dans le fichier log et affiche l'erreur dans la console.
        """
               
        error_message = f"{type(exception).__name__}: {exception} | Contexte : {context}"
        
        # Log selon le type d'erreur
        if isinstance(exception, praw.exceptions.PRAWException):
            self.logger.error(f"Erreur Reddit (PRAW) : {error_message}")
        elif isinstance(exception, AttributeError):
            self.logger.error(f"Erreur d'attribut : {error_message}")
        elif isinstance(exception, ValueError):
            self.logger.error(f"Erreur de valeur : {error_message}")
        else:
            self.logger.error(f"Erreur inconnue : {error_message}")

