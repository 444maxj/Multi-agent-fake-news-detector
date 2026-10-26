"""
Agent Décomposeur avec validation Pydantic et repli sécurisé.
"""

import logging

from factcheck.core.llm_json import call_json
from factcheck.core.logging_setup import traced
from factcheck.core.schemas import SubQuestions

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es un agent expert en décomposition d'affirmations pour le fact-checking.
Ta mission est d'analyser l'affirmation et d'en extraire entre 2 et 5 sous-questions vérifiables,
précises, indépendantes et cherchables dans des bases documentaires.
Réponds au format JSON avec la clé 'questions' contenant la liste des sous-questions.
Exemple : {"questions": ["question 1", "question 2"]}"""


@traced("decomposer")
def decomposer_agent(affirmation: str) -> list[str]:
    """
    Transforme une affirmation en sous-questions vérifiables.
    En cas d'échec ou d'erreur LLM, repli sur l'affirmation brute.
    """
    user_prompt = f"Affirmation à analyser : \"{affirmation}\""

    result = call_json(
        schema=SubQuestions,
        system=SYSTEM_PROMPT,
        user=user_prompt,
        list_key="questions",
        fallback=SubQuestions(questions=[affirmation]),
        temperature=0.0,
    )

    log.info("decomposition_done", extra={"count": len(result.questions)})
    return result.questions
