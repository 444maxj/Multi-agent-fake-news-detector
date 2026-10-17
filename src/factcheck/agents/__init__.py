"""
Autonomous specialized agents for the fact-checking pipeline.
"""

from factcheck.agents.decomposer import decomposer_agent
from factcheck.agents.researcher import researcher_agent
from factcheck.agents.evaluator import evaluator_agent
from factcheck.agents.analyst import analyst_agent
from factcheck.agents.writer import writer_agent

__all__ = [
    "decomposer_agent",
    "researcher_agent",
    "evaluator_agent",
    "analyst_agent",
    "writer_agent",
]
