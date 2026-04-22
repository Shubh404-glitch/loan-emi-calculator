"""
 Advanced Loan EMI Calculator
================================
A professional, real-world Loan EMI Calculator built with Streamlit.
Features: Slider inputs, real-time calculations, loan comparison,
amortization table, interactive charts, and multiple loan types.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import io
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title=" Loan EMI Calculator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Professional Dark/Light Theme
# ─────────────────────────────────────────────
def inject_css(dark_mode: bool):
    if dark_mode:
        bg        = "#0f1117"
        card_bg   = "#1a1d2e"
        border    = "#2d3154"
        text      = "#e8eaf6"
        sub_text  = "#9fa8da"
        accent    = "#7c83ff"
        accent2   = "#6793AC"
        green     = "#00e5a0"
        card_shad = "0 4px 24px rgba(124,131,255,0.10)"
    else:
        bg        = "#f0f2f8"
        card_bg   = "#ffffff"
        border    = "#dce1f7"
        text      = "#1a1d2e"
        sub_text  = "#5c6bc0"
        accent    = "#5c6bc0"
        accent2   = "#7da2a9"
        green     = "#00897b"
        card_shad = "0 4px 24px rgba(92,107,192,0.10)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Space Grotesk', sans-serif;
        background-color: {bg};
        color: {text};
    }}
    .main {{ background-color: {bg}; }}

    /* Header */
    .emi-header {{
        background: linear-gradient(135deg, {accent} 0%, {accent2} 100%);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: {card_shad};
    }}
    .emi-header h1 {{ color: #fff; font-size: 2.2rem; font-weight: 700; margin: 0; }}
    .emi-header p  {{ color: rgba(255,255,255,0.85); margin: 6px 0 0; font-size: 1rem; }}

    /* Result Cards */
    .result-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: {card_shad};
        transition: transform 0.2s;
    }}
    .result-card:hover {{ transform: translateY(-2px); }}
    .result-card .label {{ font-size: 0.82rem; font-weight: 600; letter-spacing: 0.08em;
                           text-transform: uppercase; color: {sub_text}; margin-bottom: 6px; }}
    .result-card .value {{ font-family: 'JetBrains Mono', monospace;
                           font-size: 1.7rem; font-weight: 700; color: {accent}; }}
    .result-card .value.green {{ color: {green}; }}
    .result-card .value.red   {{ color: {accent2}; }}

    /* Section headings */
    .section-title {{
        font-size: 1.1rem; font-weight: 700; color: {sub_text};
        letter-spacing: 0.05em; text-transform: uppercase;
        margin: 28px 0 12px; border-left: 4px solid {accent};
        padding-left: 12px;
    }}

    /* Best loan badge */
    .best-badge {{
        background: linear-gradient(135deg, {green}, #00bfa5);
        color: #fff; border-radius: 20px; padding: 4px 14px;
        font-size: 0.78rem; font-weight: 700; display: inline-block;
        letter-spacing: 0.05em; text-transform: uppercase;
    }}

    /* Metric highlight */
    .highlight-box {{
        background: linear-gradient(135deg, {accent}22, {accent2}11);
        border: 1px solid {border}; border-radius: 12px;
        padding: 16px 20px; margin: 8px 0;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {card_bg};
        border-right: 1px solid {border};
    }}

    /* Dataframe */
    .dataframe {{ font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; }}

    /* Streamlit overrides */
    .stSlider > div > div > div > div {{ background: {accent}; }}
    .stSelectbox > div > div {{ background: {card_bg}; border: 1px solid {border}; border-radius: 10px; }}
    div[data-testid="stMetricValue"] {{ font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; color: {accent}; }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CORE CALCULATION FUNCTIONS
# ─────────────────────────────────────────────

def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> dict:
    """Calculate EMI and related values using the standard formula."""
    n = tenure_years * 12                     # months
    r = annual_rate / (12 * 100)              # monthly rate

    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

    total_payment  = emi * n
    total_interest = total_payment - principal

    return {
        "emi":            emi,
        "total_payment":  total_payment,
        "total_interest": total_interest,
        "principal":      principal,
        "months":         n,
    }


def build_amortization(principal: float, annual_rate: float, tenure_years: int) -> pd.DataFrame:
    """Generate month-by-month amortization schedule."""
    result  = calculate_emi(principal, annual_rate, tenure_years)
    emi     = result["emi"]
    r       = annual_rate / (12 * 100)
    balance = principal
    rows    = []

    for month in range(1, result["months"] + 1):
        interest_part  = balance * r
        principal_part = emi - interest_part
        balance       -= principal_part
        rows.append({
            "Month":     month,
            "EMI (₹)":       round(emi, 2),
            "Principal (₹)": round(principal_part, 2),
            "Interest (₹)":  round(interest_part, 2),
            "Balance (₹)":   round(max(balance, 0), 2),
        })

    return pd.DataFrame(rows)


def format_inr(amount: float) -> str:
    """Format number as Indian Rupees with comma separators."""
    if amount >= 1_00_00_000:
        return f"₹{amount/1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount/1_00_000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


# ─────────────────────────────────────────────
# CHART FUNCTIONS
# ─────────────────────────────────────────────

def pie_chart(principal, interest, dark_mode):
    """Principal vs Interest pie chart."""
    colors = ["#7c83ff", "#8b616f"] if dark_mode else ["#5c6bc0", "#6c468b"]
    fig = go.Figure(go.Pie(
        labels=["Principal", "Total Interest"],
        values=[principal, interest],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textinfo="percent+label",
        textfont=dict(size=13, family="Space Grotesk"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#9fa8da" if dark_mode else "#3949ab"),
        legend=dict(orientation="h", x=0.15, y=-0.05),
        annotations=[dict(
            text=f"<b>{format_inr(principal+interest)}</b><br>Total",
            x=0.5, y=0.5, font_size=14, showarrow=False,
            font=dict(color="#7c83ff" if dark_mode else "#5c6bc0", family="JetBrains Mono"),
        )],
    )
    return fig


def emi_vs_tenure_chart(principal, annual_rate, dark_mode):
    """Line chart: EMI changes across different tenures."""
    tenures = list(range(1, 31))
    emis    = [calculate_emi(principal, annual_rate, t)["emi"] for t in tenures]
    totals  = [calculate_emi(principal, annual_rate, t)["total_payment"] for t in tenures]
    color   = "#7c83ff" if dark_mode else "#5c6bc0"
    color2  = "#27465F" if dark_mode else "#492079"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tenures, y=emis, name="Monthly EMI",
        line=dict(color=color, width=3), mode="lines+markers",
        marker=dict(size=5), fill="tozeroy",
        fillcolor=f"rgba(124,131,255,0.12)" if dark_mode else "rgba(92,107,192,0.08)",
        hovertemplate="Tenure: %{x}yr<br>EMI: ₹%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=tenures, y=totals, name="Total Payment",
        line=dict(color=color2, width=2, dash="dot"),
        hovertemplate="Tenure: %{x}yr<br>Total: ₹%{y:,.0f}<extra></extra>",
        yaxis="y2",
    ))
    bg = "#0f1117" if dark_mode else "#f0f2f8"
    fig.update_layout(
        xaxis=dict(title="Tenure (Years)", tickfont=dict(size=11)),
        yaxis=dict(title="Monthly EMI (₹)"),
        yaxis2=dict(title="Total Payment (₹)", overlaying="y", side="right"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=40, l=60, r=60),
        font=dict(family="Space Grotesk", color="#9fa8da" if dark_mode else "#3949ab"),
        legend=dict(orientation="h", x=0, y=1.05),
        hovermode="x unified",
    )
    return fig


def comparison_bar_chart(loan_a, loan_b, dark_mode):
    """Bar chart comparing two loans."""
    categories = ["Monthly EMI", "Total Interest", "Total Payment"]
    vals_a = [loan_a["emi"], loan_a["total_interest"], loan_a["total_payment"]]
    vals_b = [loan_b["emi"], loan_b["total_interest"], loan_b["total_payment"]]
    c1 = "#7c83ff" if dark_mode else "#5c6bc0"
    c2 = "#091a79" if dark_mode else "#051C4E"

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Loan A", x=categories, y=vals_a, marker_color=c1,
                         text=[f"₹{v:,.0f}" for v in vals_a], textposition="outside"))
    fig.add_trace(go.Bar(name="Loan B", x=categories, y=vals_b, marker_color=c2,
                         text=[f"₹{v:,.0f}" for v in vals_b], textposition="outside"))
    fig.update_layout(
        barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=40, l=60, r=20),
        font=dict(family="Space Grotesk", color="#9fa8da" if dark_mode else "#3949ab"),
        legend=dict(orientation="h", x=0.3, y=1.1),
        yaxis=dict(title="Amount (₹)"),
    )
    return fig


# ─────────────────────────────────────────────
# LOAN TYPE DEFAULTS
# ─────────────────────────────────────────────

LOAN_TYPES = {
    "🧍 Personal Loan":   {"rate": 12.0, "tenure": 5,  "min_rate": 9.0,  "max_rate": 20.0},
    "🚗 Vehicle Loan":    {"rate": 9.0,  "tenure": 7,  "min_rate": 7.0,  "max_rate": 15.0},
    "🏠 Home Loan":       {"rate": 8.5,  "tenure": 25, "min_rate": 6.5,  "max_rate": 12.0},
    "🏢 Business Loan":   {"rate": 13.0, "tenure": 10, "min_rate": 10.0, "max_rate": 20.0},
    "🎓 Education Loan":  {"rate": 10.5, "tenure": 8,  "min_rate": 8.0,  "max_rate": 15.0},
}

LOAN_SCHEMES = {
    "Scheme A — Low Rate":        {"rate_offset": -0.5, "fee_pct": 1.0,  "desc": "8.5% interest · 1% processing fee"},
    "Scheme B — Zero Fee":        {"rate_offset": +0.5, "fee_pct": 0.0,  "desc": "9% interest · No processing fee"},
    "Scheme C — Flexible Tenure": {"rate_offset": +0.25,"fee_pct": 0.5,  "desc": "8.75% interest · 0.5% processing fee · Flexible tenure"},
}

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────

if "dark_mode"  not in st.session_state: st.session_state.dark_mode  = True
if "scenarios"  not in st.session_state: st.session_state.scenarios  = []


# ─────────────────────────────────────────────
# INJECT CSS
# ─────────────────────────────────────────────

inject_css(st.session_state.dark_mode)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div class="emi-header">
  <h1>Loan EMI Calculator</h1>
  <p>Professional real-time EMI estimation · Compare loans · Export schedules</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR — INPUT CONTROLS
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    # Dark mode toggle
    dm_col1, dm_col2 = st.columns([3, 1])
    with dm_col1:
        st.markdown("**🌙 Dark Mode**")
    with dm_col2:
        if st.toggle("", value=st.session_state.dark_mode, key="dm_toggle"):
            st.session_state.dark_mode = True
        else:
            st.session_state.dark_mode = False

    st.divider()

    # Loan Type
    st.markdown("### 🏷️ Loan Type")
    loan_type = st.selectbox(
        "Select loan category",
        list(LOAN_TYPES.keys()),
        label_visibility="collapsed",
    )
    defaults = LOAN_TYPES[loan_type]

    # Loan Scheme
    st.markdown("### 🎁 Bank Scheme")
    scheme_name = st.selectbox(
        "Select scheme",
        list(LOAN_SCHEMES.keys()),
        label_visibility="collapsed",
    )
    scheme = LOAN_SCHEMES[scheme_name]
    st.caption(f"📌 {scheme['desc']}")

    st.divider()

    # Loan Amount slider
    st.markdown("### 💰 Loan Amount")
    principal = st.slider(
        "Loan Amount (₹)",
        min_value=10_000,
        max_value=50_00_000,
        value=10_00_000,
        step=10_000,
        format="₹%d",
        label_visibility="collapsed",
    )
    st.caption(f"Selected: **{format_inr(principal)}**")

    # Interest Rate slider
    st.markdown("### 📈 Interest Rate (%)")
    base_rate    = defaults["rate"] + scheme["rate_offset"]
    interest_rate = st.slider(
        "Annual Interest Rate",
        min_value=1.0,
        max_value=20.0,
        value=float(round(base_rate, 1)),
        step=0.1,
        format="%.1f%%",
        label_visibility="collapsed",
    )
    st.caption(f"Effective rate: **{interest_rate:.1f}% p.a.**")

    # Tenure slider
    st.markdown("### 📅 Loan Tenure (Years)")
    tenure = st.slider(
        "Tenure in years",
        min_value=1,
        max_value=30,
        value=defaults["tenure"],
        step=1,
        format="%d yrs",
        label_visibility="collapsed",
    )
    st.caption(f"Duration: **{tenure} years ({tenure*12} months)**")

    st.divider()

    # Reset button
    if st.button("Reset to Defaults", use_container_width=True):
        st.rerun()

    # Save scenario button
    if st.button(" Save Scenario", use_container_width=True):
        result = calculate_emi(principal, interest_rate, tenure)
        scenario = {
            "name":     f"Scenario {len(st.session_state.scenarios)+1}",
            "type":     loan_type,
            "scheme":   scheme_name,
            "amount":   principal,
            "rate":     interest_rate,
            "tenure":   tenure,
            "emi":      result["emi"],
            "saved_at": datetime.now().strftime("%H:%M:%S"),
        }
        st.session_state.scenarios.append(scenario)
        st.success("Scenario saved!")


# ─────────────────────────────────────────────
# MAIN CALCULATION
# ─────────────────────────────────────────────

result      = calculate_emi(principal, interest_rate, tenure)
emi         = result["emi"]
total_pay   = result["total_payment"]
total_int   = result["total_interest"]
fee         = principal * scheme["fee_pct"] / 100
total_cost  = total_pay + fee

# Processing fee info
st.info(f" **{scheme_name}** · Processing Fee: {format_inr(fee)} ({scheme['fee_pct']}%)")


# ─────────────────────────────────────────────
# RESULTS CARDS
# ─────────────────────────────────────────────

st.markdown('<div class="section-title"> Instant Results</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="result-card">
        <div class="label">Monthly EMI</div>
        <div class="value">{format_inr(emi)}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="result-card">
        <div class="label">Total Interest</div>
        <div class="value red">{format_inr(total_int)}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="result-card">
        <div class="label">Total Payment</div>
        <div class="value">{format_inr(total_pay)}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="result-card">
        <div class="label">Total Cost (incl. fee)</div>
        <div class="value green">{format_inr(total_cost)}</div>
    </div>""", unsafe_allow_html=True)

