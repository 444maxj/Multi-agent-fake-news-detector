# Fake News Detector — Systeme Multi-Agents

Projet academique realise dans le cadre du module SMA Agentic AI.
Verifie automatiquement la veracite d'une affirmation en s'appuyant
sur 5 agents specialises et des sources multiples.

---

## Outils utilises (100% gratuits)

| Outil              | Usage                          | Lien                          |
|--------------------|--------------------------------|-------------------------------|
| Groq Llama 3       | Raisonnement de tous les agents| console.groq.com              |
| Tavily Search API  | Recherche web (1000 req/mois)  | app.tavily.com                |
| Wikipedia API      | Encyclopedie (sans cle)        | wikipedia-api.readthedocs.io  |
| Streamlit          | Interface utilisateur          | streamlit.io                  |

---

## Installation

### 1. Cloner le projet et installer les dependances

```bash
git clone <votre-repo>
cd fake_news_detector
pip install -r requirements.txt
```

### 2. Configurer les cles API

```bash
cp .env.example .env
```

Editez le fichier `.env` et ajoutez vos cles :

```
GROQ_API_KEY=gsk_VOTRE_CLE_ICI    # console.groq.com
TAVILY_API_KEY=tvly-...           # app.tavily.com (gratuit)
```

---

## Utilisation

### Mode interface graphique (recommande pour la demo)

```bash
streamlit run app.py
```

Ouvre automatiquement le navigateur sur http://localhost:8501

### Mode terminal

```bash
python main.py
```

### Tests automatises (5 cas reels)

```bash
python tests.py
```

---

## Architecture des fichiers

```
fake_news_detector/
|
|-- src/
|   |-- factcheck/
|       |-- core/
|       |   |-- orchestrator.py        Coordinateur du pipeline multi-agents
|       |-- agents/
|       |   |-- decomposer.py          Agent 1 : decoupe l'affirmation en sous-questions
|       |   |-- researcher.py          Agent 2 : collecte les sources multi-origines
|       |   |-- evaluator.py           Agent 3 : evalue la fiabilite de chaque source
|       |   |-- analyst.py             Agent 4 : analyse contradictoire pour/contre
|       |   |-- writer.py              Agent 5 : calcule le verdict et redige le rapport
|       |-- tools/
|           |-- web_search.py          Recherche web via Tavily API
|           |-- wikipedia_search.py    Recherche Wikipedia (sans cle)
|
|-- data/
|   |-- source_reliability.json        Referentiel de fiabilite des domaines
|
|-- reports/                           Rapports generes automatiquement
|-- eval/                              Benchmark et evaluation des affirmations
|   |-- benchmark.py
|-- tests/                             Tests unitaires
|   |-- test_evaluator.py
|-- docs/                              Documentation d'architecture
|-- app.py                             Interface Streamlit
|-- main.py                            Mode terminal
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- LICENSE
```

---

## Pipeline de traitement

```
Affirmation utilisateur
       |
       v
[Agent 1] Decomposeur      --> 3 a 5 sous-questions (Chain-of-Thought)
       |
       v
[Agent 2] Chercheur        --> Sources : web + fact-checkers + Wikipedia
       |
       v
[Agent 3] Evaluateur       --> Score de fiabilite par source
       |
       v
[Agent 4] Analyste         --> Arguments pour / contre + contradictions
       |
       v
[Agent 5] Redacteur        --> Verdict + Score de confiance + Rapport
```

---

## Verdicts possibles

| Verdict          | Signification                                        |
|------------------|------------------------------------------------------|
| Vrai             | Sources fiables convergent fortement                 |
| Partiellement vrai | Sources nuancees ou contexte important             |
| Faux             | Sources fiables contredisent l'affirmation           |
| Non verifiable   | Sources insuffisantes ou affirmation trop vague      |

---

## Limites connues

- Dependance a la disponibilite des sources en ligne
- Biais potentiel si les sources web sont elles-memes biaisees
- Affirmations tres recentes (< 24h) peuvent manquer de sources
- Certaines affirmations en langue arabe ou peu courantes sont moins bien couvertes
- Le score de confiance est une heuristique, pas une certitude mathematique
