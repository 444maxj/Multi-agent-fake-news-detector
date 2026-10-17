"""
Orchestrateur principal du systeme multi-agents.
Coordonne l'execution sequentielle des 5 agents dans l'ordre logique
et retourne le rapport final avec le verdict.
"""

from factcheck.agents.decomposer import decomposer_agent
from factcheck.agents.researcher import researcher_agent
from factcheck.agents.evaluator import evaluator_agent
from factcheck.agents.analyst import analyst_agent
from factcheck.agents.writer import writer_agent


def lancer_verification(affirmation: str, callback_etape=None) -> dict:
    """
    Pipeline complet de verification d'une affirmation.

    Parametres :
        affirmation    : l'affirmation soumise par l'utilisateur
        callback_etape : fonction optionnelle appelee a chaque etape
                         avec (numero: int, description: str) pour afficher la progression

    Retourne :
        dictionnaire {
            affirmation       : str,
            sous_questions    : list,
            nb_sources        : int,
            analyse           : dict,
            verdict           : str,
            confiance         : float,
            rapport_texte     : str
        }
    """

    def notifier(numero: int, description: str):
        """Appelle le callback si fourni, sinon affiche dans la console."""
        if callback_etape:
            callback_etape(numero, description)
        else:
            print(f"[{numero}/5] {description}")

    # --- Etape 1 : Decomposition de l'affirmation ---
    notifier(1, "Decomposition de l'affirmation en sous-questions...")
    sous_questions = decomposer_agent(affirmation)
    print(f"     {len(sous_questions)} sous-question(s) generee(s)")

    # --- Etape 2 : Recherche multi-sources ---
    notifier(2, "Recherche multi-sources en cours...")
    resultats_bruts = researcher_agent(sous_questions)
    nb_sources = sum(len(v) for v in resultats_bruts.values())
    print(f"     {nb_sources} source(s) collectee(s)")

    # --- Etape 3 : Evaluation de la fiabilite ---
    notifier(3, "Evaluation de la fiabilite des sources...")
    resultats_evalues = evaluator_agent(resultats_bruts)

    # --- Etape 4 : Analyse contradictoire ---
    notifier(4, "Analyse contradictoire (pour / contre)...")
    analyse = analyst_agent(affirmation, resultats_evalues)
    print(
        f"     {len(analyse.get('arguments_pour', []))} argument(s) pour, "
        f"{len(analyse.get('arguments_contre', []))} contre"
    )

    # --- Etape 5 : Redaction du rapport final ---
    notifier(5, "Redaction du rapport final...")
    resultat_final = writer_agent(affirmation, analyse, resultats_evalues)

    return {
        "affirmation":    affirmation,
        "sous_questions": sous_questions,
        "nb_sources":     nb_sources,
        "analyse":        analyse,
        "verdict":        resultat_final["verdict"],
        "confiance":      resultat_final["confiance"],
        "rapport_texte":  resultat_final["rapport_texte"]
    }
