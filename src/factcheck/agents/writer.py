"""
Agent Redacteur.
Calcule le verdict final selon une heuristique multi-criteres
et redige un rapport de fact-checking structure et cite.
"""

import json
from factcheck.agents.evaluator import calculer_score_global
from factcheck.core.llm import call_groq_chat


# Table de correspondance convergence -> poids multiplicateur
POIDS_CONVERGENCE = {
    "forte":   1.0,
    "moderee": 0.75,
    "faible":  0.50,
    "nulle":   0.30
}


def calculer_verdict(analyse: dict, resultats_evalues: dict) -> dict:
    """
    Calcule le verdict et le score de confiance selon une heuristique explicite.

    Logique :
        - Ratio arguments pour / total des arguments
        - Qualite moyenne des sources (score de fiabilite)
        - Degre de convergence entre les sources

    Retourne :
        dict { verdict, confiance, explication_heuristique }
    """
    score_sources  = calculer_score_global(resultats_evalues)
    convergence    = analyse.get("convergence", "faible")
    poids          = POIDS_CONVERGENCE.get(convergence, 0.5)

    nb_pour        = len(analyse.get("arguments_pour", []))
    nb_contre      = len(analyse.get("arguments_contre", []))
    total          = nb_pour + nb_contre

    # Calcul du ratio de soutien (proportion d'arguments favorables)
    if total == 0:
        ratio_pour = 0.5   # cas degenere : aucun argument de part et d'autre
    else:
        ratio_pour = nb_pour / total

    # Score de confiance combine : qualite sources x convergence x ratio
    confiance_brute = score_sources * poids * (0.5 + ratio_pour * 0.5)
    confiance       = round(min(confiance_brute, 0.99), 2)   # plafonner a 99%

    # Determination du verdict selon les seuils
    if total == 0 or (nb_pour == 0 and nb_contre == 0):
        verdict = "Non verifiable"
    elif ratio_pour >= 0.75 and convergence in ("forte", "moderee"):
        verdict = "Vrai"
    elif ratio_pour >= 0.55:
        verdict = "Partiellement vrai"
    elif ratio_pour <= 0.25:
        verdict = "Faux"
    else:
        verdict = "Partiellement vrai"

    explication = (
        f"{nb_pour} argument(s) pour, {nb_contre} contre, "
        f"convergence {convergence}, "
        f"qualite moyenne des sources {int(score_sources * 100)}%"
    )

    return {
        "verdict":                 verdict,
        "confiance":               confiance,
        "explication_heuristique": explication
    }


def formatter_sources_citees(resultats_evalues: dict) -> str:
    """
    Prepare la liste des sources uniques pour le rapport final.
    Retourne une chaine formatee avec les sources les plus fiables.
    """
    sources_vues = set()
    lignes        = []

    for sources in resultats_evalues.values():
        for source in sources[:2]:   # 2 meilleures sources par question
            url = source.get("url", "")
            if url and url not in sources_vues:
                sources_vues.add(url)
                fiabilite_pct = int(source.get("fiabilite", 0) * 100)
                biais         = source.get("biais", "inconnu")
                lignes.append(
                    f"- {source.get('titre', 'Sans titre')} "
                    f"| Fiabilite : {fiabilite_pct}% | Biais : {biais} "
                    f"| URL : {url}"
                )

    return "\n".join(lignes) if lignes else "Aucune source disponible"


def writer_agent(affirmation: str, analyse: dict, resultats_evalues: dict) -> dict:
    """
    Redige le rapport final de fact-checking.

    Parametres :
        affirmation      : l'affirmation originale
        analyse          : sortie de l'agent analyste contradictoire
        resultats_evalues: sortie de l'agent evaluateur

    Retourne :
        dictionnaire {
            verdict      : str,
            confiance    : float,
            rapport_texte: str   (rapport complet en markdown)
        }
    """
    calcul_verdict = calculer_verdict(analyse, resultats_evalues)
    sources_citees = formatter_sources_citees(resultats_evalues)

    prompt = f"""Tu es un journaliste-verificateur professionnel. Redige un rapport de fact-checking.

Affirmation verifiee : "{affirmation}"

Donnees de l'analyse :
- Arguments pour l'affirmation : {json.dumps(analyse.get('arguments_pour', []), ensure_ascii=False)}
- Arguments contre l'affirmation : {json.dumps(analyse.get('arguments_contre', []), ensure_ascii=False)}
- Contradictions detectees : {json.dumps(analyse.get('contradictions', []), ensure_ascii=False)}
- Convergence des sources : {analyse.get('convergence', 'inconnue')}

Verdict calcule : {calcul_verdict['verdict']}
Score de confiance : {int(calcul_verdict['confiance'] * 100)}%
Methode de calcul : {calcul_verdict['explication_heuristique']}

Sources consultees :
{sources_citees}

Redige un rapport STRUCTURE, NEUTRE et DOCUMENTE en suivant ce plan exact :

## Affirmation verifiee
[Repeter l'affirmation telle quelle]

## Contexte
[2-3 phrases de mise en contexte]

## Preuves en faveur
[Liste des arguments qui soutiennent, avec sources citees]

## Preuves contre
[Liste des arguments qui contredisent, avec sources citees]

## Contradictions entre sources
[Decrire les contradictions detectees ou indiquer leur absence]

## Verdict : {calcul_verdict['verdict']} — Confiance : {int(calcul_verdict['confiance'] * 100)}%
[Synthese argumentee du verdict en 3-5 phrases]

## Sources consultees
[Liste des sources avec leur niveau de fiabilite]

Le rapport doit etre accessible a un lecteur non specialiste, neutre et bien cite."""

    rapport_texte = call_groq_chat(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.0
    )

    return {
        "verdict":       calcul_verdict["verdict"],
        "confiance":     calcul_verdict["confiance"],
        "rapport_texte": rapport_texte
    }
