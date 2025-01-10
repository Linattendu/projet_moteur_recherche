import streamlit as st
import os
import pickle
from src.Corpus import Corpus
from src.SearchEngine import SearchEngine
from dotenv import load_dotenv
import time
from src.constantes import *



# CONFIGURATION
nom_corpus = 'csvdiscours'

load_dotenv()

# INTERFACE STREAMLIT
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

    # Barre de recherche: Saisie des mots-clés et nombre de résultats
    mot_cle = st.text_input("Mots clés", "public college")
    
    # Filtre par date (plage de dates)
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date début", value=None)
    with col2:
        date_fin = st.date_input("Date fin", value=None)

    print("date_debut ",date_debut)
    # Filtre par auteur
    liste_auteurs = ['CLINTON','TRUMP']
    auteur_selectionne = st.selectbox("👤 Filtrer par auteur", ["Tous"] + liste_auteurs)
    
    # Slider pour le nombre de résultats
    nombre_docs = st.slider("Nombre d'articles à extraire :", 1, 20, 5)

    # Bouton de recherche
    if st.button("Rechercher"):
        st.write("Recherche en cours...")
        moteur = SearchEngine(nom_corpus=nom_corpus)
        
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
        print(f"Temps de recherche : {fin - debut:.3f} secondes")

        if not resultats.empty:
            for index, row in resultats.iterrows():
                # Titre cliquable avec une taille de police plus grande
                st.markdown(f"""
                <div class="result">
                    <a href="{row['URL']}" target="_blank">{row['Titre']}</a>
                    <p><b>{row['Extrait']}</b></p>
                    <p><b>{row['Auteur']}</b></p>
                    <p style="color:gray;">Score : {row['Score']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Ligne de séparation pour chaque résultat
                #st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.warning("Aucun document trouvé pour cette recherche.")



if __name__ == "__main__":
    main()
