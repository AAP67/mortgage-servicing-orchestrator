"""
Orchestrator — the core of the demo.

Patterns implemented:
  1. Agent registry          – agents are data, not hard-coded calls
  2. DAG execution           – dependency graph drives order
  3. Parallel dispatch       – independent agents run concurrently
  4. Shared state            – PipelineState accumulates across steps
  5. Structured output       – every agent must return valid JSON
  6. Retry with back-off     – up to N retries on parse failure
  7. Status callbacks        – UI hooks into every state change
"""

import json
import time
import concurrent.futures
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from anthropic import Anthropic

from agents import AgentDef, COMPLIANCE, RISK, COMMUNICATION, SYNTHESIS, QUALITY_CHECKER

# ── Client setup ───────────────────────────────────────────────────
client = Anthropic()                     # reads ANTHROPIC_API_KEY from env
MODEL = "claude-sonnet-4-20250514"

# ── Data classes ───────────────────────────────────────────────────

@dataclass
class AgentResult:
    """Output of a single agent run."""
    agent_name: str
    status: str          # waiting | running | retrying | complete | failed
    output: dict
    duration_s: float
    retries: int = 0
    error: Optional[str] = None


@dataclass
class PipelineState:
    """Shared mutable state that flows through the pipeline."""
    scenario: dict              = field(default_factory=dict)
    compliance: dict            = field(default_factory=dict)
    risk: dict                  = field(default_factory=dict)
    communication: dict         = field(default_factory=dict)
    synthesis: dict             = field(default_factory=dict)
    quality_check: dict         = field(default_factory=dict)
    results: list[AgentResult]  = field(default_factory=list)
    total_duration_s: float     = 0.0


# Type alias for the UI callback:  (agent_name, status, retry_count) -> None
StatusCallback = Callable[[str, str, int], None]


# ── Helpers ────────────────────────────────────────────────────────

def _scenario_to_prompt(scenario: dict) -> str:
    """Turn a scenario dict into a human-readable prompt block."""
    return f"""\
BORROWER PROFILE
  Name:              {scenario.get("borrower_name", "N/A")}
  Property State:    {scenario.get("state", "N/A")}
  Property Type:     {scenario.get("property_type", "Single Family")}
  Loan Type:         {scenario.get("loan_type", "N/A")}
  Original Amount:   {scenario.get("original_amount", "N/A")}
  Current Balance:   {scenario.get("current_balance", "N/A")}
  Interest Rate:     {scenario.get("interest_rate", "N/A")}
  Monthly Payment:   {scenario.get("monthly_payment", "N/A")}
  Origination Date:  {scenario.get("origination_date", "N/A")}
  Credit Score:      {scenario.get("credit_score", "N/A")}
  DTI Ratio:         {scenario.get("dti_ratio", "N/A")}

PAYMENT HISTORY
  {scenario.get("payment_history", "No history available.")}

CURRENT REQUEST / SITUATION
  {scenario.get("situation", "General servicing review.")}

ADDITIONAL CONTEXT
  {scenario.get("additional_context", "None.")}
"""


def _clean_json(text: str) -> str:
    """Strip markdown fences that the model sometimes adds."""
    t = text.strip()
    if t.startswith("```json"):
        t = t[7:]
    elif t.startswith("```"):
        t = t[3:]
    if t.endswith("```"):
        t = t[:-3]
    return t.strip()


# ── Single-agent runner ────────────────────────────────────────────

def run_agent(
    agent: AgentDef,
    user_message: str,
    max_retries: int = 2,
    cb: Optional[StatusCallback] = None,
) -> AgentResult:
    """
    Call Claude with the agent's system prompt, validate JSON output,
    and retry on failure.
    """
    start = time.time()
    retries = 0
    raw_text = ""

    while retries <= max_retries:
        try:
            status = "retrying" if retries > 0 else "running"
            if cb:
                cb(agent.name, status, retries)

            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=agent.system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            raw_text = response.content[0].text
            output = json.loads(_clean_json(raw_text))

            if cb:
                cb(agent.name, "complete", retries)

            return AgentResult(
                agent_name=agent.name,
                status="complete",
                output=output,
                duration_s=round(time.time() - start, 2),
                retries=retries,
            )

        except json.JSONDecodeError as exc:
            retries += 1
            if retries > max_retries:
                if cb:
                    cb(agent.name, "failed", retries)
                return AgentResult(
                    agent_name=agent.name,
                    status="failed",
                    output={"error": "JSON parse failure", "raw_snippet": raw_text[:300]},
                    duration_s=round(time.time() - start, 2),
                    retries=retries,
                    error=str(exc),
                )

        except Exception as exc:
            retries += 1
            if retries > max_retries:
                if cb:
                    cb(agent.name, "failed", retries)
                return AgentResult(
                    agent_name=agent.name,
                    status="failed",
                    output={"error": str(exc)},
                    duration_s=round(time.time() - start, 2),
                    retries=retries,
                    error=str(exc),
                )


