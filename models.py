"""
Shared Pydantic models — data contracts between supervisor and agents.
Every message flowing through the system uses one of these shapes.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

class AgentRequest(BaseModel):
    """What the supervisor (or a direct caller) sends to a specialist agent."""
    task: str = Field(..., description="The legal task to perform")
    context: str = Field("", description="Additional context about the matter")
    feedback: str = Field("", description="Supervisor feedback from a prior attempt")
    attempt: int = Field(1, description="Which attempt number this is (1-indexed)")


class SupervisorRequest(BaseModel):
    """What the Streamlit UI sends to the supervisor endpoint."""
    task: str = Field(..., description="The legal task")
    context: str = Field("", description="Additional matter context")
    agents: list[str] = Field(
        default=["research", "risk_analysis", "drafting", "review"],
        description="Which specialist agents to run"
    )
    confidence_threshold: int = Field(80, ge=0, le=100)
    risk_threshold: int = Field(50, ge=0, le=100)
    max_iterations: int = Field(3, ge=1, le=5)


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

class AgentResult(BaseModel):
    """Structured output from any specialist agent."""
    agent: str
    attempt: int
    output: str
    confidence: int                    # 0–100: how sure the agent is
    risk: int                          # 0–100: residual risk in the matter
    citations: list[str] = []
    flags: list[str] = []
    reasoning: str = ""                # model's thinking chain (transparency layer)
    passed: bool = False               # did it meet the supervisor's thresholds?
    issues: list[str] = []            # what the supervisor found wrong


class SupervisorDecision(BaseModel):
    """What the supervisor decided after evaluating all agent results."""
    agent: str
    passed: bool
    issues: list[str]
    confidence: int
    risk: int


class SupervisorResponse(BaseModel):
    """Full response from the supervisor endpoint to the UI."""
    status: str                        # "accepted" | "needs_human_review"
    total_attempts: int
    escalation_reason: Optional[str] = None

    # Per-agent final results (last attempt for each agent)
    agent_results: dict[str, AgentResult]

    # Supervisor's cross-agent synthesis
    synthesis: str
    overall_confidence: int            # average across all agents
    overall_risk: int                  # max across all agents (conservative)
    high_flag_count: int

    # Full history for the audit trail
    audit_log: list[dict]
    attempt_history: list[dict]        # [{attempt, decisions: [SupervisorDecision]}]
