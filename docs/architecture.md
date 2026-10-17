# Architecture & System Design — Fake News Detector

## Overview

The **Fake News Detector** is a multi-agent fact-checking system utilizing Groq-accelerated LLMs (Llama 3.3 70B), Tavily Search API, and Wikipedia.

## Directory Layout

```
fake_news_detector/
├── .env.example              # Template for API keys
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
├── README.md                 # Project documentation
├── requirements.txt          # Pinned runtime and dev dependencies
├── app.py                    # Streamlit web application
├── main.py                   # Terminal entrypoint
│
├── src/
│   └── factcheck/
│       ├── __init__.py
│       ├── core/             # Orchestration and pipeline flow
│       │   ├── __init__.py
│       │   └── orchestrator.py
│       ├── agents/           # Specialized autonomous agents
│       │   ├── __init__.py
│       │   ├── decomposer.py # Decomposes claim into sub-questions (Chain-of-Thought)
│       │   ├── researcher.py # Multi-source retrieval & deduplication
│       │   ├── evaluator.py  # Source credibility scoring
│       │   ├── analyst.py    # Bilateral counter-analysis (pro/con/contradictions)
│       │   └── writer.py     # Heuristic verdict calculation & report drafting
│       └── tools/            # External retrieval tools
│           ├── __init__.py
│           ├── web_search.py # Tavily search API wrapper
│           └── wikipedia_search.py # Wikipedia API wrapper
│
├── data/                     # Data assets (source credibility reference)
│   └── source_reliability.json
├── eval/                     # Evaluation benchmarks and validation cases
│   ├── __init__.py
│   └── benchmark.py
├── tests/                    # Unit tests
│   ├── __init__.py
│   └── test_evaluator.py
├── reports/                  # Generated fact-checking reports
└── docs/                     # Architectural documentation
```

## Agent Pipeline Flow

1. **Decomposer (`factcheck.agents.decomposer`)**: Takes the raw user claim and breaks it down into 3-5 factual, distinct, and searchable sub-questions.
2. **Researcher (`factcheck.agents.researcher`)**: For each sub-question, queries Tavily for web results, specialized fact-checker websites, and Wikipedia. Deduplicates and cleans results.
3. **Evaluator (`factcheck.agents.evaluator`)**: Scores source credibility based on `data/source_reliability.json` and sorts results by trustworthiness.
4. **Analyst (`factcheck.agents.analyst`)**: Examines evidence bilaterally, extracting supporting arguments, counter-arguments, and noting source contradictions.
5. **Writer (`factcheck.agents.writer`)**: Applies the multi-criteria verdict heuristic and writes a structured fact-checking report in Markdown.
