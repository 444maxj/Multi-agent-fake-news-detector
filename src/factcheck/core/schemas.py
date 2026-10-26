"""
Pydantic schemas for the FactCheck multi-agent pipeline.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Convergence = Literal["forte", "modérée", "faible", "nulle"]
VerdictLabel = Literal["Vrai", "Faux", "Partiellement vrai", "Non vérifiable"]


class SubQuestions(BaseModel):
    questions: list[str] = Field(min_length=1, max_length=6)

    @field_validator("questions")
    @classmethod
    def strip_empty(cls, v: list[str]) -> list[str]:
        v = [q.strip() for q in v if q.strip()]
        if not v:
            raise ValueError("no non-empty questions")
        return v


class Source(BaseModel):
    url: str
    title: str = ""
    content: str
    origin: Literal["web", "factcheck", "wikipedia"] = "web"
    reliability: float | None = Field(default=None, ge=0, le=1)
    bias: str | None = None
    source_type: str | None = None


class Analysis(BaseModel):
    arguments_pour: list[str] = []
    arguments_contre: list[str] = []
    contradictions: list[str] = []
    convergence: Convergence = "faible"

    @field_validator("convergence", mode="before")
    @classmethod
    def normalize_convergence(cls, v: str) -> str:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if v_clean in ("moderee", "modérée", "moderate"):
                return "modérée"
            if v_clean in ("forte", "strong"):
                return "forte"
            if v_clean in ("faible", "weak", "low"):
                return "faible"
            if v_clean in ("nulle", "none", "null"):
                return "nulle"
        return "faible"


class Verdict(BaseModel):
    verdict: VerdictLabel
    confidence: float = Field(ge=0, le=1)
    report_markdown: str
    warnings: list[str] = []

    @field_validator("verdict", mode="before")
    @classmethod
    def normalize_verdict(cls, v: str) -> str:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean in ("Non verifiable", "Non vérifiable", "Unverifiable"):
                return "Non vérifiable"
            if v_clean in ("Vrai", "True"):
                return "Vrai"
            if v_clean in ("Faux", "False"):
                return "Faux"
            if v_clean in ("Partiellement vrai", "Partially true"):
                return "Partiellement vrai"
        return v
