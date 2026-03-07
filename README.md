# 🏠 Mortgage Servicing Intelligence

**Multi-agent LLM orchestration for mortgage servicing analysis — built with raw Python + Claude API, no frameworks.**

> Built without LangChain / CrewAI / AutoGen to demonstrate orchestration fundamentals: agent registry, DAG-based execution, parallel dispatch, shared state accumulation, structured output validation, and retry logic.

---

## What It Does

Input a mortgage servicing scenario (forbearance request, refinance inquiry, escrow dispute) → the system dispatches **4 specialized AI agents** through an orchestrated pipeline → produces a unified action plan with compliance analysis, risk assessment, borrower communication, and prioritized next steps.

## Architecture

```
Input Scenario
     │
     ├───────────────────┐
     ▼                   ▼
┌───────────┐     ┌───────────┐
│ Compliance│     │   Risk    │    ← Step 1: Parallel Execution
│   Agent   │     │   Agent   │      (ThreadPoolExecutor)
└─────┬─────┘     └─────┬─────┘
      └────────┬────────┘
               ▼
      ┌──────────────┐
      │Communication │             ← Step 2: Sequential
      │    Agent     │               (depends on Step 1)
      └──────┬───────┘
             ▼
      ┌──────────────┐
      │  Synthesis   │             ← Step 3: Sequential
      │    Agent     │               (depends on all)
      └──────────────┘
```

## Orchestration Patterns

| Pattern | Implementation |
|---------|---------------|
| **Agent Registry** | Each agent is a dataclass with system prompt, output schema, metadata |
| **DAG Execution** | Dependency graph drives execution order |
| **Parallel Dispatch** | Compliance + Risk agents run via `ThreadPoolExecutor` |
| **Shared State** | `PipelineState` dataclass accumulates outputs across agents |
| **Structured Output** | Every agent must return valid JSON matching its schema |
| **Retry Logic** | Up to 2 retries on JSON parse failure |
| **Status Callbacks** | Real-time UI updates via callback functions |
| **Error Isolation** | One agent's failure doesn't crash the pipeline |

## Tech Stack

- **Python** — orchestration engine
- **Claude API (Sonnet)** — agent LLM backend
- **Streamlit** — interactive UI with live pipeline tracker
- **No orchestration framework** — demonstrates understanding of underlying patterns

## Project Structure

```
├── agents.py          # Agent definitions (system prompts + schemas)
├── orchestrator.py    # Pipeline engine (DAG execution, state, retries)
├── scenarios.py       # Synthetic mortgage scenarios
├── app.py             # Streamlit UI
├── requirements.txt
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

## Setup

### Local Development

```bash
# Clone
git clone https://github.com/<your-username>/mortgage-servicing-orchestrator.git
cd mortgage-servicing-orchestrator

# Install
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py`
4. Add `ANTHROPIC_API_KEY` in Settings → Secrets
5. Deploy


## Sample Scenarios

- **Forbearance Request (TX)** — borrower lost job, missed 2 payments, requesting relief
- **Refinance Inquiry (CA)** — strong borrower exploring rate reduction and cash-out
- **Escrow Shortage (FL)** — insurance premium spike causing payment shock for fixed-income borrowers

---

*Built by [Your Name] — UC Berkeley Haas MBA '25*
