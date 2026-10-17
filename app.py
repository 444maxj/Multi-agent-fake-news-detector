"""
Interface utilisateur Streamlit pour le Fake News Detector.
Lance avec : streamlit run app.py
"""

import os
import json
import time
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajoute 'src' au sys.path pour acceder au package factcheck
SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from factcheck.core.orchestrator import lancer_verification

# Chargement des variables d'environnement depuis .env
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration de la page Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title  = "Fake News Detector",
    page_icon   = "🔍",
    layout      = "wide",
    initial_sidebar_state = "expanded"
)

# ---------------------------------------------------------------------------
# CSS personnalise pour une presentation professionnelle
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .verdict-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.4em;
        font-weight: bold;
        margin: 20px 0;
    }
    .verdict-vrai         { background-color: #d4edda; color: #155724; border: 2px solid #28a745; }
    .verdict-faux         { background-color: #f8d7da; color: #721c24; border: 2px solid #dc3545; }
    .verdict-partiel      { background-color: #fff3cd; color: #856404; border: 2px solid #ffc107; }
    .verdict-nonverif     { background-color: #d1ecf1; color: #0c5460; border: 2px solid #17a2b8; }
    .etape-box {
        background-color: #f8f9fa;
        border-left: 4px solid #0066cc;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 0 5px 5px 0;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Barre laterale : configuration et exemples
# ---------------------------------------------------------------------------
with st.sidebar:
    
 
    st.subheader("Affirmations de test")

    affirmations_test = [
        "La Tour Eiffel mesure 400 metres de hauteur",
        "Les vaccins COVID-19 contiennent des micropuces",
        "Le Maroc a accueilli la Coupe du Monde 2030",
        "L'intelligence artificielle va remplacer tous les emplois d'ici 2030",
        "La consommation de cafe reduit le risque de diabete de type 2",
    ]

    if "affirmation_choisie" not in st.session_state:
        st.session_state["affirmation_choisie"] = ""

    for aff in affirmations_test:
        if st.button(aff[:50] + "...", key=aff, use_container_width=True):
            st.session_state["affirmation_choisie"] = aff

    st.divider()
    st.caption(
        "Fake News Detector — Architecture SMA\n"
        "5 agents specialises collaborent pour verifier chaque affirmation."
    )


# ---------------------------------------------------------------------------
# Interface principale
# ---------------------------------------------------------------------------
st.title("Fake News Detector Multi-Sources")
st.markdown(
    "Soumettez une affirmation. Le systeme multi-agents collecte des sources, "
    "evalue leur fiabilite, analyse les contradictions et produit un verdict argumente."
)

# Champ de saisie de l'affirmation
affirmation_input = st.text_area(
    "Affirmation a verifier",
    value       = st.session_state["affirmation_choisie"],
    height      = 80,
    placeholder = "Ex : La consommation de sucre cause le diabete de type 1..."
)

col1, col2 = st.columns([1, 4])
with col1:
    bouton_verifier = st.button("Verifier", type="primary", use_container_width=True)
with col2:
    st.empty()


# ---------------------------------------------------------------------------
# Lancement de la verification
# ---------------------------------------------------------------------------
if bouton_verifier and affirmation_input.strip():

    # Verification des cles API
    if not os.getenv("GROQ_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        st.error(
            "Cles API manquantes. Renseignez-les dans la barre laterale gauche."
        )
        st.stop()

    st.divider()
    st.subheader("Progression du pipeline")

    # Zone de progression des etapes
    zone_etapes     = st.empty()
    barre_progress  = st.progress(0)
    etapes_terminees = []

    def afficher_progression(numero: int, description: str):
        """
        Callback appele par l'orchestrateur a chaque etape.
        Met a jour l'affichage en temps reel.
        """
        etapes_terminees.append(f"Etape {numero}/5 : {description}")
        barre_progress.progress(numero / 5)

        html_etapes = "".join(
            f'<div class="etape-box">{e}</div>'
            for e in etapes_terminees
        )
        zone_etapes.markdown(html_etapes, unsafe_allow_html=True)

    try:
        debut = time.time()

        # Lancement du pipeline complet
        resultat = lancer_verification(
            affirmation   = affirmation_input.strip(),
            callback_etape = afficher_progression
        )

        duree = round(time.time() - debut, 1)
        barre_progress.progress(1.0)

        # ---------------------------------------------------------------------------
        # Affichage du verdict
        # ---------------------------------------------------------------------------
        st.divider()
        st.subheader("Resultat de l'analyse")

        verdict   = resultat["verdict"]
        confiance = int(resultat["confiance"] * 100)

        # Choix de la classe CSS selon le verdict
        classes_verdict = {
            "Vrai":              "verdict-vrai",
            "Faux":              "verdict-faux",
            "Partiellement vrai":"verdict-partiel",
            "Non verifiable":    "verdict-nonverif"
        }
        classe_css = classes_verdict.get(verdict, "verdict-nonverif")

        st.markdown(
            f'<div class="verdict-box {classe_css}">'
            f'Verdict : {verdict} &nbsp;&nbsp;|&nbsp;&nbsp; Confiance : {confiance}%'
            f'</div>',
            unsafe_allow_html=True
        )

        # Metriques rapides
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Sources analysees", resultat["nb_sources"])
        col_m2.metric("Sous-questions", len(resultat["sous_questions"]))
        col_m3.metric("Duree d'analyse", f"{duree}s")

        # ---------------------------------------------------------------------------
        # Rapport complet
        # ---------------------------------------------------------------------------
        st.divider()
        with st.expander("Rapport complet", expanded=True):
            st.markdown(resultat["rapport_texte"])

        # ---------------------------------------------------------------------------
        # Details techniques (pour la presentation academique)
        # ---------------------------------------------------------------------------
        with st.expander("Details techniques du pipeline"):

            st.write("**Sous-questions generees par l'agent decomposeur :**")
            for i, q in enumerate(resultat["sous_questions"], 1):
                st.write(f"{i}. {q}")

            st.write("**Analyse contradictoire :**")
            analyse = resultat["analyse"]

            col_p, col_c = st.columns(2)
            with col_p:
                st.write("Arguments pour :")
                for arg in analyse.get("arguments_pour", []):
                    st.write(f"- {arg}")
            with col_c:
                st.write("Arguments contre :")
                for arg in analyse.get("arguments_contre", []):
                    st.write(f"- {arg}")

            if analyse.get("contradictions"):
                st.write("**Contradictions detectees :**")
                for c in analyse["contradictions"]:
                    st.write(f"- {c}")

            st.write(f"**Convergence globale des sources :** {analyse.get('convergence', 'N/A')}")

        # ---------------------------------------------------------------------------
        # Export du rapport
        # ---------------------------------------------------------------------------
        rapport_json = json.dumps(resultat, ensure_ascii=False, indent=2)
        st.download_button(
            label     = "Telecharger le rapport (JSON)",
            data      = rapport_json,
            file_name = "rapport_fact_check.json",
            mime      = "application/json"
        )

    except EnvironmentError as e:
        st.error(f"Erreur de configuration : {e}")
    except Exception as e:
        st.error(f"Erreur inattendue : {e}")
        st.exception(e)

elif bouton_verifier and not affirmation_input.strip():
    st.warning("Veuillez saisir une affirmation avant de lancer la verification.")
