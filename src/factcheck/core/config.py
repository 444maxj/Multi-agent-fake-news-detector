"""
Configuration centralisée du système FactCheck.
"""

import os
from pathlib import Path

# Chemins de base du projet
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Modèle Groq (priorité : variable d'environnement GROQ_MODEL, sinon modèle de pointe disponible)
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
FALLBACK_GROQ_MODELS = [
    DEFAULT_GROQ_MODEL,
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile"
]


def get_groq_model() -> str:
    """Retourne le modèle Groq configuré."""
    return os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
