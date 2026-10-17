"""
Agent Chercheur Multi-Sources.
Pour chaque sous-question, collecte des sources depuis le web general,
les fact-checkers specialises et Wikipedia.
Effectue la deduplication par URL.
"""

from factcheck.tools.web_search import recherche_web, recherche_fact_checkers
from factcheck.tools.wikipedia_search import recherche_wikipedia


def researcher_agent(sous_questions: list) -> dict:
    """
    Collecte des sources pour chaque sous-question depuis plusieurs origines.

    Parametres :
        sous_questions : liste de questions generees par l'agent decomposeur

    Retourne :
        dictionnaire { question -> liste de sources }
        chaque source est un dict { url, titre, contenu, domaine }
    """
    resultats_complets = {}

    for question in sous_questions:
        sources_brutes = []

        # --- Source 1 : Recherche web generale ---
        sources_web = recherche_web(question, max_results=4)
        sources_brutes.extend(sources_web)

        # --- Source 2 : Fact-checkers specialises ---
        sources_fc = recherche_fact_checkers(question)
        sources_brutes.extend(sources_fc)

        # --- Source 3 : Wikipedia (gratuit, sans cle) ---
        source_wiki = recherche_wikipedia(question)
        if source_wiki:
            sources_brutes.append(source_wiki)

        # --- Deduplication par URL ---
        urls_vues = set()
        sources_uniques = []
        for source in sources_brutes:
            url = source.get("url", "")
            if url and url not in urls_vues:
                urls_vues.add(url)
                sources_uniques.append(source)

        # Filtrer les sources sans contenu utile
        sources_filtrees = [
            s for s in sources_uniques
            if len(s.get("contenu", "")) > 50
        ]

        resultats_complets[question] = sources_filtrees
        print(f"     [{len(sources_filtrees)} sources] {question[:60]}...")

    return resultats_complets
