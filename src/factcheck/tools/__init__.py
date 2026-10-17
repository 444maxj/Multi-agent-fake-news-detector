"""
External retrieval tools for web and encyclopedia searches.
"""

from factcheck.tools.web_search import recherche_web, recherche_fact_checkers
from factcheck.tools.wikipedia_search import recherche_wikipedia

__all__ = ["recherche_web", "recherche_fact_checkers", "recherche_wikipedia"]
