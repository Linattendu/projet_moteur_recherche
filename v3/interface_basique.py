import streamlit as st
import os
import pickle
from src.Corpus import Corpus
from src.SearchEngine import SearchEngine
from dotenv import load_dotenv
import time
from src.constantes import *


# ============================================
# CONFIGURATION
# ============================================

CORPUS_PICKLE = os.path.join(DATA_DIR, "corpus_discours.pkl")
TF_PICKLE = os.path.join(DATA_DIR, "matrice_TF_discours.pkl")
TFxIDF_PICKLE = os.path.join(DATA_DIR, "matrice_TFxIDF_discours.pkl")
VOCAB_PICKLE = os.path.join(DATA_DIR, "corpus_discours_vocab.pkl")

load_dotenv()


# ============================================
# CHARGEMENT DU CORPUS
# ============================================
@st.cache_resource
def charger_corpus():
    if os.path.exists(CORPUS_PICKLE):
        with open(CORPUS_PICKLE, 'rb') as f:
            return pickle.load(f)
    else:
        st.error("❌ Corpus non trouvé ! Veuillez d'abord exécuter `tester_moteur.py` pour générer le corpus.")
        return None


# ============================================
# CHARGEMENT DES MATRICES TF / TFxIDF
# ============================================
@st.cache_resource
def charger_matrices():
    if os.path.exists(TF_PICKLE) and os.path.exists(TFxIDF_PICKLE):
        with open(TF_PICKLE, 'rb') as f:
            tf = pickle.load(f)
        with open(TFxIDF_PICKLE, 'rb') as f:
            tfidf = pickle.load(f)
        return tf, tfidf
    else:
        return None, None


# ============================================
# CHARGEMENT DU VOCABULAIRE
# ============================================
@st.cache_resource
def charger_vocabulaire():
    if os.path.exists(VOCAB_PICKLE):
        with open(VOCAB_PICKLE, 'rb') as f:
            return pickle.load(f)
    else:
        return None


# ============================================
# CONSTRUCTION DES MATRICES SI ABSENTES
# ============================================
def construire_matrices_si_absentes(corpus):
    tf, tfidf = charger_matrices()
    
    if tf is not None and tfidf is not None :
        moteur = SearchEngine(corpus)
        #moteur.matrice.vocab = charger_vocabulaire()

        # Si les matrices sont absentes ou incohérentes
        if tf is None or tfidf is None is None:
            st.warning("🔧 Matrices  non trouvés. Reconstruction en cours...")

            moteur.matrice.construire_vocab_et_matrice_TF()
            moteur.matrice.construire_matrice_TFxIDF()

            # Sauvegarde des matrices et du vocabulaire
            with open(TF_PICKLE, 'wb') as f:
                pickle.dump(moteur.matrice.mat_TF, f)

            with open(TFxIDF_PICKLE, 'wb') as f:
                pickle.dump(moteur.matrice.mat_TFxIDF, f)

            with open(VOCAB_PICKLE, 'wb') as f:
                pickle.dump(moteur.matrice.vocab, f)

            st.success("✅ Matrices et vocabulaire construits et sauvegardés.")
            return moteur.matrice.mat_TF, moteur.matrice.mat_TFxIDF
    else:
        print("Matrices non chargées !!!")
        return
    
    return tf, tfidf


# ============================================
# INTERFACE STREAMLIT
# ============================================
def main():
    # === CSS pour espacement ===
    st.markdown(
        """
        <style>
        .title h1 {
        font-size: 30px;  /* Taille du titre principal (plus petit) */
        font-weight: bold;
        text-align: center;  /* Centre le titre */
        }
        .result {
            margin-bottom: 30px;  /* Espace entre chaque résultat (gros espace) */
        }
        .result p {
            margin: 5px 0;  /* Espace réduit entre les lignes (titre, extrait, lien) */
            line-height: 1.4;  /* Hauteur de ligne (1.4x la taille de la police) */
        }
        .result a {
            text-decoration: none;  /* Pas de soulignement pour les liens */
            color: #b2a5c3;  /* Couleur du lien comme Google */
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    
    st.markdown('<div class="title"><h1> Moteur de Recherche de Discours</h1></div>', unsafe_allow_html=True)

    # Initialisation du corpus
    corpus = charger_corpus()
    if not corpus:
        st.stop()
    else:
        print("corpus chargé --->")

    # Initialisation de la matrice TF et TFxIDF
    tf, tfidf = construire_matrices_si_absentes(corpus)
    
    # Barre de recherche: Saisie des mots-clés et nombre de résultats
    mot_cle = st.text_input("🔍 Mots clés", "public college")
    
    # Filtre par date (plage de dates)
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("📅 Date début", value=None)
    with col2:
        date_fin = st.date_input("📅 Date fin", value=None)

    print("date_debut ",date_debut)
    # Filtre par auteur
    liste_auteurs = list(set(doc.auteur for doc in corpus.id2doc.values()))
    auteur_selectionne = st.selectbox("👤 Filtrer par auteur", ["Tous"] + liste_auteurs)
    
    # Slider pour le nombre de résultats
    nombre_docs = st.slider("Nombre d'articles à extraire :", 1, 50, 5)

    # Bouton de recherche
    if st.button("Rechercher"):
        st.write("Recherche en cours...")
        moteur = SearchEngine(corpus)
        
        # Charger les matrices et vocabulaire
        moteur.matrice.mat_TF = tf
        moteur.matrice.mat_TFxIDF = tfidf
        #moteur.matrice.vocab = charger_vocabulaire()

        debut = time.time()
        # Exécution de la recherche
        resultats = moteur.search(
            mot_cle, 
            n_resultats=nombre_docs,
            auteur=auteur_selectionne if auteur_selectionne != "Tous" else None,
            date_debut=date_debut,
            date_fin=date_fin
            )
        fin = time.time()
        print(f"🔍 Temps de recherche : {fin - debut:.3f} secondes")

        if not resultats.empty:
            for index, row in resultats.iterrows():
                # Titre cliquable avec une taille de police plus grande
                st.markdown(f"""
                <div class="result">
                    <a href="{row['URL']}" target="_blank">{row['Titre']}</a>
                    <p><b>{row['Extrait']}</b></p>
                    <p style="color:gray;">Score : {row['Score']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Ligne de séparation pour chaque résultat
                #st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.warning("Aucun document trouvé pour cette recherche.")



if __name__ == "__main__":
    main()
