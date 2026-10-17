"""
Module orchestrateur (conservé pour compatibilité ascendante).
Redirige vers factcheck.core.orchestrator.
"""

import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from factcheck.core.orchestrator import lancer_verification

__all__ = ["lancer_verification"]