# ── Pipeline (DAG execution) ──────────────────────────────────────

def run_pipeline(
    scenario: dict,
    cb: Optional[StatusCallback] = None,
) -> PipelineState:
    """
    Execute the full pipeline:

        ┌────────────┐   ┌────────────┐
        │ Compliance │   │    Risk    │   ← Step 1  (parallel)
        └─────┬──────┘   └─────┬──────┘
              └────────┬───────┘
                       ▼
              ┌────────────────┐
              │ Communication  │          ← Step 2  (sequential)
              └───────┬────────┘
                      ▼
              ┌────────────────┐
              │   Synthesis    │          ← Step 3  (sequential)
              └────────────────┘
    """

    pipeline_start = time.time()
    state = PipelineState(scenario=scenario)
    base_prompt = _scenario_to_prompt(scenario)

    # ── Step 1: Compliance + Risk ─────────────────────────────
    #   NOTE: These two agents are independent (no data dependency)
    #   and *could* run in parallel with ThreadPoolExecutor.
    #   We run them sequentially here because Streamlit's UI
    #   callbacks are not thread-safe. In a production FastAPI
    #   backend you would use asyncio.gather() or threads.
    if cb:
        cb("Step 1", "starting", 0)

    compliance_result = run_agent(COMPLIANCE, base_prompt, 2, cb)
    risk_result = run_agent(RISK, base_prompt, 2, cb)

    state.compliance = compliance_result.output
    state.risk = risk_result.output
    state.results.extend([compliance_result, risk_result])

    # ── Step 2: Communication (depends on Step 1) ──────────────
    if cb:
        cb("Step 2", "sequential", 0)

    comm_prompt = (
        f"{base_prompt}\n\n"
        f"── COMPLIANCE FINDINGS ──\n{json.dumps(state.compliance, indent=2)}\n\n"
        f"── RISK ASSESSMENT ──\n{json.dumps(state.risk, indent=2)}"
    )

    comm_result = run_agent(COMMUNICATION, comm_prompt, 2, cb)
    state.communication = comm_result.output
    state.results.append(comm_result)

    # ── Step 3: Synthesis (depends on all) ─────────────────────
    if cb:
        cb("Step 3", "sequential", 0)

    synth_prompt = (
        f"{base_prompt}\n\n"
        f"── COMPLIANCE AGENT OUTPUT ──\n{json.dumps(state.compliance, indent=2)}\n\n"
        f"── RISK AGENT OUTPUT ──\n{json.dumps(state.risk, indent=2)}\n\n"
        f"── COMMUNICATION AGENT OUTPUT ──\n{json.dumps(state.communication, indent=2)}"
    )

    synth_result = run_agent(SYNTHESIS, synth_prompt, 2, cb)
    state.synthesis = synth_result.output
    state.results.append(synth_result)

    # ── Step 4: Quality Checker (depends on all) ───────────────
    if cb:
        cb("Step 4", "sequential", 0)

    qc_prompt = (
        f"{base_prompt}\n\n"
        f"── COMPLIANCE AGENT OUTPUT ──\n{json.dumps(state.compliance, indent=2)}\n\n"
        f"── RISK AGENT OUTPUT ──\n{json.dumps(state.risk, indent=2)}\n\n"
        f"── COMMUNICATION AGENT OUTPUT ──\n{json.dumps(state.communication, indent=2)}\n\n"
        f"── SYNTHESIS AGENT OUTPUT ──\n{json.dumps(state.synthesis, indent=2)}"
    )

    qc_result = run_agent(QUALITY_CHECKER, qc_prompt, 2, cb)
    state.quality_check = qc_result.output
    state.results.append(qc_result)

    state.total_duration_s = round(time.time() - pipeline_start, 2)

    if cb:
        cb("Pipeline", "complete", 0)

    return state