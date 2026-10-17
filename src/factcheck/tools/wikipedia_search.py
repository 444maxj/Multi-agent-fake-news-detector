"""
Outil de recherche Wikipedia utilisant l'API officielle (gratuite, sans cle).
Supporte le francais et l'anglais selon la disponibilite de l'article.
"""

import wikipediaapi


def get_wiki(langue: str = "fr"):
    """
    Initialise le client Wikipedia avec un user-agent obligatoire.
    """
    return wikipediaapi.Wikipedia(
        language=langue,
        user_agent="FakeNewsDetector/1.0 (projet academique)"
    )


def recherche_wikipedia(query: str) -> dict:
    """
    Recherche un article Wikipedia en francais, puis en anglais si absent.

    Parametres :
        query : terme ou phrase a rechercher

    Retourne :
        dictionnaire { url, titre, contenu, domaine } ou dict vide si non trouve
    """
    # Tentative en francais d'abord
    wiki_fr = get_wiki("fr")
    page = wiki_fr.page(query)

    if not page.exists():
        # Repli sur l'anglais si l'article n'existe pas en francais
        wiki_en = get_wiki("en")
        page = wiki_en.page(query)

    if not page.exists():
        return {}

    return {
        "url":     page.fullurl,
        "titre":   page.title,
        "contenu": page.summary[:2000],   # resume suffisant pour l'analyse
        "domaine": "wikipedia.org"
    }


def recherche_wikipedia_sections(query: str) -> list:
    """
    Retourne plusieurs resultats Wikipedia en cherchant les sections pertinentes.
    Utile quand la requete est vague et peut correspondre a plusieurs articles.
    """
    mots_cles = query.split()[:3]    # utilise les 3 premiers mots comme cles
    resultats = []

    for mot in mots_cles:
        res = recherche_wikipedia(mot)
        if res and res not in resultats:
            resultats.append(res)

    return resultats
