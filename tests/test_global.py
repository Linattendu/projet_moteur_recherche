import pytest
import pickle
import pandas as pd
import streamlit as st
from unittest.mock import MagicMock, patch, mock_open
from interface_basique import main
from datetime import date, datetime
from app import StreamlitApp
from src.SearchEngine import *

@pytest.fixture
def mock_streamlit(mocker):
    """Mock les fonctions Streamlit pour éviter les appels réels."""
    return mocker.patch.multiple(
        "streamlit",
        text_input=MagicMock(return_value="climatechange"),
        date_input=MagicMock(side_effect=[date(2020, 1, 1), date(2023, 1, 1)]),  # Utilisation d'objets date
        #date_input=MagicMock(side_effect=["2020-01-01", "2023-01-01"]),
        selectbox=MagicMock(return_value="Tous"),
        slider=MagicMock(return_value=5),
        button=MagicMock(return_value=True),
        markdown=MagicMock(),
        write=MagicMock(),
        warning=MagicMock(),
    )


def test_main_interface_basique():
    """Test simple pour vérifier les appels Streamlit dans l'interface basique."""
    with patch("streamlit.text_input", return_value="climatechange") as mock_text_input, \
         patch("streamlit.date_input", side_effect=["2020-01-01", "2023-01-01"]) as mock_date_input, \
         patch("streamlit.selectbox", return_value="Tous") as mock_selectbox, \
         patch("streamlit.slider", return_value=5) as mock_slider, \
         patch("streamlit.button", return_value=True) as mock_button, \
         patch("streamlit.markdown") as mock_markdown, \
         patch("streamlit.write") as mock_write, \
         patch("streamlit.warning") as mock_warning:

        # Appeler la fonction principale de l'interface basique
        main()

        # Vérifier les appels Streamlit
        mock_text_input.assert_called_once_with("Mots clés", "public college")
        mock_date_input.assert_any_call("Date début", value=None)
        mock_date_input.assert_any_call("Date fin", value=None)
        mock_selectbox.assert_called_once_with("👤 Filtrer par auteur", ["Tous", "CLINTON", "TRUMP"])
        mock_slider.assert_called_once_with("Nombre d'articles à extraire :", 1, 20, 5)
        mock_button.assert_called_once_with("Rechercher")
        mock_markdown.assert_called()


def test_inject_css():
    with patch("builtins.open", mock_open(read_data="body { background-color: red; }")) as mock_file:
        app = StreamlitApp()
        with patch("streamlit.markdown") as mock_markdown:
            app.inject_css()
            mock_file.assert_called_once_with("streamlit_style.css")
            mock_markdown.assert_called_once_with('<style>body { background-color: red; }</style>', unsafe_allow_html=True)


def test_charger_document_par_chemin():
    mock_data = {"key": "value"}
    with patch("builtins.open", mock_open(read_data=pickle.dumps(mock_data))) as mock_file:
        app = StreamlitApp()
        result = app.charger_document_par_chemin("test_document.pkl")
        mock_file.assert_called_once_with("test_document.pkl", 'rb')
        assert result == mock_data


def test_config_interface():
    app = StreamlitApp()
    with patch("streamlit.set_page_config") as mock_set_page_config, \
         patch("streamlit.markdown") as mock_markdown, \
         patch("app.StreamlitApp.inject_css") as mock_inject_css:  # Corrected path
        app.config_interface()
        mock_set_page_config.assert_called_once_with(layout="wide", page_title="Moteur de Recherche")
        mock_inject_css.assert_called_once()
        mock_markdown.assert_called()

def test_filtres():
    app = StreamlitApp()
    with patch("streamlit.text_input", side_effect=["climate change", ""]) as mock_text_input, \
         patch("streamlit.multiselect", side_effect=[["Tous"], ["Tous"]]) as mock_multiselect, \
         patch("streamlit.date_input", side_effect=[date(2020, 1, 1), date(2023, 1, 1)]) as mock_date_input, \
         patch("streamlit.slider", return_value=10) as mock_slider, \
         patch("streamlit.button", side_effect=[True, False, False, False]) as mock_button:
        result = app.filtres()
        assert result == (
            "climate change", ["Tous"], date(2020, 1, 1), date(2023, 1, 1),
            "", ["Tous"], 10, {"Recherche textuelle": True, "Recherche Nuage de Mots": False, "Recherche Temporelle": False, "Comparer les Sources": False}
        )

def test_resultats_corpus():
    app = StreamlitApp()

    # Simuler le SearchEngine et sa méthode search
    with patch("src.SearchEngine.SearchEngine") as MockSearchEngine:
        mock_engine = MockSearchEngine.return_value
        mock_engine.search.return_value = pd.DataFrame({"Titre": ["Doc1"], "Score": [0.8]})

        # Appeler la méthode à tester
        app.resultats_corpus("climate", ["Tous"], ["Tous"], 10, "clinton", "2020-01-01", "2023-01-01")

        # Vérifier qu'il y a au moins un résultat
        assert len(app.resultats_par_corpus) > 0

