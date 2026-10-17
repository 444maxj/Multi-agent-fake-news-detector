"""
Outil de recherche web utilisant l'API Tavily (gratuite, 1000 req/mois).
Retourne une liste de sources avec url, titre, contenu et domaine.
"""

import os
from tavily import TavilyClient


def get_client():
    """
    Initialise le client Tavily avec la cle depuis les variables d'environnement.
    Leve une erreur claire si la cle est absente.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "TAVILY_API_KEY manquante. Creez un compte gratuit sur app.tavily.com"
        )
    return TavilyClient(api_key=api_key)


def extraire_domaine(url: str) -> str:
    """
    Extrait le nom de domaine depuis une URL complete.
    Exemple : 'https://www.lemonde.fr/article' -> 'lemonde.fr'
    """
    try:
        parties = url.replace("https://", "").replace("http://", "").split("/")
        domaine = parties[0].replace("www.", "")
        return domaine
    except Exception:
        return ""


def recherche_web(query: str, max_results: int = 5) -> list:
    """
    Effectue une recherche web via Tavily et retourne les resultats normalises.

    Parametres :
        query       : la question ou requete a rechercher
        max_results : nombre maximum de resultats (defaut 5)

    Retourne :
        liste de dictionnaires { url, titre, contenu, domaine }
    """
    client = get_client()

    try:
        reponse = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic"   # "basic" est inclus dans le plan gratuit
        )
    except Exception as e:
        print(f"[ERREUR recherche_web] {e}")
        return []

    sources = []
    for resultat in reponse.get("results", []):
        url = resultat.get("url", "")
        sources.append({
            "url":     url,
            "titre":   resultat.get("title", "Sans titre"),
            "contenu": resultat.get("content", "")[:1500],  # limite la taille
            "domaine": extraire_domaine(url)
        })

    return sources


def recherche_fact_checkers(query: str) -> list:
    """
    Recherche specifiquement sur les sites de fact-checking reconnus.
    Utilise les operateurs de recherche Tavily pour cibler ces domaines.
    """
    query_ciblee = f"{query} fact check verification"
    return recherche_web(query_ciblee, max_results=3)
