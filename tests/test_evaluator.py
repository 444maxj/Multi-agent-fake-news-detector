"""
Tests unitaires pour l'evaluateur de sources et le calcul de fiabilite.
"""

import sys
from pathlib import Path

# Ajoute 'src' au sys.path pour importer factcheck
SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from factcheck.agents.evaluator import evaluer_domaine, calculer_score_global, evaluator_agent
from factcheck.agents.writer import calculer_verdict


def test_evaluer_domaine_connu():
    resultat = evaluer_domaine("lemonde.fr")
    assert resultat["score"] > 0.8
    assert resultat["type"] == "presse_etablie"


def test_evaluer_domaine_sous_domaine():
    resultat = evaluer_domaine("fr.wikipedia.org")
    assert resultat["score"] == 0.75
    assert resultat["type"] == "encyclopedie"


def test_evaluer_domaine_inconnu():
    resultat = evaluer_domaine("random-unverified-blog.xyz")
    assert resultat["score"] == 0.40
    assert resultat["type"] == "source_inconnue"


def test_calculer_score_global():
    resultats_evalues = {
        "q1": [
            {"fiabilite": 0.90},
            {"fiabilite": 0.80}
        ]
    }
    score = calculer_score_global(resultats_evalues)
    assert score == 0.85


def test_calculer_verdict_faux():
    analyse = {
        "arguments_pour": [],
        "arguments_contre": ["Contre 1", "Contre 2"],
        "contradictions": [],
        "convergence": "forte"
    }
    resultats_evalues = {
        "q1": [{"fiabilite": 0.90}]
    }
    verdict = calculer_verdict(analyse, resultats_evalues)
    assert verdict["verdict"] == "Faux"


def test_calculer_verdict_vrai():
    analyse = {
        "arguments_pour": ["Pour 1", "Pour 2", "Pour 3"],
        "arguments_contre": [],
        "contradictions": [],
        "convergence": "forte"
    }
    resultats_evalues = {
        "q1": [{"fiabilite": 0.95}]
    }
    verdict = calculer_verdict(analyse, resultats_evalues)
    assert verdict["verdict"] == "Vrai"


if __name__ == "__main__":
    test_evaluer_domaine_connu()
    test_evaluer_domaine_sous_domaine()
    test_evaluer_domaine_inconnu()
    test_calculer_score_global()
    test_calculer_verdict_faux()
    test_calculer_verdict_vrai()
    print("[OK] Tous les tests unitaires ont reussi.")