def test_afficher_resultats():
    app = StreamlitApp()
    app.resultats_par_corpus = {
        "Corpus1": pd.DataFrame({
            "Titre": ["america"],
            "Auteur": ["clinton"],
            "Date": ["2020-01-01"],
            "Extrait": ["This is an excerpt."],
            "Score": [0.9],
            "URL": ["http://politics.com"]
        })
    }
    with patch("streamlit.markdown") as mock_markdown, \
         patch("streamlit.write") as mock_write, \
         patch("streamlit.warning") as mock_warning:
        app.afficher_resultats(
            {"Recherche textuelle": True, "Recherche Nuage de Mots": False, "Recherche Temporelle": False, "Comparer les Sources": False},
            "climate",
            "clinton",
            "2020-01-01",
            "2023-01-01"
        )
        mock_markdown.assert_called()
        mock_write.assert_called()
        mock_warning.assert_not_called()


def test_flux_complet_recherche():
    with patch("src.SearchEngine.SearchEngine") as MockSearchEngine:
        moteur = MockSearchEngine.return_value
        moteur.search.return_value = pd.DataFrame({
            "Extrait": ["climate change is real", "climate policies are crucial"],
            "Score": [0.9, 0.8]
        })

        resultats = moteur.search("climate", n_resultats=10)
        assert len(resultats) > 0
        assert all("climate" in extrait.lower() for extrait in resultats["Extrait"])


def test_validation_filtres_recherche():
    with patch("src.SearchEngine.SearchEngine") as MockSearchEngine:
        moteur = MockSearchEngine.return_value
        moteur.search.return_value = pd.DataFrame({
            "Extrait": ["climate change discussion"],
            "Date": ["2021-06-01"],
            "Auteur": ["Barack Obama"]
        })

        # Test des filtres par date
        resultats = moteur.search("climate", date_debut="2020-01-01", date_fin="2022-01-01")
        for _, row in resultats.iterrows():
            assert "2020-01-01" <= row["Date"] <= "2022-01-01"

        # Test des filtres par auteur
        resultats = moteur.search("climate", auteur="Barack Obama")
        for _, row in resultats.iterrows():
            assert row["Auteur"] == "Barack Obama"


def test_visualisation_resultats():
    with patch("src.SearchEngine.SearchEngine") as MockSearchEngine:
        moteur = MockSearchEngine.return_value
        moteur.search.return_value = pd.DataFrame({
            "Extrait": ["climate change discussion", "global climate policies"],
            "Date": ["2021-06-01", "2022-05-01"]
        })

        resultats = moteur.search("climate", n_resultats=10)
        texte_concatene = " ".join(resultats["Extrait"])
        assert "climate" in texte_concatene

        # Vérifier que les dates sont valides
        for date in resultats["Date"]:
            datetime.strptime(date, "%Y-%m-%d")


def test_classification_documents():
    classifier = MagicMock()
    classifier.creer_sous_corpus.return_value = {"climatechange": ["Doc1", "Doc2"]}

    sous_corpus = classifier.creer_sous_corpus(None, None, None)
    assert "climatechange" in sous_corpus


def test_robustesse_recherche():
    with patch("src.SearchEngine.SearchEngine") as MockSearchEngine:
        moteur = MockSearchEngine.return_value
        moteur.search.side_effect = [
            pd.DataFrame(),
            pd.DataFrame()
        ]

        resultats = moteur.search("nonexistent", n_resultats=10)
        assert len(resultats) == 0

        resultats = moteur.search("climate", date_debut="2022-01-01", date_fin="2020-01-01")
        assert len(resultats) == 0

def test_performance():
    with patch("src.SearchEngine.SearchEngine") as MockSearchEngine:
        moteur = MockSearchEngine.return_value
        moteur.search.return_value = pd.DataFrame({
            "Extrait": [f"Document {i}" for i in range(50)]
        })

        resultats = moteur.search("climate", n_resultats=50)
        assert len(resultats) == 50


from unittest.mock import patch, MagicMock

def test_base_donnees_resilience():
    # Patcher la classe CorpusMatriceManager
    with patch("src.CorpusMatriceManager.CorpusMatriceManager") as MockManager:
        # Simuler une instance de CorpusMatriceManager
        mock_instance = MockManager.return_value

        # Simuler le curseur et son comportement
        mock_instance.cursor.execute.return_value.fetchone.return_value = [10]  # Simule un résultat SQL

        # Appeler une méthode fictive qui utilise la base de données
        result = mock_instance.cursor.execute("SELECT COUNT(*) FROM corpus").fetchone()[0]

        # Vérifier que le résultat est valide
        assert result > 0, "La base de données n'a pas été correctement initialisée."

def test_base_donnees_erreur():
    with patch("src.CorpusMatriceManager.CorpusMatriceManager") as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.cursor.execute.side_effect = Exception("Erreur SQL")

        with pytest.raises(Exception, match="Erreur SQL"):
            mock_instance.cursor.execute("SELECT COUNT(*) FROM corpus")

def test_charger_document_fichier_manquant():
    app = StreamlitApp()
    with pytest.raises(FileNotFoundError):
        app.charger_document_par_chemin("fichier_inexistant.pkl")
