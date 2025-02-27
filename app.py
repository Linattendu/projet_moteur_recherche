import sqlite3
import pickle
import streamlit as st
from src.SearchEngine import SearchEngine
from src.ClassificateurThemesDiscours import ClassificateurThemesDiscours
import pandas as pd
from datetime import datetime
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import tempfile
import base64
from src.constantes import *

class StreamlitApp:
    """
    @class StreamlitApp
    @brief Application principale pour l'interface Streamlit.
    """

    def __init__(self):
        """
        @brief Initialise l'application avec des structures de données.
        """
        self.resultats_par_corpus = {}
        self.resultats_corpus_discours = {}

    def inject_css(self, file_name="streamlit_style.css"):
        """
        @brief Injecte un fichier CSS dans l'interface.
        @param file_name Nom du fichier CSS.
        """
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    def charger_document_par_chemin(self, chemin_document):
        """
        @brief Charge un document pickle depuis un chemin.
        @param chemin_document Chemin du fichier pickle.
        @return Document chargé.
        """
        with open(chemin_document, 'rb') as f:
            return pickle.load(f)

    def config_interface(self):
        """
        @brief Configure l'interface utilisateur (layout, styles, titre).
        """
        st.set_page_config(layout="wide", page_title="Moteur de Recherche")
        self.inject_css()
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {
                background-color: #262730;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.title("Moteur de Recherche de Corpus")

    def filtres(self):
        """
        @brief Définit les filtres de recherche via l'interface.
        @return Tuple contenant les filtres (mots-clés, thèmes, dates, etc.).
        """
        with st.sidebar:
            mot_cle = st.text_input("Entrez les mots-clés pour la recherche").strip()
            themes_selectionnes = st.multiselect("Sélectionnez les thèmes", ["Tous"] + list(THEMESCORPUS.keys()), default=["Tous"])
            date_debut = st.date_input("Date de début", value=None)
            date_fin = st.date_input("Date de fin", value=None)
            auteur = st.text_input("Entrez le nom de l'auteur (optionnel)").strip()
            sources = st.multiselect("Sélectionnez la source :", ["Tous", "csv", "redditArxiv"], default=["Tous"])
            nombre_docs = st.slider("Nombre de documents à extraire :", 1, 50, 10)
            choix_recherche = {
                "Recherche textuelle": st.button("Recherche textuelle"),
                "Recherche Nuage de Mots": st.button("Recherche Nuage de Mots"),
                "Recherche Temporelle": st.button("Recherche Temporelle"),
                "Comparer les Sources": st.button("Comparer les Sources")
            }
        return mot_cle, themes_selectionnes, date_debut, date_fin, auteur, sources, nombre_docs, choix_recherche

    def resultats_corpus(self, mot_cle, themes_selectionnes, sources, nombre_docs, auteur, date_debut, date_fin):
        """
        @brief Effectue une recherche dans les corpus en fonction des filtres.
        @param mot_cle Mots-clés recherchés.
        @param themes_selectionnes Thèmes sélectionnés.
        @param sources Sources sélectionnées.
        @param nombre_docs Nombre de documents à extraire.
        @param auteur Auteur filtré.
        @param date_debut Date de début pour la recherche.
        @param date_fin Date de fin pour la recherche.
        """
        tous = "csv" in sources and "redditArxiv" in sources
        liste_noms_corpus = []

        if ("Tous" in themes_selectionnes and ("Tous" in sources or tous)):
            for valeur in THEMESCORPUS.values():
                liste_noms_corpus.append(valeur[0])
            liste_noms_corpus.append("csvdiscours")
        elif ("Tous" not in themes_selectionnes and "Tous" not in sources and not tous):
            for theme in themes_selectionnes:
                if theme in THEMESCORPUS:
                    valeur = THEMESCORPUS[theme]
                    if "csv" in sources:
                        liste_noms_corpus.append(valeur[1])
                    if "redditArxiv" in sources:
                        liste_noms_corpus.append(valeur[0])
        elif "Tous" in themes_selectionnes and "Tous" not in sources and not tous:
            for valeur in THEMESCORPUS.values():
                if "csv" in sources:
                    liste_noms_corpus.append(valeur[1])
                if "redditArxiv" in sources:
                    liste_noms_corpus.append(valeur[0])
        elif "Tous" not in themes_selectionnes and ("Tous" in sources or tous):
            for theme in themes_selectionnes:
                if theme in THEMESCORPUS:
                    valeur = THEMESCORPUS[theme]
                    liste_noms_corpus.extend(valeur)

        for nom_corpus in liste_noms_corpus:
            print("nom_corpus resultat ", nom_corpus)
            if nom_corpus.startswith("csv") and nom_corpus != "csvdiscours":
                theme_corpus = nom_corpus.split("csv")[1]
                print("theme_corpus", theme_corpus)
                documents_scores = self.resultats_corpus_discours.get(theme_corpus, [])
                resultats = pd.DataFrame([{
                    'Titre': document.titre,
                    'Auteur': document.auteur,
                    'Date': document.date,
                    'Extrait': document.texte[:300],
                    'Score': score,
                    'URL': document.url
                } for chemin_document, score in documents_scores
                    for document in [self.charger_document_par_chemin(chemin_document)]
                    if mot_cle.lower() in document.texte.lower()])
            else:
                moteur = SearchEngine(nom_corpus)
                resultats = moteur.search(
                    mot_cle,
                    n_resultats=nombre_docs,
                    auteur=auteur,
                    date_debut=date_debut,
                    date_fin=date_fin
                )
            self.resultats_par_corpus[nom_corpus] = resultats

    def afficher_resultats(self, choix_recherche, mot_cle, auteur,date_debut,date_fin):
        """
        @brief Affiche les résultats de recherche dans différents formats.
        @param choix_recherche Options de recherche sélectionnées.
        @param mot_cle Mots-clés recherchés.
        @param auteur Auteur filtré.
        @param date_debut Date de début pour filtrer les résultats.
        @param date_fin Date de fin pour filtrer les résultats.
        """
        col1, col2 = st.columns([1, 3])
        with col2:
            
            # choix recherche textuelle
            if choix_recherche["Recherche textuelle"]:
                resultats_trouves = False  # Ajout d'un drapeau pour suivre l'état des résultats trouvés
                corpus_trie = sorted(self.resultats_par_corpus.items(), key=lambda x: len(x[1]), reverse=True)            
                for corpus, resultats in corpus_trie:
                    if not resultats.empty:
                        resultats_trouves = True
                        st.markdown(f"""
                                    <div style ="color: #2ce5c1;"> Corpus : {corpus}
                                    <p> Nombre de documents : {len(resultats)}\n </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        resultats = resultats.sort_values(by='Score', ascending=False)
                        
                        for index, row in resultats.iterrows():
                            st.write(f"**Titre :** {row['Titre']}")
                            st.write(f"**Auteur :** {row.get('Auteur', 'Non disponible')}")
                            st.write(f"**Date :** {row.get('Date', 'Non disponible')}")
                            st.write(f"**Extrait :** {row.get('Extrait', 'Pas d extrait disponible')}")
                            st.write(f"**URL :** {row.get('URL', 'Non disponible')}")
                            st.write(f"**Score :** {row['Score']:.2f}")
                            st.markdown("---")
                if not resultats_trouves:
                    st.warning(f"Aucune occurrence du mot-clé '{mot_cle}' n'a été trouvée dans les corpus sélectionnés oui.")
            
            # choix recherche par nuage de mots
            if choix_recherche["Recherche Nuage de Mots"]:            
                resultats_trouves = False 
                # corpus_trie : liste des résultats classés
                corpus_trie = sorted(self.resultats_par_corpus.items(), key=lambda x: len(x[1]), reverse=True)                
                
                # resultats : dataframe
                # colonnes :'Titre', 'Extrait', 'URL', 'Auteur', 'Date', 'Score'
                for corpus, resultats in corpus_trie:
 
                    if not resultats.empty:
                        resultats_trouves = True
                        st.markdown(f"""
                                <div style ="color: #2ce5c1;"> Corpus : {corpus}
                                <p> Nombre de documents : {len(resultats)}\n </p>
                                </div>
                                """, unsafe_allow_html=True)
                        resultats = resultats.sort_values(by='Score', ascending=False)     
                        texte_concatene = ' '.join(resultats['Extrait'].dropna().values)
                        
                        # Générer le WordCloud
                        wordcloud = WordCloud(width=800, height=600, background_color='white').generate(texte_concatene)
                        
                        # Créer un fichier temporaire pour sauvegarder l'image du Word Cloud
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                            fig, ax = plt.subplots(figsize=(9, 6))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis("off")
                            plt.savefig(tmpfile.name, bbox_inches='tight')
                            plt.close(fig)

                            # Intégrer l'image dans une div HTML personnalisée
                            st.markdown(
                                f"""
                                <div class="wordcloud-container">
                                    <img src="data:image/png;base64,{base64.b64encode(open(tmpfile.name, 'rb').read()).decode()}" alt="Word Cloud">
                                </div>
                                """,
                                unsafe_allow_html=True)
                if not resultats_trouves:
                    st.warning(f"Aucune occurrence du mot-clé '{mot_cle}' n'a été trouvée dans les corpus sélectionnés oui.")
            
            # recherche temporelle
            if choix_recherche["Recherche Temporelle"] and any(not resultats.empty for resultats in self.resultats_par_corpus.values()):
                st.subheader("Évolution temporelle du terme")

                # Concaténer les résultats pour toutes les sources
                df_temporel = pd.concat(self.resultats_par_corpus.values(), ignore_index=True)
                print("df_temporel conc ", df_temporel)

                # Filtrer les documents contenant le mot-clé
                df_temporel = df_temporel[df_temporel['Extrait'].str.contains(mot_cle, case=False, na=False)]
                
                print("df_temporel extrait ", df_temporel)
                
                # Filtrer par auteur si spécifié
                if auteur:
                    df_temporel = df_temporel[df_temporel['Auteur'].str.contains(auteur, case=False, na=False)]
                    print("df_temporel auteur ", df_temporel)

                # Conversion de la colonne Date au format datetime
                df_temporel['Date'] = pd.to_datetime(df_temporel['Date'], errors='coerce')
                print("df_temporel date ", df_temporel["Date"])
                
                # Supprimer les entrées sans date valide
                df_temporel.dropna(subset=['Date'], inplace=True)

                # Filtrer par plage de dates (si spécifiée)
                if date_debut:
                    df_temporel = df_temporel[df_temporel['Date'] >= pd.to_datetime(date_debut)]
                    
                if date_fin:
                    df_temporel = df_temporel[df_temporel['Date'] <= pd.to_datetime(date_fin)]

                # Grouper par mois (année-mois)
                freq_par_mois = df_temporel.groupby(df_temporel['Date'].dt.to_period("M")).size()
                
                # Tracer le graphique
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(freq_par_mois.index.astype(str), freq_par_mois.values, marker='o')
                ax.set_xlabel("Mois")
                ax.set_ylabel("Occurrences")
                ax.set_title(f"Évolution du terme '{mot_cle}' au fil du temps (par mois)")

                # Rotation des étiquettes pour une meilleure lisibilité
                plt.xticks(rotation=45)

                st.pyplot(fig)
            
            # recherche par comparaison 
            if choix_recherche["Comparer les Sources"]  and mot_cle:
                st.subheader(f"Comparaison des sources pour le mot '{mot_cle}'")

                repartition_sources = {}

                # Parcourir les corpus pour compter les occurrences du mot-clé
                for nom_corpus, resultats in self.resultats_par_corpus.items():
                    if not resultats.empty:
                        # Convertir le texte en minuscule pour éviter la casse
                        freq = resultats['Extrait'].str.lower().str.count(mot_cle.lower()).sum()
                        repartition_sources[nom_corpus] = freq

                if not repartition_sources:
                    st.warning("Aucune occurrence trouvée pour ce mot-clé.")
                else:
                    # Calculer la répartition des fréquences par source (CSV ou Reddit/Arxiv)
                    reddit_total = 0
                    csv_total = 0
                    sous_corpus_repartition = {}

                    for c, freq in repartition_sources.items():
                        if 'RedditArxiv' in c:
                            reddit_total += freq
                            theme = c.replace('RedditArxiv', '')
                            sous_corpus_repartition[f"Reddit/Arxiv ({theme})"] = freq
                        elif 'csv' in c:
                            csv_total += freq
                            theme = c.replace('csv', '')
                            sous_corpus_repartition[f"CSV ({theme})"] = freq

                    # Calculer les pourcentages correctement
                    total = reddit_total + csv_total
                    repartition_sources = {
                        "Reddit/Arxiv": reddit_total,
                        "CSV (Discours)": csv_total
                    }

                    # Affichage du graphique global
                    labels = list(repartition_sources.keys())
                    valeurs = list(repartition_sources.values())
                    pourcentages = [f"{(v / total) * 100:.1f}%" for v in valeurs]

                    fig, ax = plt.subplots()
                    wedges, texts, autotexts = ax.pie(
                        valeurs, autopct='%1.1f%%', startangle=90
                    )
                    ax.axis('equal')
                    plt.legend(wedges, [f"{label} - {pourcentages[i]}" for i, label in enumerate(labels)],
                            title="Sources", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

                    st.pyplot(fig)

                    # Graphique détaillé par thème
                    if sous_corpus_repartition:
                        st.subheader("Répartition par thèmes Reddit/Arxiv")
                        fig, ax = plt.subplots()
                        labels_detail = list(sous_corpus_repartition.keys())
                        valeurs_detail = list(sous_corpus_repartition.values())
                        pourcentages_detail = [f"{(v / total) * 100:.1f}%" for v in valeurs_detail]

                        wedges, texts, autotexts = ax.pie(
                            valeurs_detail, autopct='%1.1f%%', startangle=90
                        )
                        ax.axis('equal')
                        plt.legend(wedges, [f"{label} - {pourcentages_detail[i]}" for i, label in enumerate(labels_detail)],
                                title="Sous-corpus", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

                        st.pyplot(fig)

    def executer(self):
        """
        @brief Point d'entrée principal pour exécuter l'application.
        """
        self.config_interface()
 
        mot_cle, themes_selectionnes, date_debut, date_fin, auteur, sources, nombre_docs, choix_recherche = self.filtres()
        if any(choix_recherche.values()) and mot_cle:
            
            self.resultats_corpus(mot_cle, themes_selectionnes, sources, nombre_docs, auteur, date_debut, date_fin)
            self.afficher_resultats(choix_recherche, mot_cle, auteur,date_debut,date_fin)

if __name__ == "__main__":
    app = StreamlitApp()
    app.executer()
