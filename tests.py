"""
Script de test et evaluation.
Redirige vers eval/benchmark.py pour executer la suite de tests.
Lancer avec : python tests.py ou python eval/benchmark.py
"""

import sys
from pathlib import Path

# Ajoute 'src' et la racine au sys.path
ROOT_PATH = Path(__file__).resolve().parent
SRC_PATH = ROOT_PATH / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from eval.benchmark import lancer_tests

if __name__ == "__main__":
    lancer_tests()
