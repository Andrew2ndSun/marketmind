"""Validated structured research output."""
from pydantic import BaseModel, ConfigDict, Field

class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=1800)
    evidence_ids: list[str] = Field(min_length=1, max_length=12)

class Synthesis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: Claim
    findings: list[Claim] = Field(min_length=1, max_length=6)
    conflicting_evidence: list[Claim] = Field(max_length=6)
    risks: list[Claim] = Field(min_length=1, max_length=6)
    unknowns: list[str] = Field(min_length=1, max_length=8)
