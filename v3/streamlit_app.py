import sqlite3
import pickle
import streamlit as st
from src.SearchEngine import SearchEngine
import pandas as pd
from datetime import datetime
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import tempfile
import base64

DB_PATH = "../db/corpus_matrix.sqlite"
RESULTS_PATH = "../db/classified_results.pkl"

# Dictionnaire des corpus par thème
theme_nomCorpus = { 
    "politics": ["RedditArxivpolitics", "csvdiscours"],
    "technology": ["RedditArxivtechnology", "csvtechnology"],
    "education": ["RedditArxiveducation", "csveducation"],
    "climatechange": ["RedditArxivclimatechange", "csvclimatechange"],
    "science": ["RedditArxivscience", "csvscience"],
    "health": ["RedditArxivhealth", "csvhealth"]
}

# CONFIGURATION DE L'INTERFACE
st.set_page_config(layout="wide", page_title="Moteur de Recherche ")

def inject_css(file_name="streamlit_style.css"):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def charger_resultats_corpus_discours():
    ''' 
    retourne un dictionnaire où chaque clé est un thème (par exemple "climatechange") et 
    chaque valeur est une liste de tuples contenant des objets Document et des scores.
    '''
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH, 'rb') as f:
            return pickle.load(f) 
    else:
        st.warning("Aucun sous-corpus classifié trouvé. Exécutez l'analyse d'abord.")
        return {}

def mettre_a_jour_theme_nomCorpus(resultats_classes, theme_nomCorpus):
    '''
    Cette fonction met à jour theme_nomCorpus en ajoutant les sous-corpus classifiés 
    (csvscience, csvclimatechange etc.) après le chargement de classified_results.pkl. 
    '''

    for theme, documents in resultats_classes.items():
        corpus_csv = f"csv{theme}"  # Générer le nom du sous-corpus CSV basé sur le thème
        if theme in theme_nomCorpus:
            if corpus_csv not in theme_nomCorpus[theme]:
                theme_nomCorpus[theme].append(corpus_csv)  # Ajouter le sous-corpus à la liste existante
        else:
            # Créer une nouvelle clé si le thème n'existe pas encore
            theme_nomCorpus[theme] = ["RedditArxiv" + theme, corpus_csv]
    print("Dictionnaire mis à jour : ", theme_nomCorpus)
    return theme_nomCorpus


# ============================================
# LANCEMENT DU PROGRAMME
# ============================================


