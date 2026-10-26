"""
Agent Analyste Contradictoire avec validation Pydantic et repli sécurisé.
"""

import logging

from factcheck.core.llm_json import call_json
from factcheck.core.logging_setup import traced
from factcheck.core.schemas import Analysis, Source

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es un agent analyste spécialisé en pensée critique et vérification des faits.
Ta mission est d'analyser les preuves documentaires et de produire une analyse bilatérale et objective.

Instructions :
1. Identifie les arguments qui SOUTIENNENT l'affirmation, avec mention de la source.
2. Identifie les arguments qui CONTREDISENT l'affirmation, avec mention de la source.
3. Signale toute contradiction directe entre sources.
4. Évalue la convergence globale des sources : "forte", "modérée", "faible", ou "nulle".

Tu dois répondre UNIQUEMENT par un objet JSON valide conforme au schéma :
{
  "arguments_pour": ["arg 1 (source: ...)", "arg 2"],
  "arguments_contre": ["arg 1 (source: ...)"],
  "contradictions": ["description de contradiction"],
  "convergence": "forte"
}"""


def preparer_contexte(sources: list[Source]) -> str:
    """Formate les meilleures sources en texte lisible pour l'analyse."""
    lignes: list[str] = []
    # Prendre les 8 sources les plus fiables
    for s in sources[:8]:
        rel_pct = int((s.reliability or 0.4) * 100)
        lignes.append(
            f"- [{s.origin}] {s.title} (Fiabilité: {rel_pct}%, Biais: {s.bias})\n"
            f"  URL: {s.url}\n"
            f"  Extrait: {s.content[:350]}...\n"
        )
    return "\n".join(lignes) if lignes else "Aucune source disponible."


@traced("analyst")
def analyst_agent(affirmation: str, sources: list[Source]) -> Analysis:
    """
    Produit une analyse contradictoire à partir des sources évaluées.
    En cas de panne LLM, repli sécurisé sur Analysis(convergence='nulle').
    """
    contexte = preparer_contexte(sources)
    user_prompt = (
        f"Affirmation à analyser : \"{affirmation}\"\n\n"
        f"Sources collectées :\n{contexte}"
    )

    result = call_json(
        schema=Analysis,
        system=SYSTEM_PROMPT,
        user=user_prompt,
        fallback=Analysis(
            arguments_pour=[],
            arguments_contre=[],
            contradictions=[],
            convergence="nulle",
        ),
        temperature=0.0,
    )

    log.info(
        "analysis_completed",
        extra={
            "pour": len(result.arguments_pour),
            "contre": len(result.arguments_contre),
            "convergence": result.convergence,
        },
    )
    return result
