# 🏠 Mortgage Servicing Intelligence

**Multi-agent LLM orchestration for mortgage servicing analysis — built with raw Python + Claude API, no frameworks.**

---

## What It Does

Input a mortgage servicing scenario (forbearance, collections, loan modification, etc.) → the system orchestrates 5 specialized AI agents through a dependency-aware pipeline → produces a unified action plan with compliance analysis, risk assessment, borrower communication, and rubric-based quality evaluation.

## Architecture

```
Input Scenario
     │
     ├───────────────────┐
     ▼                   ▼
┌───────────┐     ┌───────────┐
│ Compliance│     │   Risk    │    ← Step 1: Independent
│   Agent   │     │   Agent   │
└─────┬─────┘     └─────┬─────┘
      └────────┬────────┘
               ▼
      ┌──────────────┐
      │Communication │             ← Step 2: Depends on Step 1
      │    Agent     │
      └──────┬───────┘
             ▼
      ┌──────────────┐
      │  Synthesis   │             ← Step 3: Depends on all
      │    Agent     │
      └──────┬───────┘
             ▼
      ┌──────────────┐
      │   Quality    │             ← Step 4: LLM-as-Judge
      │   Checker    │               (rubric-based evaluation)
      └──────────────┘
```

## Orchestration Patterns

| Pattern | Implementation |
|---------|---------------|
| **Agent Registry** | Each agent is a dataclass with system prompt, output schema, metadata |
| **DAG Execution** | Dependency graph drives execution order |
| **Shared State** | `PipelineState` dataclass accumulates outputs across agents |
| **Structured Output** | Every agent returns validated JSON matching its schema |
| **Retry Logic** | Up to 2 retries on JSON parse failure |
| **LLM-as-Judge** | Quality Checker scores all outputs on a 5-dimension rubric |
| **Status Callbacks** | Real-time UI updates via callback functions |
| **Error Isolation** | One agent's failure doesn't crash the pipeline |

## Agents

1. **Compliance Agent** — federal/state regulations, disclosures, deadlines
2. **Risk Agent** — delinquency risk, refinance eligibility, cross-sell opportunities
3. **Communication Agent** — drafts compliant borrower letters (depends on 1 & 2)
4. **Synthesis Agent** — unified action plan with conflict detection (depends on 1, 2, 3)
5. **Quality Checker** — rubric-based evaluation across accuracy, completeness, consistency, communication quality, and actionability (depends on all)

## Scenarios

12 scenarios across 4 segments:

- **Servicer** — forbearance, refinance, escrow shortage, early payoff
- **Collections** — pre-foreclosure, debt validation disputes, deficiency judgment, third-party collector handoff
- **Originator** — servicing transfer, VA loan assumption
- **Investor/GSE** — loan modification, FHA partial claim

## Tech Stack

- **Python** — orchestration engine
- **Claude API (Sonnet)** — agent LLM backend
- **Streamlit** — interactive UI with live pipeline tracker

## Project Structure

```
├── agents.py          # Agent definitions (system prompts + schemas)
├── orchestrator.py    # Pipeline engine (DAG execution, state, retries)
├── scenarios.py       # Synthetic mortgage scenarios
├── app.py             # Streamlit UI
├── requirements.txt
└── .streamlit/
    └── config.toml
```

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → select `app.py`
4. Add `ANTHROPIC_API_KEY` in Settings → Secrets
5. Deploy
