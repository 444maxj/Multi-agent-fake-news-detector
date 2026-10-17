"""
Agent Decomposeur.
Analyse une affirmation et la decoupe en 3 a 5 sous-questions verificables
en utilisant le raisonnement Chain-of-Thought.
"""

import json
from factcheck.core.llm import call_groq_chat


def decomposer_agent(affirmation: str) -> list:
    """
    Transforme une affirmation en sous-questions verificables.

    Parametres :
        affirmation : l'affirmation brute soumise par l'utilisateur

    Retourne :
        liste de strings (sous-questions)
    """
    prompt = f"""Tu es un agent specialise en decomposition d'affirmations pour le fact-checking.

Affirmation a analyser : "{affirmation}"

Etape 1 : Identifie les elements factuels cles de cette affirmation
          (chiffres, dates, personnes, evenements, causalites).

Etape 2 : Pour chaque element, formule une sous-question precise et independante
          qui peut etre verifiee par une recherche documentaire.

Regles :
- Entre 3 et 5 sous-questions maximum
- Chaque question doit etre autonome et recherchable
- Eviter les questions trop vagues ou trop larges
- Privilegier les questions qui ont une reponse factuelle claire

Reponds UNIQUEMENT avec un tableau JSON de strings, sans texte supplementaire.
Format attendu : ["question 1", "question 2", "question 3"]"""

    texte = call_groq_chat(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.0
    )

    # Nettoyage des balises markdown si presentes
    if "```" in texte:
        texte = texte.split("```")[1]
        if texte.startswith("json"):
            texte = texte[4:]

    try:
        sous_questions = json.loads(texte.strip())
        # Validation : s'assurer que c'est bien une liste de strings
        if not isinstance(sous_questions, list):
            raise ValueError("Le resultat n'est pas une liste")
        return sous_questions
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[ERREUR decomposer] Impossible de parser la reponse : {e}")
        # Fallback : retourner l'affirmation comme unique question
        return [affirmation]
