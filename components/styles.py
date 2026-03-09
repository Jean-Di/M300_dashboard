"""
CSS — M300 NEC Platform v5
SEforALL palette · Inter + Syne · Responsive · No icon-breaking overrides
"""

CSS = """
<style>
/* ── FONTS ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

/* Base font — only on html/body/[class*=css], NOT on span/div/p
   Avoids breaking Streamlit's internal SVG icon fonts (_arrow_right bug) */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Streamlit chrome removal ──────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, div[data-testid="stToolbar"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
}

/* ── Page background ───────────────────────────────────── */
html, body, .main, [data-testid="stAppViewContainer"] {
    background-color: #F5F7FA !important;
    color: #1B2E3C;
}

/* ═══════════════════════════
   JUSTIFIED TEXT — only where it makes sense (multi-line body text)
   ═══════════════════════════ */
.tab-desc {
    font-size: 0.75rem;
    color: #1B2E3C;
    line-height: 1.7;
    text-align: justify;
    margin-bottom: 12px;
    max-width: 860px;
}
.method-note {
    background: #FEF8EE;
    border: 1px solid #F7D08A;
    border-left: 4px solid #F7941D;
    border-radius: 0 6px 6px 0;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.75rem;
    color: #5C3D00;
    line-height: 1.6;
    text-align: justify;
}
.method-note-title {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #A06000;
    margin-bottom: 4px;
    text-align: left;   /* titles: NEVER justify */
}
.info-box {
    background: #E8F7F7;
    border-left: 3px solid #00A19A;
    padding: 6px 9px;
    font-size: 0.68rem;
    color: #1B5C59;
    border-radius: 0 4px 4px 0;
    line-height: 1.5;
    margin-top: 4px;
    text-align: justify;
}
.context-sub {
    font-size: 0.74rem;
    color: #6B7A8D;
    line-height: 1.6;
    max-width: 900px;
    margin-top: 3px;
    text-align: justify;
}

/* ═══════════════════════════
   PAGE HEADER
   ═══════════════════════════ */
.page-header {
    background: #1B3A5C;
    padding: 13px 20px 11px;
    margin-bottom: 0;
    border-bottom: 3px solid #00A19A;
}
.page-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.05rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.03em;
    line-height: 1.2;
    text-align: left;
}
.page-subtitle {
    font-size: 0.68rem;
    color: #7BA8C9;
    font-weight: 400;
    margin-top: 2px;
    letter-spacing: 0.02em;
    text-align: left;
}

/* ═══════════════════════════
   CONTEXT BAND
   ═══════════════════════════ */
.context-band {
    background: #FFFFFF;
    border-bottom: 1px solid #DDE2E8;
    padding: 11px 20px 10px;
}
.context-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #1B2E3C;
    line-height: 1.55;
    max-width: 900px;
    text-align: left;
}
.context-meta {
    font-size: 0.63rem;
    color: #A8B4C0;
    margin-top: 7px;
    text-align: left;
}

/* ═══════════════════════════
   KPI BAND
   ═══════════════════════════ */
.kpi-band {
    display: flex;
    gap: 8px;
    padding: 10px 0 8px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
}
.kpi-band::-webkit-scrollbar { display: none; }
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #DDE2E8;
    border-radius: 8px;
    padding: 11px 14px 9px;
    flex: 1 1 120px;
    min-width: 118px;
    max-width: 200px;
}
.kpi-value {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.45rem;
    font-weight: 800;
    color: #F7941D;
    line-height: 1;
    margin-bottom: 5px;
    white-space: nowrap;
    text-align: left;
}
.kpi-label {
    font-size: 0.6rem;
    color: #1B3A5C;
    text-transform: capitalize;
    letter-spacing: 0.07em;
    font-weight: 500;
    line-height: 1.4;
    text-align: left;
}

/* ═══════════════════════════
   SECTION SEPARATOR
   ═══════════════════════════ */
.section-sep {
    border: none;
    border-top: 1px solid #DDE2E8;
    margin: 7px 0;
}

/* ═══════════════════════════
   PANEL TITLE
   ═══════════════════════════ */
.panel-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.56rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #1B3A5C;
    border-bottom: 2px solid #00A19A;
    padding-bottom: 5px;
    margin-bottom: 12px;
    text-align: left;
}

/* ═══════════════════════════
   COUNTRY PROFILE
   ═══════════════════════════ */
.country-header {
    background: linear-gradient(135deg, #1B3A5C 0%, #234B77 100%);
    border-radius: 8px;
    padding: 12px 14px 10px;
    margin-bottom: 10px;
}
.country-name {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.05rem;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 4px;
    line-height: 1.2;
    text-align: left;
}
.country-meta {
    font-size: 0.62rem;
    color: #7BA8C9;
    font-weight: 400;
    text-align: left;
}

/* ═══════════════════════════
   KPI BLOCKS
   ═══════════════════════════ */
.kpi-block {
    background: #FFFFFF;
    border: 1px solid #DDE2E8;
    border-radius: 7px;
    padding: 10px 12px 8px;
    margin-bottom: 7px;
}
.kpi-block-title {
    font-size: 0.58rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6B7A8D;
    margin-bottom: 8px;
    text-align: left;
}
.kpi-block-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 8px;
}
.kpi-block-item { flex: 1; }
.kpi-num-cur {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.25rem;
    font-weight: 800;
    color: #00A19A;
    line-height: 1;
}
.kpi-num-tgt {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.25rem;
    font-weight: 800;
    color: #F7941D;
    line-height: 1;
}
.kpi-num-invest {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.1rem;
    font-weight: 800;
    color: #1B3A5C;
    line-height: 1;
}
.kpi-sub { font-size: 0.58rem; font-weight: 500; margin-top: 3px; }
.kpi-sub-cur { color: #00A19A; }
.kpi-sub-tgt { color: #F7941D; }
.kpi-sub-muted { color: #9AA5B0; }

/* ═══════════════════════════
   PROGRESS BARS
   ═══════════════════════════ */
.prog-bar-wrap { margin-top: 7px; }
.prog-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.58rem;
    color: #A8B4C0;
    margin-bottom: 3px;
}
.prog-bar-bg {
    height: 5px;
    background: #E8EDF2;
    border-radius: 3px;
    overflow: hidden;
}
.prog-bar-fill {
    height: 100%;
    border-radius: 3px;
    background: #00A19A;
    transition: width 0.3s ease;
}
.cov-bar-bg { height: 5px; background: #E8EDF2; border-radius: 3px; overflow: hidden; }
.cov-bar-fill { height: 100%; border-radius: 3px; background: #00A19A; }

/* ═══════════════════════════
   STREAMLIT OVERRIDES
   ═══════════════════════════ */
div[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #DDE2E8 !important;
    border-radius: 7px !important;
    padding: 9px 11px !important;
}
[data-testid="metric-container"] > div:first-child {
    font-size: 0.58rem !important;
    color: #6B7A8D !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600 !important;
}
[data-testid="metric-container"] > div:nth-child(2) {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    color: #1B2E3C !important;
}
.stSelectbox > div > div {
    background: #FAFBFC !important;
    border: 1px solid #DDE2E8 !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
}
label[data-testid="stWidgetLabel"] {
    font-size: 0.64rem !important;
    color: #6B7A8D !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.74rem !important;
    font-weight: 500 !important;
    color: #6B7A8D !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00A19A !important;
    border-bottom-color: #00A19A !important;
}
.stButton > button {
    white-space: nowrap !important;
    height: auto !important;
    min-height: 38px !important;
}
.stButton > button[kind="primary"] {
    background: #1B3A5C !important;
    border-color: #1B3A5C !important;
    color: white !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border-color: #DDE2E8 !important;
    color: #1B3A5C !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
}
.stButton > button:hover {
    border-color: #00A19A !important;
    color: #00A19A !important;
}
hr { border-color: #DDE2E8 !important; margin: 8px 0 !important; }

/* ═══════════════════════════
   MAP / CHART WRAPPERS
   ═══════════════════════════ */
.map-wrap {
    background: #FFFFFF;
    border: 1px solid #DDE2E8;
    border-radius: 8px;
    padding: 4px;
    overflow: hidden;
}
.chart-wrap {
    background: #FFFFFF;
    border: 1px solid #DDE2E8;
    border-radius: 8px;
    padding: 12px 8px 6px;
}
.chart-title {
    font-size: 0.7rem;
    font-weight: 700;
    color: #1B3A5C;
    margin-bottom: 6px;
    text-align: left;
    letter-spacing: 0.03em;
}
.chart-sub {
    font-size: 0.62rem;
    color: #9AA5B0;
    margin-bottom: 8px;
    text-align: left;
}
.no-data-ph {
    text-align: center;
    color: #A8B4C0;
    padding: 40px 12px;
    font-size: 0.78rem;
    line-height: 1.8;
}

/* ═══════════════════════════
   FOOTER
   ═══════════════════════════ */
.footer {
    background: #1B3A5C;
    border-radius: 6px;
    padding: 9px 18px;
    margin-top: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
}
.footer-text { font-size: 0.63rem; color: #7BA8C9; }

/* ═══════════════════════════
   DIALOG
   ═══════════════════════════ */
div[data-testid="stDialog"] > div {
    width: 82vw !important;
    max-width: 82vw !important;
}
div[data-testid="stDialog"] > div > div { width: 100% !important; }

/* ═══════════════════════════
   SCROLLBAR
   ═══════════════════════════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #F5F7FA; }
::-webkit-scrollbar-thumb { background: #C5CDD6; border-radius: 2px; }

/* ═══════════════════════════
   RESPONSIVE — MOBILE ≤ 768px
   ═══════════════════════════ */
@media screen and (max-width: 768px) {
    .main .block-container {
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        padding-top: 0.2rem !important;
    }
    .page-title  { font-size: 0.85rem !important; }
    .page-subtitle { font-size: 0.6rem !important; }
    .kpi-band { gap: 4px; padding: 6px 0; }
    .kpi-card { min-width: 90px; max-width: 150px; padding: 7px 8px; }
    .kpi-value { font-size: 1.1rem; }
    .kpi-label { font-size: 0.54rem; }
    .context-title { font-size: 0.78rem; }
    .context-sub   { font-size: 0.69rem; }
    .country-name  { font-size: 0.9rem; }
    .kpi-num-cur, .kpi-num-tgt { font-size: 1.0rem; }
    .tab-desc { font-size: 0.7rem; }
    /* Stack columns */
    section.main > div > div > div > div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    section.main > div > div > div > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    div[data-testid="stDialog"] > div {
        width: 96vw !important;
        max-width: 96vw !important;
    }
    .chart-wrap { padding: 8px 4px 4px; }
}

/* ═══════════════════════════
   RESPONSIVE — TABLET 769-1024px
   ═══════════════════════════ */
@media screen and (min-width: 769px) and (max-width: 1024px) {
    .kpi-card { min-width: 105px; }
    .kpi-value { font-size: 1.25rem; }
    .main .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
}

/* ═══════════════════════════
   LARGE SCREENS ≥ 1440px
   ═══════════════════════════ */
@media screen and (min-width: 1440px) {
    .kpi-value { font-size: 1.6rem; }
    .kpi-label { font-size: 0.65rem; }
    .context-title { font-size: 0.95rem; }
}
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
