
#fichier tester_moteur_discours.py
import pandas as pd 
from src.constantes import *
from src.Corpus import Corpus
from tqdm import tqdm
from src.Document import Document
from src.Utils import Utils
import re
from src.SearchEngine import *
from src.GestionErreurs import *

pickle_path = ""

# Fonction pour découper les discours en phrases
def decouper_en_phrases(texte):
    return re.findall(r"[^.]+(?:\.(?:\s|\n))?", texte)

# 1.1 - détection du séparateur 
""" separateurs = ['\t', ',', ' ']
for i, sep in enumerate (separateurs):
    try:
        df = pd.read_csv(CSV_DISCOURS_PATH, sep=sep)
        print(f"✅ Séparateur détecté : {sep} i = {i}")
        print(df.head())
        break
    except Exception as e:
        print(f"❌ Erreur avec séparateur : {sep}") """

def convertir_discours():
    df = pd.read_csv(CSV_DISCOURS_PATH, sep='\t')
    
    # Conversion de la colonne 'date' au format datetime
    df['date'] = pd.to_datetime(df['date'], format='%B %d, %Y')
    print(df.head())
    print(df.columns)
    # resultat : Index(['speaker', 'text', 'date', 'descr', 'link'], dtype='object')

    # 1.2. Analyser la répartition des auteurs
    # il y a plusieurs orateurs
    print(df['speaker'].value_counts())
    
    return df
    
def construire_corpus_discours():
    df = convertir_discours()
    # 1.3 corpus
    nom_corpus = "discours"
    corpus = Corpus(nom_corpus)

    # Ajouter les documents (sans nettoyage pour le moment)
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        phrases = decouper_en_phrases(row['text'])
        
        for j,phrase in enumerate(phrases):
            """ if j < 6 :
                print(f"phrase:{phrase} longueur : {len(phrase)}\n ") """
            phrase_split = phrase.split()
            
            if len(phrase_split) > 3:  # Ignorer les phrases trop courtes
                doc = Document(
                    titre=row['descr'],
                    auteur=row['speaker'],
                    date=row['date'],
                    url=row['link'],
                    texte=phrase
                )
                result = corpus.ajouter_document(doc)
                            
    #  Nettoyer et concaténer le corpus une fois qu'il est complet
    corpus.texte_concatene = Utils.concatener_textes(corpus)
    
    # Chemin de sauvegarde dans le dossier 'data'
    dossier_data = "../data/"
    nom_fichier = "corpus_discours.pkl"
    chemin_sauvegarde = os.path.join(dossier_data, nom_fichier)
    # Sauvegarder le corpus discours
    corpus.save(chemin_sauvegarde)
    print(f"💾 Corpus sauvegardé dans {chemin_sauvegarde}")

    return corpus

def tester_corpus_discours(mot_cle):
    
    corpus = construire_corpus_discours()

    # Tester une recherche simple
    mot_cle = "University"
    resultats_search = corpus.search(mot_cle)
    print("resultats_search : \n", resultats_search)

    # recherche avec concorde
    result_concorde = corpus.concorde(mot_cle)
    print("result_concorde : \n", result_concorde)

def tester_moteur_discours(mot_cle):
    
    corpus = construire_corpus_discours()

    # initialisation du moteur
    search_engine = SearchEngine(corpus)
    
    
    resultats = search_engine.search(mot_cle, n_resultats=10)
    print("\n🔍 Résultats de la recherche :")
    print(resultats)


if __name__ == "__main__":
    
    load_dotenv()
    erreur = GestionErreurs(log_file="app_errors.log")
    mot_cle = "public college"
    