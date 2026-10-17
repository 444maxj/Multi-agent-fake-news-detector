"""
Helper pour les appels Groq avec sélection et repli automatique de modèle.
"""

import os
import groq
from factcheck.core.config import FALLBACK_GROQ_MODELS


def call_groq_chat(messages: list, max_tokens: int = 2000, temperature: float = 0.0) -> str:
    """
    Execute un appel chat completion sur Groq en testant les modeles disponibles.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY manquante. Obtenez une cle sur console.groq.com"
        )
    client = groq.Groq(api_key=api_key)

    dernier_erreur = None
    for modele in FALLBACK_GROQ_MODELS:
        try:
            reponse = client.chat.completions.create(
                model=modele,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return reponse.choices[0].message.content.strip()
        except Exception as e:
            if "does not exist" in str(e) or "model_not_found" in str(e) or "NotFoundError" in type(e).__name__:
                dernier_erreur = e
                continue
            raise e

    if dernier_erreur:
        raise dernier_erreur
    raise RuntimeError("Aucun modele Groq n'a pu repondre.")