if __name__ == "__main__":
    
    inject_css()
    st.title("Moteur de Recherche de Corpus")

    resultats_par_corpus = {}
    resultats_corpus_discours = charger_resultats_corpus_discours() # issus du corpus discours
    #print("type resultats_corpus_discours ", resultats_corpus_discours)
    
    theme_nomCorpus = mettre_a_jour_theme_nomCorpus(resultats_corpus_discours, theme_nomCorpus)
    # {'politics': ['RedditArxivpolitics', 'csvdiscours'], 
    #  'technology': ['RedditArxivtechnology', 'csvtechnology'],
    #  ...
    
    print("themes mis à jour : ",theme_nomCorpus )

    col1, col2 = st.columns([1, 3])

    with col1:
        #st.subheader("Filtres de recherche")
        mot_cle = st.text_input("Entrez les mots-clés pour la recherche").strip()
        themes_selectionnes = st.multiselect("Sélectionnez les thèmes", ["Tous"] + list(theme_nomCorpus.keys()), default=["Tous"])
        date_debut = st.date_input("Date de début", value=None)
        date_fin = st.date_input("Date de fin", value=None)
        auteur = st.text_input("Entrez le nom de l'auteur (optionnel)").strip()
        sources = st.multiselect("Sélectionnez la source :", ["Tous", "csv", "redditArxiv"], default=["Tous"])


        nombre_docs = st.slider("Nombre de documents à extraire :", 1, 50, 10)
        recherche_textuelle = st.button("Recherche textuelle")
        recherche_wordcloud = st.button("Recherche Nuage de Mots")
        recherche_temporelle = st.button("Graphique Temporel")
        recherche_comparaison = st.button("Comparer les Sources")


        
    if (recherche_textuelle or recherche_wordcloud 
        or recherche_temporelle or recherche_comparaison) and mot_cle:
        
        # Déterminer si toutes les sources sont sélectionnées
        tous = "csv" in sources and "redditArxiv" in sources
        
        liste_noms_corpus = [] # liste des corpus

        # Si "Tous" est sélectionné dans les thèmes et toutes les sources sont choisies
        if ("Tous" in themes_selectionnes 
            and ("Tous" in sources or tous) ):
            # recherche dans le dictionnaire theme_nomCorpus { theme: [liste corpus]}
            for valeur in theme_nomCorpus.values():
                liste_noms_corpus.append(valeur[0]) # Prendre la source redditArxiv par défaut
            liste_noms_corpus.append("csvdiscours") # ajout corpus discours (csv)
                    
        elif ("Tous" not in themes_selectionnes 
              and "Tous" not in sources and not tous) :
            for theme in themes_selectionnes:
                if theme in theme_nomCorpus:
                    valeur = theme_nomCorpus[theme]
                    if "csv" in sources:
                        liste_noms_corpus.append(valeur[1]) # Prendre le corpus csv
                    if "redditArxiv" in sources:
                        liste_noms_corpus.append(valeur[0]) # Prendre le corpus redditArxiv
        
        
        elif "Tous" in themes_selectionnes and "Tous" not in sources and not tous:
            for valeur in theme_nomCorpus.values():
                if "csv" in sources :
                    liste_noms_corpus.append(valeur[1])
                if "redditArxiv" in sources:
                    liste_noms_corpus.append(valeur[0])

        # Cas 4 : Thèmes spécifiques mais toutes les sources
        elif "Tous" not in themes_selectionnes and ("Tous" in sources or tous):
            for theme in themes_selectionnes:
                if theme in theme_nomCorpus:
                    valeur = theme_nomCorpus[theme]
                    liste_noms_corpus.extend(valeur)  # Ajouter les deux corpus (csv et redditArxiv)
            
        # Chargement et recherche dans les corpus sélectionnés
        for nom_corpus in liste_noms_corpus:
            print("nom_corpus près remplissage liste : ", nom_corpus)
            if nom_corpus.startswith("csv") and nom_corpus != "csvdiscours":
            
                # Transformer les tuples (Document, score) en dictionnaires exploitables
                documents_scores = resultats_corpus_discours[nom_corpus.split("csv")[1]]
                
                # Utilisation des sous-corpus classifiés discours(fichiers pickle)
                resultats = pd.DataFrame([{
                'Titre': doc.titre,
                'Auteur': doc.auteur,
                'Date': doc.date,
                'Extrait': doc.texte[:300],  # Extrait limité à 300 caractères
                'Score': score,
                'URL': doc.url
                } for doc, score in documents_scores if mot_cle.lower() in doc.texte.lower()])
                print("Documents filtrés : ", resultats)

            else:
                print("nom de corpus si pas discours ",nom_corpus)
                # Chargement normal depuis la base de données
                #corpus, tf, tfidf, vocab = charger_corpus_depuis_db(nom_corpus)
               

                moteur = SearchEngine(nom_corpus)
                resultats = moteur.search(
                    mot_cle, 
                    n_resultats=nombre_docs, 
                    auteur=auteur,
                    date_debut=date_debut, 
                    date_fin=date_fin 
                    )
            
            resultats_par_corpus[nom_corpus] = resultats  
        print("resultats_par_corpus ", resultats_par_corpus) 
        print("resultats_par_corpus ", len(resultats_par_corpus))              

    # Affichage conditionnel basé sur le bouton cliqué
    with col2: 
                   
        if recherche_textuelle and resultats_par_corpus:
            st.subheader("Résultats de la recherche")
            resultats_trouves = False  # Ajout d'un drapeau pour suivre l'état des résultats trouvés
            corpus_trie = sorted(resultats_par_corpus.items(), key=lambda x: len(x[1]), reverse=True)
            
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
        # resultats_par_corpus : dictionnaire
        if recherche_wordcloud  and  resultats_par_corpus:
            print("type de resultats_par_corpus ", type(resultats_par_corpus))
            
            # corpus_trie : liste des résultats classés
            corpus_trie = sorted(resultats_par_corpus.items(), key=lambda x: len(x[1]), reverse=True)
            
            print("type de corpus_trie ", type(corpus_trie))
            
            # resultats : dataframe
            # colonnes :'Titre', 'Extrait', 'URL', 'Auteur', 'Date', 'Score'
            for corpus, resultats in corpus_trie:
                
                print("type de resultats ", type(resultats))
                print("colonnes resultats ", resultats.columns)
                print("type de corpus ", type(corpus))
                resultats = resultats.sort_values(by='Score', ascending=False)
                
               
                
                if not resultats.empty:
                    st.markdown(f"""
                            <div style ="color: #2ce5c1;"> Corpus : {corpus}
                            <p> Nombre de documents : {len(resultats)}\n </p>
                            </div>
                            """, unsafe_allow_html=True)
                    print("dataframe resultats : ", resultats)
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
                            unsafe_allow_html=True
                        )
        if recherche_temporelle and any(not resultats.empty for resultats in resultats_par_corpus.values()):
            st.subheader("Évolution temporelle du terme")

            # Concaténer les résultats pour toutes les sources
            df_temporel = pd.concat(resultats_par_corpus.values(), ignore_index=True)
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
        
        if recherche_comparaison and mot_cle:
            st.subheader(f"Comparaison des sources pour le mot '{mot_cle}'")

            repartition_sources = {}

            # Parcourir les corpus pour compter les occurrences du mot-clé
            for nom_corpus, resultats in resultats_par_corpus.items():
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
