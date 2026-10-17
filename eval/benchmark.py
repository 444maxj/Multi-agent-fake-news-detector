"""
Script d'evaluation et benchmark sur 5 affirmations reelles.
Permet d'evaluer la justesse du systeme et de generer un bilan de performance.
Lancer avec : python eval/benchmark.py
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Ajoute 'src' au sys.path si necessaire
SRC_PATH = Path(__file__).resolve().parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from factcheck.core.orchestrator import lancer_verification

load_dotenv()

# Banque de 5 affirmations avec verdict attendu pour evaluation
CAS_DE_TEST = [
    {
        "affirmation":     "La Tour Eiffel mesure 400 metres de hauteur",
        "verdict_attendu": "Faux",
        "note":            "La Tour Eiffel mesure environ 330 metres avec antenne"
    },
    {
        "affirmation":     "Les vaccins COVID-19 contiennent des micropuces electroniques",
        "verdict_attendu": "Faux",
        "note":            "Theorie du complot refutee par de nombreux fact-checkers"
    },
    {
        "affirmation":     "La consommation reguliere de cafe reduit le risque de diabete de type 2",
        "verdict_attendu": "Partiellement vrai",
        "note":            "Des etudes montrent une correlation mais pas de causalite etablie"
    },
    {
        "affirmation":     "L'intelligence artificielle va remplacer tous les emplois humains d'ici 2030",
        "verdict_attendu": "Partiellement vrai",
        "note":            "Transformation de nombreux emplois mais pas suppression totale"
    },
    {
        "affirmation":     "Le Maroc organisera la Coupe du Monde de football en 2030",
        "verdict_attendu": "Vrai",
        "note":            "Decision FIFA confirmee pour le centenaire de la Coupe du Monde"
    }
]


def evaluer_justesse(verdict_obtenu: str, verdict_attendu: str) -> bool:
    """
    Verifie si le verdict obtenu correspond au verdict attendu.
    Tolerance : 'Partiellement vrai' accepte aussi 'Vrai' et vice versa.
    """
    if verdict_obtenu == verdict_attendu:
        return True
    # Tolerance pour les cas ambigus
    proches = {"Partiellement vrai", "Vrai"}
    if verdict_obtenu in proches and verdict_attendu in proches:
        return True
    return False


def lancer_tests():
    """
    Execute les 5 cas de test et affiche un bilan de performance.
    Sauvegarde les rapports individuels dans reports/tests/
    """
    os.makedirs("reports/tests", exist_ok=True)

    resultats_tests  = []
    nb_corrects      = 0

    print("=" * 70)
    print("   BENCHMARK EVALUATION — Fake News Detector")
    print(f"   {len(CAS_DE_TEST)} affirmations a evaluer")
    print("=" * 70)

    for i, cas in enumerate(CAS_DE_TEST, 1):
        affirmation     = cas["affirmation"]
        attendu         = cas["verdict_attendu"]

        print(f"\n[Test {i}/{len(CAS_DE_TEST)}] {affirmation[:60]}...")
        print(f"  Verdict attendu : {attendu}")

        debut = time.time()

        try:
            resultat = lancer_verification(affirmation)
            duree    = round(time.time() - debut, 1)

            obtenu  = resultat["verdict"]
            correct = evaluer_justesse(obtenu, attendu)

            if correct:
                nb_corrects += 1
                statut = "OK"
            else:
                statut = "DIFFERENT"

            print(f"  Verdict obtenu  : {obtenu} ({int(resultat['confiance'] * 100)}% confiance)")
            print(f"  Statut          : {statut} ({duree}s)")

            # Sauvegarde du rapport individuel
            nom_fichier = f"reports/tests/test_{i}_{statut.lower()}.json"
            with open(nom_fichier, "w", encoding="utf-8") as f:
                json.dump({
                    "cas":             cas,
                    "resultat":        resultat,
                    "statut":          statut,
                    "duree_secondes":  duree
                }, f, ensure_ascii=False, indent=2)

            resultats_tests.append({
                "affirmation":     affirmation,
                "attendu":         attendu,
                "obtenu":          obtenu,
                "correct":         correct,
                "confiance":       resultat["confiance"],
                "duree":           duree
            })

        except Exception as e:
            print(f"  ERREUR : {e}")
            resultats_tests.append({
                "affirmation": affirmation,
                "attendu":     attendu,
                "obtenu":      "ERREUR",
                "correct":     False,
                "erreur":      str(e)
            })

    # ---------------------------------------------------------------------------
    # Bilan final
    # ---------------------------------------------------------------------------
    print()
    print("=" * 70)
    print(f"   BILAN FINAL : {nb_corrects}/{len(CAS_DE_TEST)} verdicts corrects")
    precision = round(nb_corrects / len(CAS_DE_TEST) * 100)
    print(f"   Precision   : {precision}%")
    print("=" * 70)

    # Sauvegarde du bilan global
    bilan = {
        "date":                  time.strftime("%Y-%m-%d %H:%M"),
        "nb_tests":              len(CAS_DE_TEST),
        "nb_corrects":           nb_corrects,
        "precision_pct":         precision,
        "detail":                resultats_tests
    }
    with open("reports/bilan_tests.json", "w", encoding="utf-8") as f:
        json.dump(bilan, f, ensure_ascii=False, indent=2)

    print("\n[OK] Bilan sauvegarde dans reports/bilan_tests.json")
    return bilan


if __name__ == "__main__":
    lancer_tests()
