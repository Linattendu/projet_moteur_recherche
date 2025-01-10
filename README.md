# Projet : Moteur de Recherche

### Branche Stable -  Version 3 : Recherche Avancée et Documentation

## Description

La branche main correspond à la version stable de l'application, intégrant toutes les fonctionnalités développées jusqu'aux TDs 3 à 10. Cette version comprend des fonctionnalités de recherche avancées, une interface utilisateur performante, et une documentation détaillée.

## Fonctionnalités

### Gestion de Corpus
- **Création et classification des corpus :** 
  - Génération des corpus à partir de sources comme des fichiers CSV ou des API externes (Reddit et Arxiv).
  - Nettoyage des textes et création de sous-corpus classifiés par thème.
- **Analyse des données :**
  - Extraction de fréquences de mots et génération de matrices TF-IDF.

### Moteur de Recherche
- **Recherche par mots-clés :**
  - Recherche dans les corpus avec un système de pondération basé sur les matrices TF-IDF.
  - Prise en charge des filtres par auteur, date, et thème.
- **Affichage des résultats :**
  - Résultats triés par pertinence avec extraits textuels.
  - Génération de nuages de mots pour visualiser les résultats.

### Interface Utilisateur
- **Streamlit :**
  - Interface simple pour lancer des recherches, sélectionner des filtres et afficher les résultats.
  - Visualisation des données avec graphiques interactifs et nuages de mots.

### Tests et Documentation
- **Tests automatisés :**
  - Validation des fonctionnalités principales avec `pytest`.
  - Couverture des modules de gestion de corpus, moteur de recherche, et extraction des données.
- **Documentation technique :**
  - Documentation générée automatiquement avec Doxygen.
  - Instructions claires pour les développeurs.

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/Linattendu/projet_moteur_recherche.git
cd projet_moteur_recherche
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux ou avecc Windows : venv\Scripts\activate  
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Utilisation

Lancer l'application Streamlit
```bash
streamlit run app.py
```

Lancer l'application Streamlit de l'interface basique
```bash
streamlit run interface_basique.py
```

Exécuter les tests
```bash
python -m pytest tests/
```

Générer la documentation en local ( celle-ci est automatisé avec github Actions)
```bash
doxygen Doxyfile # La documentation HTML sera disponible dans le dossier `docs/html/index.html`
```

## Auteurs

Binôme : Paul PONCET et Lina RHIM

Encadrants : Julien VELCIN et Francesco AMATO
