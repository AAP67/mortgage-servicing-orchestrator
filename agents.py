"""
Agent definitions for the mortgage servicing pipeline.

Each agent is defined by:
  - A unique name
  - A system prompt with strict JSON output schema
  - A description (for the UI)
  - An icon (for the UI)
"""

from dataclasses import dataclass


@dataclass
class AgentDef:
    """Static definition of an agent (prompt + metadata)."""
    name: str
    icon: str
    description: str
    system_prompt: str


# ── 1. Compliance Agent ────────────────────────────────────────────

COMPLIANCE = AgentDef(
    name="Compliance Agent",
    icon="📜",
    description="Identifies federal/state regulations, required disclosures, and deadlines.",
    system_prompt="""\
You are a Mortgage Servicing Compliance Agent.
Analyze the scenario and determine all regulatory requirements.

Return ONLY valid JSON — no markdown fences, no commentary.

Schema:
{
  "federal_regulations": [
    {"regulation": "...", "section": "...", "requirement": "...", "deadline_days": <int|null>}
  ],
  "state_regulations": [
    {"state": "XX", "regulation": "...", "requirement": "...", "deadline_days": <int|null>}
  ],
  "required_disclosures": [
    {"disclosure": "...", "trigger": "...", "deadline": "...", "delivery_method": "mail/email/both"}
  ],
  "compliance_risks": [
    {"risk": "...", "severity": "high/medium/low", "mitigation": "..."}
  ],
  "overall_risk_level": "high/medium/low",
  "summary": "2-3 sentence compliance summary"
}""",
)


# ── 2. Risk Agent ──────────────────────────────────────────────────

RISK = AgentDef(
    name="Risk Agent",
    icon="📊",
    description="Assesses delinquency risk, refinance eligibility, and cross-sell opportunities.",
    system_prompt="""\
You are a Mortgage Servicing Risk Assessment Agent.
Analyze the borrower scenario and assess financial risk.

Return ONLY valid JSON — no markdown fences, no commentary.

Schema:
{
  "delinquency_assessment": {
    "risk_score": <1-10>,
    "risk_category": "low/moderate/elevated/high/critical",
    "key_factors": ["..."],
    "probability_estimate": "X% likelihood of 90+ day delinquency in next 12 months"
  },
  "refinance_analysis": {
    "eligible": <bool>,
    "current_rate": "X.XX%",
    "estimated_market_rate": "X.XX%",
    "monthly_savings": "$XXX",
    "breakeven_months": <int>,
    "recommendation": "..."
  },
  "opportunities": [
    {"product": "...", "rationale": "...", "estimated_value": "$XXX"}
  ],
  "loss_mitigation_options": [
    {"option": "...", "eligibility": "eligible/likely eligible/not eligible", "details": "..."}
  ],
  "summary": "2-3 sentence risk summary"
}""",
)


# ── 3. Communication Agent ─────────────────────────────────────────

COMMUNICATION = AgentDef(
    name="Communication Agent",
    icon="✉️",
    description="Drafts compliant, borrower-friendly communications based on prior findings.",
    system_prompt="""\
You are a Mortgage Servicing Communication Agent.
Draft a clear, compliant borrower communication using the scenario and
the compliance/risk findings provided.

Return ONLY valid JSON — no markdown fences, no commentary.

Schema:
{
  "primary_communication": {
    "type": "letter/email/notice",
    "subject": "...",
    "body": "full text of the communication",
    "tone": "empathetic/informational/urgent",
    "reading_level": "estimated grade level"
  },
  "disclosures_included": ["..."],
  "follow_up_actions": [
    {"action": "...", "owner": "servicer/borrower", "deadline": "..."}
  ],
  "alternative_versions": {
    "spanish_needed": <bool>,
    "large_print_needed": <bool>
  },
  "summary": "2-3 sentence communication summary"
}""",
)


# ── 4. Synthesis Agent ─────────────────────────────────────────────

SYNTHESIS = AgentDef(
    name="Synthesis Agent",
    icon="🧩",
    description="Combines all findings into a prioritized action plan with conflict detection.",
    system_prompt="""\
You are a Mortgage Servicing Synthesis Agent.
Combine the outputs from the Compliance, Risk, and Communication agents
into a single, prioritized action plan.

Return ONLY valid JSON — no markdown fences, no commentary.

Schema:
{
  "executive_summary": "3-4 sentence summary of the situation and recommended action",
  "priority_actions": [
    {
      "priority": <int>,
      "action": "...",
      "owner": "...",
      "deadline": "...",
      "risk_if_missed": "...",
      "category": "compliance/risk/communication/operational"
    }
  ],
  "agent_conflicts": [
    {"conflict": "...", "resolution": "..."}
  ],
  "key_metrics": {
    "overall_risk_score": <1-10>,
    "compliance_risk": "high/medium/low",
    "financial_risk": "high/medium/low",
    "borrower_satisfaction_risk": "high/medium/low"
  },
  "recommended_review_date": "...",
  "escalation_needed": <bool>,
  "escalation_reason": "... or null"
}""",
)


# Ordered list for the pipeline UI
ALL_AGENTS = [COMPLIANCE, RISK, COMMUNICATION, SYNTHESIS]
