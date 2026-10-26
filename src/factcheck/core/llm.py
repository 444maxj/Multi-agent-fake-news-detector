"""
Fournisseur client LLM utilisant l'API OpenAI compatible avec Groq.
"""

import os

from openai import OpenAI

from factcheck.core.config import get_groq_model


def get_client() -> tuple[OpenAI, str]:
    """
    Initialise le client OpenAI pointant vers l'API Groq (endpoint compatible).
    Retourne (client, nom_du_modele).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise OSError(
            "GROQ_API_KEY manquante. Renseignez votre cle dans le fichier .env (console.groq.com)."
        )

    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    model = get_groq_model()
    return client, model
