"""
Agent Analyste Contradictoire.
Analyse les sources collectees et produit une synthese structuree
avec arguments pour et contre l'affirmation, meme si les sources convergent.
Force un regard critique bilateral pour eviter les biais de confirmation.
"""

import json
from factcheck.core.llm import call_groq_chat


def preparer_contexte(resultats_evalues: dict) -> str:
    """
    Formate les sources evaluees en texte lisible pour le prompt.
    Limite la taille pour rester dans la fenetre de contexte.

    Retourne :
        string formate avec les sources les plus fiables de chaque question
    """
    lignes = []
    for question, sources in resultats_evalues.items():
        lignes.append(f"\nQuestion : {question}")
        # Prendre les 3 sources les plus fiables par question
        for source in sources[:3]:
            fiabilite_pct = int(source["fiabilite"] * 100)
            lignes.append(
                f"  Source ({source['type_source']}, fiabilite {fiabilite_pct}%) : "
                f"{source['titre']}\n"
                f"  Contenu : {source['contenu'][:400]}...\n"
                f"  URL : {source['url']}"
            )
    return "\n".join(lignes)


def analyst_agent(affirmation: str, resultats_evalues: dict) -> dict:
    """
    Produit une analyse contradictoire a partir des sources collectees.

    Parametres :
        affirmation      : l'affirmation originale de l'utilisateur
        resultats_evalues: sortie de l'agent evaluateur

    Retourne :
        dictionnaire avec cles :
        - arguments_pour   : liste de strings
        - arguments_contre : liste de strings
        - contradictions   : liste de strings
        - convergence      : "forte" | "moderee" | "faible" | "nulle"
    """
    contexte = preparer_contexte(resultats_evalues)

    prompt = f"""Tu es un agent analyste specialise en pensee critique et verification des faits.

Affirmation a analyser : "{affirmation}"

Sources collectees (classees par fiabilite) :
{contexte}

Ta mission est de produire une analyse BILATERALE et OBJECTIVE.

Instructions obligatoires :
1. Identifie les arguments qui SOUTIENNENT l'affirmation, avec la source correspondante.
2. Identifie les arguments qui CONTREDISENT l'affirmation, avec la source correspondante.
3. Si les sources semblent converger, cherche activement les nuances, contextes differents,
   exceptions, ou interpretations alternatives avant de conclure.
4. Signale toute contradiction entre sources.
5. Evalue le degre de convergence globale des sources.

IMPORTANT : Meme si l'affirmation semble clairement vraie ou fausse, tu DOIS presenter
les deux cotes. La rigueur journalistique l'exige.

Reponds UNIQUEMENT en JSON valide avec cette structure exacte, sans texte autour :
{{
    "arguments_pour": [
        "argument 1 (source : nom de la source)",
        "argument 2 (source : nom de la source)"
    ],
    "arguments_contre": [
        "argument 1 (source : nom de la source)",
        "argument 2 (source : nom de la source)"
    ],
    "contradictions": [
        "description d'une contradiction entre sources",
        "autre contradiction si applicable"
    ],
    "convergence": "forte"
}}

Valeurs possibles pour convergence : "forte", "moderee", "faible", "nulle"."""

    texte = call_groq_chat(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.0
    )

    # Nettoyage des balises markdown eventuelles
    if "```" in texte:
        texte = texte.split("```")[1]
        if texte.startswith("json"):
            texte = texte[4:]

    try:
        analyse = json.loads(texte.strip())
        # Validation des cles obligatoires
        for cle in ["arguments_pour", "arguments_contre", "contradictions", "convergence"]:
            if cle not in analyse:
                analyse[cle] = [] if cle != "convergence" else "faible"
        return analyse
    except json.JSONDecodeError as e:
        print(f"[ERREUR analyst] Impossible de parser la reponse JSON : {e}")
        # Retour minimal en cas d'erreur
        return {
            "arguments_pour":   ["Analyse indisponible en raison d'une erreur technique"],
            "arguments_contre": ["Analyse indisponible en raison d'une erreur technique"],
            "contradictions":   [],
            "convergence":      "nulle"
        }
