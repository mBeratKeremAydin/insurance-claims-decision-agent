from typing import Literal, Optional

from pydantic import BaseModel, Field


class GraphInput(BaseModel):
    """Stable input contract - this is what a BPMN Agent node (or any caller) must provide."""

    policy_number: str
    claimant_name: str
    claim_amount: float
    incident_date: str  # ISO date, e.g. "2026-03-15"
    document_texts: list[str] = Field(default_factory=list)


class GraphOutput(BaseModel):
    """Stable output contract - this is what a BPMN HITL node will show the reviewer."""

    decision: Literal["approve", "reject", "manual_review"]
    rationale: str
    policy_valid: bool
    is_duplicate: bool
    fraud_risk_score: float


class GraphState(BaseModel):
    # input
    policy_number: str
    claimant_name: str
    claim_amount: float
    incident_date: str
    document_texts: list[str] = Field(default_factory=list)

    # check_policy
    policy_valid: bool = False
    policy_rejection_reason: Optional[str] = None
    coverage_amount: Optional[float] = None

    # check_duplicate
    is_duplicate: bool = False

    # analyze_documents
    documents_complete: bool = True
    missing_document_types: list[str] = Field(default_factory=list)
    fraud_risk_score: float = 0.0
    document_findings: str = ""

    # recommend_decision (final)
    decision: Optional[Literal["approve", "reject", "manual_review"]] = None
    rationale: str = ""
