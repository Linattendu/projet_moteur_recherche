# Projet : Moteur de recherche

Version 1 : Gestion de Corpus et Recherche de Textes 

## Description

Cette version `v1` constitue le socle de base de l'application, correspondant aux fonctionnalités développées dans les TDs 3 à 5. Elle permet de gérer un corpus, de nettoyer les textes, et de fournir des fonctionnalités de recherche simples.

---

## Fonctionnalités

- **Gestion de Corpus :** 
  - Création de corpus à partir de fichiers CSV.
  - Nettoyage et segmentation des textes.

- **Recherche :** 
  - Recherche par mots-clés dans le corpus.
  - Extraction des passages pertinents contenant les mots recherchés.

- **Préparation :** 
  - Mise en place de structures pour des fonctionnalités avancées dans les futures versions (matrices TF-IDF, classification).

---

## Installation

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/Linattendu/projet_moteur_recherche.git
   cd projet_moteur_recherche
   ```
2. **Créer un environnement virtuel et installer les dépendances :**

  ```bash
  python -m venv venv
  source venv/bin/activate  # sur linux ; sur Windows : venv\Scripts\activate
  pip install -r requirements.txt
  ```

5. **Utilisation**
Lancer le code :
  ```bash
  python -m src.Author
  ect...
  ```

6. Exécuter les tests :

```bash
python -m pytest tests/
```

## Auteurs
Binôme : PONCET Paul et RHIM Lina

Encadrants : Julien Velcin et Francesco Amato
