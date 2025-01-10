# Projet : Moteur de Recherche  

### Version 2 : Moteur de Recherche Avancé

## Description
Cette version **v2** correspond aux fonctionnalités développées dans les TDs 3 à 7. Elle intègre un moteur de recherche avancé basé sur des matrices TF-IDF, permettant une classification thématique et des recherches plus précises dans les corpus.

## Fonctionnalités

### Gestion de Corpus :
- Création de corpus à partir de fichiers CSV ou via des API (Reddit, ArXiv).
- Nettoyage, segmentation, et indexation des textes.
- Génération des matrices TF et TF-IDF.

### Moteur de Recherche :
- Recherche par mots-clés avec gestion des expressions exactes.
- Extraction des passages pertinents contenant les mots recherchés.
- Filtrage des résultats par auteur et période (date de début et de fin).
- Classement des documents en fonction des scores pertinents (TF-IDF).

### Visualisation et Analyse :
- Nuages de mots pour visualiser les thèmes dominants.
- Graphiques d'évolution temporelle des termes recherchés.
- Comparaison des résultats entre différentes sources (Reddit, ArXiv, CSV).

## Installation

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/Linattendu/projet_moteur_recherche.git
   cd projet_moteur_recherche
   
2. **Créer un environnement virtuel et installer les dépendances :**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Linux/Mac ou sur Windows: venv\Scripts\activate   
    pip install -r requirements.txt
    
3. **Utilisation **
Lancer l'application Streamlit :
    ```bash
    Copier le code
    streamlit run app.py
    
Vous pouvez accéder à l'interface utilisateur via un navigateur web.

Exécuter le moteur de recherche en ligne de commande :

bash
Copier le code
python -m src.SearchEngine
Exécuter les tests unitaires :

bash
Copier le code
python -m pytest tests/