interest_pct = (total_int / total_pay) * 100
st.progress(int(100 - interest_pct), text=f"Principal covers **{100-interest_pct:.1f}%** of total payment")


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────

st.markdown('<div class="section-title"> Visualizations</div>', unsafe_allow_html=True)

ch1, ch2 = st.columns(2)

with ch1:
    st.subheader(" Principal vs Interest")
    st.plotly_chart(pie_chart(principal, total_int, st.session_state.dark_mode),
                    use_container_width=True)

with ch2:
    st.subheader("EMI vs Tenure")
    st.plotly_chart(emi_vs_tenure_chart(principal, interest_rate, st.session_state.dark_mode),
                    use_container_width=True)


# ─────────────────────────────────────────────
# AMORTIZATION TABLE
# ─────────────────────────────────────────────

st.markdown('<div class="section-title"> Amortization Schedule</div>', unsafe_allow_html=True)

amort_df = build_amortization(principal, interest_rate, tenure)

col_a, col_b = st.columns([3, 1])
with col_a:
    show_all = st.checkbox("Show all months", value=False)
with col_b:
    csv_data = amort_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Export CSV",
        data=csv_data,
        file_name=f"amortization_{loan_type.split()[1]}_{tenure}yr.csv",
        mime="text/csv",
        use_container_width=True,
    )

