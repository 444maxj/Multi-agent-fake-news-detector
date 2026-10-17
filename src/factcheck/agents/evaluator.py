"""
Agent Evaluateur de Sources.
Attribue un score de fiabilite a chaque source selon le referentiel JSON
et des heuristiques supplementaires (fraicheur, type de domaine).
"""

import json
import os
from pathlib import Path


def charger_referentiel() -> dict:
    """
    Charge le referentiel de fiabilite depuis le fichier JSON.
    Cherche dans plusieurs emplacements possibles pour garantir la portabilite.
    """
    candidats = [
        # Emplacement relatif standard (racine du projet / data)
        Path(__file__).resolve().parents[3] / "data" / "source_reliability.json",
        Path.cwd() / "data" / "source_reliability.json",
        Path(__file__).resolve().parent / ".." / ".." / ".." / "data" / "source_reliability.json",
    ]

    for chemin in candidats:
        if chemin.is_file():
            with open(chemin, "r", encoding="utf-8") as f:
                return json.load(f)

    # Si introuvable, lever une erreur explicite
    raise FileNotFoundError(
        "Fichier source_reliability.json introuvable dans data/. "
        "Verifiez la presence du dossier data/ a la racine du projet."
    )


# Chargement unique au demarrage du module (evite les IO repetees)
REFERENTIEL = charger_referentiel()


def evaluer_domaine(domaine: str) -> dict:
    """
    Recherche le score de fiabilite d'un domaine dans le referentiel.
    Utilise une correspondance partielle pour gerer les sous-domaines.

    Parametres :
        domaine : nom de domaine extrait de l'URL (ex: 'lemonde.fr')

    Retourne :
        dict { score, biais, type } avec valeurs par defaut si inconnu
    """
    # Recherche exacte d'abord
    if domaine in REFERENTIEL:
        return REFERENTIEL[domaine]

    # Recherche partielle (ex: 'fr.wikipedia.org' -> 'wikipedia.org')
    for cle in REFERENTIEL:
        if cle in domaine:
            return REFERENTIEL[cle]

    # Valeur par defaut pour les domaines inconnus
    return {
        "score": 0.40,
        "biais": "inconnu",
        "type":  "source_inconnue"
    }


def evaluator_agent(resultats: dict) -> dict:
    """
    Enrichit chaque source avec son evaluation de fiabilite.
    Trie les sources par score decroissant pour chaque question.

    Parametres :
        resultats : dictionnaire question -> liste de sources (sortie du researcher)

    Retourne :
        dictionnaire question -> liste de sources enrichies et triees
    """
    resultats_evalues = {}

    for question, sources in resultats.items():
        sources_evaluees = []

        for source in sources:
            domaine   = source.get("domaine", "")
            evaluation = evaluer_domaine(domaine)

            # Enrichissement de la source avec les donnees de fiabilite
            source_enrichie = {
                **source,                             # copie tous les champs existants
                "fiabilite":   evaluation["score"],
                "biais":       evaluation["biais"],
                "type_source": evaluation["type"]
            }
            sources_evaluees.append(source_enrichie)

        # Tri par score de fiabilite decroissant
        sources_evaluees.sort(key=lambda s: s["fiabilite"], reverse=True)
        resultats_evalues[question] = sources_evaluees

    return resultats_evalues


def calculer_score_global(resultats_evalues: dict) -> float:
    """
    Calcule le score de fiabilite moyen sur l'ensemble des sources collectees.
    Utilise dans le calcul du verdict final.

    Retourne :
        float entre 0 et 1
    """
    tous_les_scores = []
    for sources in resultats_evalues.values():
        for source in sources:
            tous_les_scores.append(source.get("fiabilite", 0.4))

    if not tous_les_scores:
        return 0.4

    return round(sum(tous_les_scores) / len(tous_les_scores), 3)
