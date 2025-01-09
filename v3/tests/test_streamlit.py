import pytest
from unittest.mock import MagicMock, patch
from interface_basique import main
from streamlit_app import charger_resultats_corpus_discours, mettre_a_jour_theme_nomCorpus
import os
from datetime import date


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
        mock_text_input.assert_called_once_with("🔍 Mots clés", "public college")
        mock_date_input.assert_any_call("📅 Date début", value=None)
        mock_date_input.assert_any_call("📅 Date fin", value=None)
        mock_selectbox.assert_called_once_with("👤 Filtrer par auteur", ["Tous", "CLINTON", "TRUMP"])
        mock_slider.assert_called_once_with("Nombre d'articles à extraire :", 1, 20, 5)
        mock_button.assert_called_once_with("Rechercher")
        mock_markdown.assert_called()

def test_charger_resultats_corpus_discours(mocker):
    """Tester le chargement des résultats classifiés."""
    mocker.patch("streamlit_app.os.path.exists", return_value=True)
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=b"{}"))
    mocker.patch("pickle.load", return_value={"politics": []})

    resultats = charger_resultats_corpus_discours()
    assert isinstance(resultats, dict)
    assert "politics" in resultats


def test_mettre_a_jour_theme_nomCorpus():
    """Tester la mise à jour du dictionnaire des thèmes."""
    theme_nomCorpus = {"politics": ["RedditArxivpolitics"]}
    resultats_classes = {"climatechange": []}
    updated = mettre_a_jour_theme_nomCorpus(resultats_classes, theme_nomCorpus)
    assert "climatechange" in updated
    assert "csvclimatechange" in updated["climatechange"]