display_df = amort_df if show_all else amort_df.head(24)
st.dataframe(
    display_df.style
        .format({"EMI (₹)": "₹{:,.2f}", "Principal (₹)": "₹{:,.2f}",
                 "Interest (₹)": "₹{:,.2f}", "Balance (₹)": "₹{:,.2f}"})
        .background_gradient(subset=["Balance (₹)"], cmap="Blues_r")
        .background_gradient(subset=["Interest (₹)"], cmap="Reds"),
    use_container_width=True,
    height=400,
)


# ─────────────────────────────────────────────
# LOAN COMPARISON TOOL
# ─────────────────────────────────────────────

st.markdown('<div class="section-title">Loan Comparison Tool</div>', unsafe_allow_html=True)

with st.expander("⚖️ Compare Loan A vs Loan B", expanded=True):
    la_col, lb_col = st.columns(2)

    with la_col:
        st.markdown("#### Loan A")
        a_amount  = st.number_input("Amount A (₹)", 10_000, 50_00_000, 10_00_000, 10_000, key="a_amt")
        a_rate    = st.number_input("Rate A (%)", 1.0, 20.0, 9.0, 0.1, format="%.1f", key="a_rate")
        a_tenure  = st.number_input("Tenure A (yrs)", 1, 30, 10, key="a_ten")

    with lb_col:
        st.markdown("#### Loan B")
        b_amount  = st.number_input("Amount B (₹)", 10_000, 50_00_000, 10_00_000, 10_000, key="b_amt")
        b_rate    = st.number_input("Rate B (%)", 1.0, 20.0, 11.5, 0.1, format="%.1f", key="b_rate")
        b_tenure  = st.number_input("Tenure B (yrs)", 1, 30, 10, key="b_ten")

    loan_a_res = calculate_emi(a_amount, a_rate, a_tenure)
    loan_b_res = calculate_emi(b_amount, b_rate, b_tenure)

    # Determine best loan (lower total cost)
    best = "A" if loan_a_res["total_payment"] <= loan_b_res["total_payment"] else "B"

    r1, r2, r3 = st.columns(3)
    for col, label, key in [(r1, "Monthly EMI", "emi"), (r2, "Total Interest", "total_interest"), (r3, "Total Payment", "total_payment")]:
        with col:
            diff = loan_a_res[key] - loan_b_res[key]
            st.metric(
                f"{label} — A",
                format_inr(loan_a_res[key]),
                delta=f"{format_inr(abs(diff))} {'cheaper' if diff < 0 else 'costlier'} than B",
                delta_color="normal" if diff < 0 else "inverse",
            )
            st.metric(f"{label} — B", format_inr(loan_b_res[key]))

    st.markdown(f"""<div class="highlight-box">
        <b>🏆 Best Option:</b> &nbsp;<span class="best-badge">Loan {best}</span>
        &nbsp; saves you <b>{format_inr(abs(loan_a_res['total_payment'] - loan_b_res['total_payment']))}</b> in total repayment.
    </div>""", unsafe_allow_html=True)

    st.plotly_chart(comparison_bar_chart(loan_a_res, loan_b_res, st.session_state.dark_mode),
                    use_container_width=True)


# ─────────────────────────────────────────────
# SAVED SCENARIOS
# ─────────────────────────────────────────────

if st.session_state.scenarios:
    st.markdown('<div class="section-title">💾 Saved Scenarios</div>', unsafe_allow_html=True)
    scen_df = pd.DataFrame(st.session_state.scenarios)
    scen_df["emi"] = scen_df["emi"].apply(lambda x: f"₹{x:,.0f}")
    scen_df["amount"] = scen_df["amount"].apply(format_inr)
    st.dataframe(scen_df, use_container_width=True)

    if st.button("🗑️ Clear Saved Scenarios"):
        st.session_state.scenarios = []
        st.rerun()


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.divider()
st.markdown("""
<div style="text-align:center; opacity:0.5; font-size:0.82rem;">
Advanced Loan EMI Calculator · Built with Python & Streamlit ·
EMI formula: <code>P × r × (1+r)ⁿ / ((1+r)ⁿ − 1)</code>
</div>
""", unsafe_allow_html=True)