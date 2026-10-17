"""
Point d'entree en mode terminal (sans interface graphique).
Utile pour tester le pipeline rapidement ou pour les tests automatises.
Lancer avec : python main.py
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Reconfiguration de stdout/stderr pour supporter l'UTF-8 sur consoles Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ajoute 'src' au sys.path pour acceder au package factcheck
SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from factcheck.core.orchestrator import lancer_verification

# Chargement du fichier .env s'il existe
load_dotenv()


def verifier_configuration():
    """
    Verifie que les cles API obligatoires sont presentes.
    Affiche un message d'aide clair si elles manquent.
    """
    manquantes = []
    if not os.getenv("GROQ_API_KEY"):
        manquantes.append("GROQ_API_KEY (console.groq.com — gratuit)")
    if not os.getenv("TAVILY_API_KEY"):
        manquantes.append("TAVILY_API_KEY (app.tavily.com — gratuit)")

    if manquantes:
        print("\nERREUR : Cles API manquantes dans le fichier .env :")
        for cle in manquantes:
            print(f"  - {cle}")
        print("\nCopiez .env.example vers .env et renseignez vos cles.")
        return False
    return True


def sauvegarder_rapport(resultat: dict):
    """
    Sauvegarde le rapport dans le dossier reports/ avec un nom base sur le temps.
    """
    os.makedirs("reports", exist_ok=True)
    import time
    nom_fichier = f"reports/rapport_{int(time.time())}.json"
    with open(nom_fichier, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Rapport sauvegarde : {nom_fichier}")


if __name__ == "__main__":

    print("=" * 60)
    print("   FAKE NEWS DETECTOR — Systeme Multi-Agents")
    print("=" * 60)

    if not verifier_configuration():
        sys.exit(1)

    # Saisie de l'affirmation (soit via argument CLI, soit via prompt interactif)
    print()
    if len(sys.argv) > 1:
        affirmation = " ".join(sys.argv[1:]).strip()
        print(f"Affirmation a verifier : {affirmation}")
    else:
        affirmation = input("Entrez une affirmation a verifier : ").strip()

    if not affirmation:
        print("Aucune affirmation saisie. Arrêt.")
        sys.exit(0)

    print()
    print("-" * 60)

    # Lancement du pipeline
    resultat = lancer_verification(affirmation)

    # Affichage du verdict
    print()
    print("=" * 60)
    print(f"  VERDICT    : {resultat['verdict']}")
    print(f"  CONFIANCE  : {int(resultat['confiance'] * 100)}%")
    print(f"  SOURCES    : {resultat['nb_sources']} collectees")
    print("=" * 60)
    print()
    print(resultat["rapport_texte"])

    # Sauvegarde automatique
    sauvegarder_rapport(resultat)
