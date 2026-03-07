"""
Mortgage Servicing Intelligence — Streamlit UI

Displays:
  • Scenario selector (pre-built + custom)
  • Live pipeline tracker (agent status cards)
  • Results dashboard (tabs per agent)
  • Pipeline metrics (duration, retries, success rate)
"""

import streamlit as st
import json
from scenarios import SCENARIOS
from agents import ALL_AGENTS
from orchestrator import run_pipeline, PipelineState

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(page_title="Mortgage Servicing Intelligence", page_icon="🏠", layout="wide")

# ── CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
.block-container { max-width: 1100px; }

.hero { margin-bottom: 1.2rem; }
.hero h1 { font-family:'DM Sans',sans-serif; font-size:2rem; font-weight:700; margin:0; }
.hero p  { color:#6b7280; margin:0; font-size:1rem; }

.agent-card {
    border:1px solid #e5e7eb; border-radius:10px; padding:14px 16px;
    margin-bottom:8px; background:#fafafa; font-family:'DM Sans',sans-serif;
}
.agent-card.running  { border-color:#3b82f6; background:#eff6ff; }
.agent-card.complete { border-color:#10b981; background:#ecfdf5; }
.agent-card.failed   { border-color:#ef4444; background:#fef2f2; }
.agent-card.retrying { border-color:#f59e0b; background:#fffbeb; }

.badge {
    font-family:'JetBrains Mono',monospace; font-size:.75rem;
    padding:2px 8px; border-radius:4px; display:inline-block;
}
.badge-waiting  { background:#f3f4f6; color:#6b7280; }
.badge-running  { background:#dbeafe; color:#2563eb; }
.badge-complete { background:#d1fae5; color:#059669; }
.badge-failed   { background:#fee2e2; color:#dc2626; }
.badge-retrying { background:#fef3c7; color:#d97706; }

.metric-row { display:flex; gap:12px; margin-top:12px; }
.metric-box {
    flex:1; background:linear-gradient(135deg,#1a1a2e,#16213e);
    border-radius:10px; padding:16px; text-align:center; color:white;
}
.metric-box .val { font-size:1.6rem; font-weight:700; color:#60a5fa; }
.metric-box .lbl { font-size:.78rem; color:#94a3b8; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🏠 Mortgage Servicing Intelligence</h1>
  <p>Multi-agent orchestration demo — raw Python + Claude API, no frameworks</p>
</div>""", unsafe_allow_html=True)

# ── Architecture explainer ─────────────────────────────────────────
with st.expander("⚙️  How the orchestration works"):
    st.code("""
    Input Scenario
         │
         ├───────────────────┐
         ▼                   ▼
    ┌───────────┐     ┌───────────┐
    │ Compliance│     │   Risk    │    ← Step 1: Parallel
    │   Agent   │     │   Agent   │
    └─────┬─────┘     └─────┬─────┘
          └────────┬────────┘
                   ▼
          ┌──────────────┐
          │Communication │             ← Step 2: Sequential
          │    Agent     │
          └──────┬───────┘
                 ▼
          ┌──────────────┐
          │  Synthesis   │             ← Step 3: Sequential
          │    Agent     │
          └──────────────┘
    """, language=None)
    st.markdown("""
    **Patterns demonstrated:** Agent registry · DAG execution · Parallel dispatch ·
    Shared state accumulation · Structured JSON output validation · Retry logic ·
    Real-time status callbacks
    """)

st.divider()

# ── Layout: scenario picker (left) + pipeline tracker (right) ─────
col_left, col_right = st.columns([3, 2], gap="large")

# ── Scenario selection ─────────────────────────────────────────────
with col_left:
    st.subheader("📋 Scenario")
    choice = st.selectbox(
        "Pick a scenario",
        ["— select —"] + list(SCENARIOS.keys()) + ["✏️ Custom"],
        label_visibility="collapsed",
    )

    scenario = None

    if choice in SCENARIOS:
        scenario = SCENARIOS[choice]
        c1, c2, c3 = st.columns(3)
        c1.metric("Borrower", scenario["borrower_name"])
        c2.metric("State", scenario["state"])
        c3.metric("Rate", scenario["interest_rate"])
        st.info(f"**Situation:** {scenario['situation']}")
        with st.expander("Full scenario JSON"):
            st.json(scenario)

    elif choice == "✏️ Custom":
        c1, c2 = st.columns(2)
        with c1:
            borrower_name   = st.text_input("Borrower Name", "Jane Doe")
            state_code      = st.selectbox("State", ["TX","CA","FL","NY","IL","OH","PA","AZ","GA","NC"])
            loan_type       = st.selectbox("Loan Type", [
                "30-year Fixed (Conventional)","30-year Fixed (FHA)",
                "15-year Fixed","5/1 ARM","30-year Fixed (VA)",
            ])
            original_amount = st.text_input("Original Amount", "$350,000")
            interest_rate   = st.text_input("Interest Rate", "6.50%")
        with c2:
            current_balance = st.text_input("Current Balance", "$330,000")
            monthly_payment = st.text_input("Monthly Payment", "$2,200")
            credit_score    = st.text_input("Credit Score", "700")
            dti_ratio       = st.text_input("DTI Ratio", "40%")
            origination     = st.text_input("Origination Date", "January 2023")
        payment_history = st.text_area("Payment History", "On-time 24 months. Recently missed 1 payment.", height=70)
        situation       = st.text_area("Current Situation", "Borrower calling to discuss options.", height=70)
        extra           = st.text_area("Additional Context", "Property value ~$380k.", height=50)

        scenario = {
            "borrower_name": borrower_name, "state": state_code,
            "property_type": "Single Family", "loan_type": loan_type,
            "original_amount": original_amount, "current_balance": current_balance,
            "interest_rate": interest_rate, "monthly_payment": monthly_payment,
            "origination_date": origination, "credit_score": credit_score,
            "dti_ratio": dti_ratio, "payment_history": payment_history,
            "situation": situation, "additional_context": extra,
        }

# ── Pipeline tracker (right column) ───────────────────────────────
with col_right:
    st.subheader("🔄 Pipeline")
    tracker = {}
    for ag in ALL_AGENTS:
        tracker[ag.name] = st.empty()
        tracker[ag.name].markdown(
            f'<div class="agent-card">'
            f'<strong>{ag.icon} {ag.name}</strong> '
            f'<span class="badge badge-waiting">waiting</span><br>'
            f'<small style="color:#9ca3af">{ag.description}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )
    metrics_placeholder = st.empty()


# ── Callback wired to the tracker cards ────────────────────────────
def status_cb(name: str, status: str, retries: int):
    """Update the matching tracker card in real time."""
    # Map orchestrator step names to display
    for ag in ALL_AGENTS:
        if ag.name == name:
            badge = status
            extra = f" (retry {retries})" if retries > 0 else ""
            tracker[ag.name].markdown(
                f'<div class="agent-card {badge}">'
                f'<strong>{ag.icon} {ag.name}</strong> '
                f'<span class="badge badge-{badge}">{badge}{extra}</span><br>'
                f'<small style="color:#9ca3af">{ag.description}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )
            break


# ── Run button ─────────────────────────────────────────────────────
st.divider()

run_disabled = scenario is None
if st.button("🚀  Run Pipeline", type="primary", disabled=run_disabled, use_container_width=True):
    with st.spinner("Agents working…"):
        state: PipelineState = run_pipeline(scenario, cb=status_cb)

    # ── Metrics row ────────────────────────────────────────────
    successes = sum(1 for r in state.results if r.status == "complete")
    total_retries = sum(r.retries for r in state.results)
    metrics_placeholder.markdown(f"""
    <div class="metric-row">
      <div class="metric-box"><div class="val">{state.total_duration_s}s</div><div class="lbl">Total Duration</div></div>
      <div class="metric-box"><div class="val">{successes}/{len(state.results)}</div><div class="lbl">Agents OK</div></div>
      <div class="metric-box"><div class="val">{total_retries}</div><div class="lbl">Retries</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Results tabs ───────────────────────────────────────────
    st.divider()
    st.subheader("📑 Results")

    tab_synth, tab_compliance, tab_risk, tab_comm, tab_raw = st.tabs([
        "🧩 Synthesis", "📜 Compliance", "📊 Risk", "✉️ Communication", "🗂 Raw JSON"
    ])

    # ── Synthesis tab ──────────────────────────────────────────
    with tab_synth:
        s = state.synthesis
        if "error" in s:
            st.error(f"Synthesis agent failed: {s['error']}")
        else:
            st.markdown(f"**Executive Summary**\n\n{s.get('executive_summary','')}")

            st.markdown("**Key Metrics**")
            km = s.get("key_metrics", {})
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Overall Risk", f"{km.get('overall_risk_score','?')}/10")
            m2.metric("Compliance", km.get("compliance_risk","—"))
            m3.metric("Financial", km.get("financial_risk","—"))
            m4.metric("Borrower Sat.", km.get("borrower_satisfaction_risk","—"))

            st.markdown("**Priority Actions**")
            for a in s.get("priority_actions", []):
                with st.expander(f"P{a['priority']}: {a['action'][:80]}"):
                    st.write(f"**Owner:** {a.get('owner','-')}")
                    st.write(f"**Deadline:** {a.get('deadline','-')}")
                    st.write(f"**Risk if missed:** {a.get('risk_if_missed','-')}")
                    st.write(f"**Category:** {a.get('category','-')}")

            if s.get("agent_conflicts"):
                st.markdown("**⚠️ Agent Conflicts**")
                for c in s["agent_conflicts"]:
                    st.warning(f"**Conflict:** {c['conflict']}\n\n**Resolution:** {c['resolution']}")

            if s.get("escalation_needed"):
                st.error(f"🚨 Escalation needed: {s.get('escalation_reason','')}")

    # ── Compliance tab ─────────────────────────────────────────
    with tab_compliance:
        cp = state.compliance
        if "error" in cp:
            st.error(f"Compliance agent failed: {cp['error']}")
        else:
            st.markdown(f"**Summary:** {cp.get('summary','')}")
            st.markdown(f"**Overall Risk Level:** `{cp.get('overall_risk_level','?')}`")

            if cp.get("federal_regulations"):
                st.markdown("**Federal Regulations**")
                for r in cp["federal_regulations"]:
                    st.write(f"- **{r['regulation']}** ({r.get('section','')}): {r['requirement']}"
                             + (f" — *deadline: {r['deadline_days']} days*" if r.get("deadline_days") else ""))

            if cp.get("state_regulations"):
                st.markdown("**State Regulations**")
                for r in cp["state_regulations"]:
                    st.write(f"- **[{r['state']}] {r['regulation']}**: {r['requirement']}")

            if cp.get("compliance_risks"):
                st.markdown("**Compliance Risks**")
                for r in cp["compliance_risks"]:
                    icon = {"high":"🔴","medium":"🟡","low":"🟢"}.get(r["severity"],"⚪")
                    st.write(f"- {icon} **{r['severity'].upper()}** — {r['risk']} → *{r['mitigation']}*")

    # ── Risk tab ───────────────────────────────────────────────
    with tab_risk:
        rk = state.risk
        if "error" in rk:
            st.error(f"Risk agent failed: {rk['error']}")
        else:
            st.markdown(f"**Summary:** {rk.get('summary','')}")

            da = rk.get("delinquency_assessment", {})
            r1, r2, r3 = st.columns(3)
            r1.metric("Risk Score", f"{da.get('risk_score','?')}/10")
            r2.metric("Category", da.get("risk_category","—"))
            r3.metric("90+ Day Prob.", da.get("probability_estimate","—"))

            if da.get("key_factors"):
                st.markdown("**Key Factors:** " + " · ".join(da["key_factors"]))

            ra = rk.get("refinance_analysis", {})
            if ra:
                st.markdown("**Refinance Analysis**")
                rc1, rc2, rc3 = st.columns(3)
                rc1.metric("Eligible", "✅ Yes" if ra.get("eligible") else "❌ No")
                rc2.metric("Monthly Savings", ra.get("monthly_savings","—"))
                rc3.metric("Breakeven", f"{ra.get('breakeven_months','?')} months")
                st.write(f"*{ra.get('recommendation','')}*")

            if rk.get("opportunities"):
                st.markdown("**Opportunities**")
                for o in rk["opportunities"]:
                    st.write(f"- **{o['product']}**: {o['rationale']} (est. {o.get('estimated_value','?')})")

    # ── Communication tab ──────────────────────────────────────
    with tab_comm:
        cm = state.communication
        if "error" in cm:
            st.error(f"Communication agent failed: {cm['error']}")
        else:
            st.markdown(f"**Summary:** {cm.get('summary','')}")
            pc = cm.get("primary_communication", {})
            st.markdown(f"**Type:** {pc.get('type','')} · **Tone:** {pc.get('tone','')} · **Reading Level:** {pc.get('reading_level','')}")
            st.text_area("Draft Communication", value=pc.get("body",""), height=300, disabled=True)

            if cm.get("follow_up_actions"):
                st.markdown("**Follow-up Actions**")
                for f in cm["follow_up_actions"]:
                    st.write(f"- [{f.get('owner','')}] {f['action']} — *{f.get('deadline','')}*")

    # ── Raw JSON tab ───────────────────────────────────────────
    with tab_raw:
        st.json({
            "compliance": state.compliance,
            "risk": state.risk,
            "communication": state.communication,
            "synthesis": state.synthesis,
            "pipeline_metrics": {
                "total_duration_s": state.total_duration_s,
                "agent_results": [
                    {
                        "agent": r.agent_name,
                        "status": r.status,
                        "duration_s": r.duration_s,
                        "retries": r.retries,
                        "error": r.error,
                    }
                    for r in state.results
                ],
            },
        })
