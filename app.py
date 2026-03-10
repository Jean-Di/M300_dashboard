"""
M300 National Energy Compacts — Africa Tracker  v4
===================================================
SEforALL palette · Inter + Syne · Mobile-responsive
streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(
    page_title="M300 - Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

USE_REAL_DATA = True
EXCEL_FILE    = "data/M300 Compacts Dataset.xlsx"

from components.styles    import inject_css
from components.map_chart import (
    build_bubble_capacity_investment, build_choropleth, build_completeness_map, build_category_bar, build_quadrant_scatter,
    build_radar_chart, build_comparison_grouped_bar, build_comparison_radar,
    build_comparison_lollipop, build_comparison_heatmap,
    build_rankings_chart, build_scatter_elec_vs_cooking, build_scorecard_chart,
    _get_comparison_data, ISLAND_MARKERS,
    TEAL, ORANGE, NAVY,
)
from utils.i18n  import t
from data.config import (
    NARRATIVE, LAST_UPDATED, LAST_UPDATED_EN, TARGET_YEAR, CURRENT_YEAR,
)

inject_css()


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Loading data…")
def load_data(use_real, path):
    if use_real:
        from data.excel_loader import load_nec_excel
        return load_nec_excel(path)
    from data.mock_data import get_mock_data
    return get_mock_data()

data          = load_data(USE_REAL_DATA, EXCEL_FILE)
long_df       = data["long"]
countries_df  = data["countries"]
indicators_df = data["indicators"]
categories    = data["categories"]
key_metrics   = data["key_metrics"]

VALID_ISO3 = set(countries_df["iso3"].tolist())

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {"lang":"en", "selected_iso3":None, "page":"dashboard"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

lang = st.session_state.lang
page = st.session_state.page

# ── Helpers ───────────────────────────────────────────────────────────────────
def _f(v, fmt="{:.1f}", sfx=""):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "—"
    return fmt.format(v) + (" " + sfx if sfx else "")

def _bar(pct, height=5):
    pct = min(100, max(0, pct or 0))
    return (f'<div class="prog-bar-bg" style="height:{height}px;">'
            f'<div class="prog-bar-fill" style="width:{pct:.0f}%;height:{height}px;"></div></div>')

def _kpi_card(value, label, accent=TEAL):
    return (f'<div class="kpi-card" style="border-top:3px solid {accent};">'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-label">{label}</div></div>')

def _nc():
    return "country_name_en" if lang == "en" else "country_name_fr"


def _handle_map_click(event):
    if not (event and hasattr(event, "selection") and event.selection):
        return
    pts = event.selection.get("points", [])
    if not pts:
        return
    pt = pts[0]

    # 1. Choropleth standard
    loc = pt.get("location")
    if loc and loc in VALID_ISO3:
        st.session_state.selected_iso3 = loc; st.rerun()

    # 2. Island — customdata[0] = iso3
    cd = pt.get("customdata")
    if cd and len(cd) >= 1 and cd[0] in VALID_ISO3:
        st.session_state.selected_iso3 = cd[0]; st.rerun()

    # 3. Fallback — cherche iso3 dans hovertext ou bbox
    for field in ["hovertext", "text", "bbox"]:
        val = pt.get(field, "")
        if isinstance(val, str):
            for iso3 in VALID_ISO3:
                if iso3 in val:
                    st.session_state.selected_iso3 = iso3; st.rerun()

    # 4. Fallback texte — normalise les accents
    import unicodedata
    def _norm(s):
        return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower().strip()

    text = pt.get("text", "")
    if text:
        text_n = _norm(str(text))
        for _, row in countries_df.iterrows():
            if (_norm(row["country_name_en"]) in text_n or
                _norm(row["country_name_fr"]) in text_n or
                text_n in _norm(row["country_name_en"])):
                st.session_state.selected_iso3 = row["iso3"]; st.rerun()

    # 5. Trace name
    tn = ""
    if isinstance(pt.get("data"), dict):
        tn = pt["data"].get("name", "")
    if isinstance(tn, str) and tn.startswith("island_") and tn[7:] in VALID_ISO3:
        st.session_state.selected_iso3 = tn[7:]; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MODAL — All indicators (80% screen)
# ══════════════════════════════════════════════════════════════════════════════
@st.dialog("Country Indicators", width="large")
def show_indicators_modal(iso3_init):
    _lang = st.session_state.lang
    nc    = "country_name_en" if _lang == "en" else "country_name_fr"
    all_names = sorted(countries_df[nc].tolist())
    n2i = dict(zip(countries_df[nc], countries_df["iso3"]))
    i2n = dict(zip(countries_df["iso3"], countries_df[nc]))
    cur_name = i2n.get(iso3_init, iso3_init)

    col_sel, col_pdf = st.columns([2, 2])
    with col_sel:
        chosen = st.selectbox("Country", all_names,
                              index=all_names.index(cur_name) if cur_name in all_names else 0,
                              key="modal_country")
    iso3 = n2i.get(chosen, iso3_init)

    with col_pdf:
        with st.expander("Customise & download PDF", expanded=False):
            st.caption("Key indicators are always included. Select additional categories below.")
            cd_all     = long_df[(long_df["iso3"]==iso3) & (long_df["has_data"]==True)]
            cats_avail = [c for c in categories if not cd_all[cd_all["category"]==c].empty]
            PRIO = {"Electricity Access","Renewables, Climate & Efficiency","Clean Cooking","Finance"}
            default_sel = [c for c in cats_avail if c in PRIO] or cats_avail[:2]
            sel_cats_pdf = st.multiselect("Additional categories", cats_avail, default_sel,
                                          key="pdf_cats")
            if st.button("Generate PDF", type="primary", use_container_width=True, key="gen_pdf"):
                try:
                    from components.pdf_generator import generate_country_pdf
                    km_row  = key_metrics[key_metrics["iso3"]==iso3]
                    km_dict = km_row.iloc[0].to_dict() if not km_row.empty else {}
                    cat_ind = {}
                    for cat in sel_cats_pdf:
                        rows = cd_all[cd_all["category"]==cat]
                        if not rows.empty:
                            cat_ind[t(cat, _lang)] = [
                                (r["indicator"], r["value"], r["unit"], r["ind_type"])
                                for _, r in rows.iterrows()
                            ]
                    pdf_bytes = generate_country_pdf(chosen, iso3, km_dict, cat_ind, _lang)
                    st.download_button(
                        f"Download — {chosen}.pdf", pdf_bytes,
                        f"NEC_{iso3}_{_lang.upper()}.pdf", "application/pdf",
                        use_container_width=True, key="dl_pdf",
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}")

    st.divider()

    cd = long_df[(long_df["iso3"]==iso3) & (long_df["has_data"]==True)].copy()
    cats_present = [c for c in categories if not cd[cd["category"]==c].empty]
    if not cats_present:
        st.info("No data reported for this country."); return

    st.caption(f"**{cd['indicator'].nunique()}** indicators reported")
    tabs = st.tabs([t(c, _lang) for c in cats_present])
    for tab, cat in zip(tabs, cats_present):
        with tab:
            cat_d = cd[cd["category"]==cat]
            cur_d = cat_d[cat_d["ind_type"]=="current"]
            tgt_d = cat_d[cat_d["ind_type"]=="target"]

            def _rows(container, df_rows, color, title):
                import contextlib
                ctx = container if hasattr(container, "__enter__") else contextlib.nullcontext()
                wr  = container if hasattr(container, "markdown") else st
                with ctx:
                    wr.markdown(
                        f'<div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;'
                        f'letter-spacing:.1em;color:{color};border-bottom:1.5px solid {color};'
                        f'padding-bottom:3px;margin-bottom:8px;">{title}</div>',
                        unsafe_allow_html=True,
                    )
                    for _, row in df_rows.iterrows():
                        val = f"{row['value']:,.1f} {row['unit']}" if pd.notna(row["value"]) else "—"
                        cmt = row.get("comment","")
                        wr.markdown(
                            f'<div style="display:flex;justify-content:space-between;'
                            f'padding:5px 0;border-bottom:1px solid #F0F2F5;font-size:0.79rem;">'
                            f'<span style="color:#1B2E3C;flex:1;padding-right:8px;">{row["indicator"]}</span>'
                            f'<span style="font-weight:700;color:#1B2E3C;white-space:nowrap;">{val}</span></div>'
                            + (f'<div style="font-size:0.65rem;color:#9AA5B0;padding:2px 0 3px;'
                               f'font-style:italic;">{cmt}</div>' if cmt else ""),
                            unsafe_allow_html=True,
                        )

            if not cur_d.empty and not tgt_d.empty:
                c1, c2 = st.columns(2)
                _rows(c1, cur_d, TEAL,   "Current values")
                _rows(c2, tgt_d, ORANGE, "2030 Targets")
            elif not cur_d.empty:
                _rows(st, cur_d, TEAL,   "Current values")
            else:
                _rows(st, tgt_d, ORANGE, "2030 Targets")

    st.divider()
    st.caption("Sources: M300 National Energy Compacts · SEforALL  "
               "· Data reflects Compacts as signed, not interpolated.")


# ══════════════════════════════════════════════════════════════════════════════
# SHARED HEADER
# ══════════════════════════════════════════════════════════════════════════════
nav      = NARRATIVE[lang]
date_str = LAST_UPDATED if lang == "fr" else LAST_UPDATED_EN

st.markdown(
    f'<div style="font-size:1.1rem;font-weight:700;color:#FFFFFF;'
    f'background:#1B3A5C;padding:14px 20px;'          # ← retiré text-align:justify
    f'border-bottom:3px solid #F7941D;">'
    f'<div style="font-family: \'Syne\', sans-serif !important;font-size:1.05rem;'
    f'font-weight:800;letter-spacing:0.03em;line-height:1.2;">{nav["headline"]}</div>'
    f'<div style="font-size:0.68rem;color:#7BA8C9;font-weight:400;'
    f'margin-top:2px;letter-spacing:0.02em;">{nav["subtitle"]}</div></div>',  # ← retiré aussi
    unsafe_allow_html=True,
)

# Navigation with FR/EN buttons on the right
nav_cols = st.columns([1, 1, 1, 5, 0.8, 0.8], gap="small")
_pages = [("dashboard","Dashboard"),("comparison","Comparison"),("methodology","Methodology")]

for i, (pid, plbl) in enumerate(_pages):
    with nav_cols[i]:
        if st.button(plbl, key=f"nav_{pid}",
                     type="primary" if page==pid else "secondary",
                     use_container_width=True):
            st.session_state.page = pid; st.rerun()

with nav_cols[4]:
    if st.button("FR", type="primary" if lang=="fr" else "secondary",
                 use_container_width=True, key="btn_fr"):
        st.session_state.lang = "fr"; st.rerun()

with nav_cols[5]:
    if st.button("EN", type="primary" if lang=="en" else "secondary",
                 use_container_width=True, key="btn_en"):
        st.session_state.lang = "en"; st.rerun()

st.markdown('<hr class="section-sep"/>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════════
if page == "methodology":
    st.markdown(
        f'<div class="context-band">'
        f'<div class="context-title">{nav["intro"]}</div>'
        f'<div class="context-sub" style="margin-top:4px;">{nav["mission"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")
    for cat in sorted(indicators_df["category"].unique().tolist()):
        with st.expander(t(cat, lang)):
            ci = indicators_df[indicators_df["category"]==cat]
            for _, r in ci.iterrows():
                dot_c = {
                    "current": TEAL, "target": ORANGE
                }.get(r["ind_type"], "#9AA5B0")
                cmt = r.get("comment","")
                st.markdown(
                    f'<div style="padding:5px 0;border-bottom:1px solid #EEF0F3;">'
                    f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;'
                    f'background:{dot_c};margin-right:8px;vertical-align:middle;"></span>'
                    f'<span style="font-size:0.79rem;font-weight:500;color:#1B2E3C;">{r["indicator"]}</span>'
                    f'<span style="font-size:0.64rem;color:#9AA5B0;margin-left:6px;">({r["unit"]})</span>'
                    + (f'<div style="font-size:0.7rem;color:#7A8A9A;margin:2px 0 0 15px;'
                       f'font-style:italic;">{cmt}</div>' if cmt else "")
                    + '</div>',
                    unsafe_allow_html=True,
                )
    st.divider()
    st.markdown(
        f'<div class="method-note"><div class="method-note-title">Data note</div>'
        f'{nav.get("disclaimer","")}</div>',
        unsafe_allow_html=True,
    )
    
    st.markdown(
         f'<div class="footer">'
        f'<div class="footer-text">Sources: M300 National Energy Compacts · SEforALL</div>'
         f'<div class="footer-text">Last updated: {date_str}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COUNTRY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
if page == "comparison":
    st.markdown(
        f'<div class="context-band">'
        f'<div class="context-title">Country Comparison - Key Indicators</div>'
        f'<div class="context-sub">Select up to 10 countries and a chart type. '
        f'Values are declared targets and current values from National Energy Compacts.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    nc_col    = _nc()
    all_names = sorted(countries_df[nc_col].tolist())
    n2i       = dict(zip(countries_df[nc_col], countries_df["iso3"]))
    i2n       = dict(zip(countries_df["iso3"], countries_df[nc_col]))

    # Controls
    ctrl1, ctrl2 = st.columns([3, 1])
    with ctrl1:
        sel_names = st.multiselect(
            "Countries to compare (up to 10)",
            all_names, default=all_names[:6], max_selections=10, key="comp_names",
        )
    with ctrl2:
        chart_type = st.selectbox(
            "Chart type",
            ["Grouped bars", "Radar / spider", "Dot plot (ranked)", "Heatmap",],
            key="comp_chart_type",
        )

    sel_iso3s = [n2i[n] for n in sel_names if n in n2i]
    nc_map    = {iso3: i2n.get(iso3, iso3) for iso3 in sel_iso3s}

    if len(sel_iso3s) < 2:
        st.info("Select at least 2 countries to start comparing.")
        st.caption(f"Sources: M300 National Energy Compacts · SEforALL  |  Last updated: {date_str}")
        st.stop()

    df_comp = _get_comparison_data(key_metrics, sel_iso3s, nc_map)

    # ── Default: always show two charts ──────────────────────────────────────
    if chart_type == "Grouped bars":
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.1em;color:{TEAL};margin-bottom:4px;">'
            f'Electricity Access · Renewable Share · Clean Cooking — Current vs. 2030 Target</div>',
            unsafe_allow_html=True,
        )
        fig1 = build_comparison_grouped_bar(df_comp)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.1em;color:{NAVY};margin-bottom:4px;">'
            f'Radar — Current profile per country (normalised 0-100)</div>',
            unsafe_allow_html=True,
        )
        fig2 = build_comparison_radar(df_comp, lang)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "Radar / spider":
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.1em;color:{NAVY};margin-bottom:4px;">'
            f'Radar — Current profile per country</div>',
            unsafe_allow_html=True,
        )
        fig1 = build_comparison_radar(df_comp, lang)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.1em;color:{TEAL};margin-bottom:4px;">'
            f'Heatmap — all 4 key indicators</div>',
            unsafe_allow_html=True,
        )
        fig2 = build_comparison_heatmap(df_comp)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "Dot plot (ranked)":
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.1em;color:{TEAL};margin-bottom:4px;">'
            f'Electricity Access — Ranked (current & 2030 target)</div>',
            unsafe_allow_html=True,
        )
        fig1 = build_comparison_lollipop(df_comp)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.1em;color:{NAVY};margin-bottom:4px;">'
            f'Grouped bars — all 3 percentage indicators</div>',
            unsafe_allow_html=True,
        )
        fig2 = build_comparison_grouped_bar(df_comp)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    elif chart_type == "Heatmap":
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.1em;color:{NAVY};margin-bottom:4px;">'
            f'Heatmap — Countries × Key indicators (current values)</div>',
            unsafe_allow_html=True,
        )
        fig1 = build_comparison_heatmap(df_comp)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.1em;color:{TEAL};margin-bottom:4px;">'
            f'Radar — Normalised current profile</div>',
            unsafe_allow_html=True,
        )
        fig2 = build_comparison_radar(df_comp, lang)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
         f'<div class="footer">'
        f'<div class="footer-text">Sources: M300 National Energy Compacts · SEforALL</div>'
         f'<div class="footer-text">Last updated: {date_str}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

# Context band
st.markdown(
    f'<div class="context-band">'
    f'<div class="context-title">{nav["intro"]}</div>'
    f'<div class="context-sub">{nav["mission"]}</div>'
    f'<div class="context-meta">{nav["update_note"].format(date=date_str)}</div>'
    f'</div>',
    unsafe_allow_html=True, 
)

# KPI band — 2030 targets only
kpi_title = "Mission 300 en un coup d'œil" if lang == "fr" else "Mission 300 at a Glance"
st.markdown(
    f'<div style="font-size:1.1rem;font-weight:700;color:#FFFFFF;'
    f'background:#1B3A5C;text-align:center;padding:14px 20px;'
    f'border-bottom:3px solid #F7941D;margin-bottom:8px;">'
    f'{kpi_title}</div>',
    unsafe_allow_html=True,
)

n_c     = len(countries_df)
n_i     = len(indicators_df)
e_tgt   = key_metrics["elec_access_tgt"].mean()
c_tgt   = key_metrics["cap_target_mw"].sum()
r_tgt   = key_metrics["renew_share_tgt"].mean()
k_tgt   = key_metrics["cooking_tgt"].mean()
inv_tot = key_metrics["private_invest_usd"].sum()

st.markdown(
    '<div class="kpi-band">'
    + _kpi_card(str(n_c),   "Countries covered",              NAVY)
    + _kpi_card(str(n_i),   "Indicators tracked",            NAVY)
    + _kpi_card(_f(e_tgt, sfx="%"), "Avg. electricity access · 2030",  NAVY)
    + _kpi_card(f"{c_tgt/1000:.1f} GW" if not np.isnan(c_tgt) else "—",
                "Total installed capacity · 2030", NAVY)
    + _kpi_card(_f(r_tgt, sfx="%"), "Avg. renewable share · 2030",     NAVY)
    + _kpi_card(_f(k_tgt, sfx="%"), "Avg. clean cooking · 2030",       NAVY)
    + _kpi_card(f"${inv_tot/1e9:.1f}B" if not np.isnan(inv_tot) else "—",
                "Total private investment · 2030",  NAVY)
    + '</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="section-sep"/>', unsafe_allow_html=True)


# ── THREE-COLUMN LAYOUT ───────────────────────────────────────────────────────
left_col, mid_col, right_col = st.columns([0.85, 3.0, 1.15], gap="small")


# ══════════════════════════════════════
# LEFT — Filters
# ══════════════════════════════════════
with left_col:
    st.markdown('<div class="panel-title">Filters</div>', unsafe_allow_html=True)

    # Display mode — NO "Data completeness"
    mode_opts = {
        "Current values": "current",
        "2030 Targets":   "target",
    }
    mode_lbl  = st.selectbox("Display mode", list(mode_opts.keys()), key="mode_sel")
    disp_mode = mode_opts[mode_lbl]

    cat_disp = {c: t(c, lang) for c in categories}
    sel_cat  = st.selectbox("Category", categories,
                            format_func=lambda c: cat_disp.get(c, c), key="cat_sel")

    sel_ind, ind_unit = None, "%"
    ftype    = "current" if disp_mode == "current" else "target"
    ind_list = indicators_df[
        (indicators_df["category"]==sel_cat) & (indicators_df["ind_type"]==ftype)
    ]["indicator"].tolist()
    if not ind_list:
        ind_list = indicators_df[indicators_df["category"]==sel_cat]["indicator"].tolist()
    if ind_list:
        sel_ind  = st.selectbox("Indicator", ind_list, key="ind_sel")
        u_vals   = indicators_df.loc[indicators_df["indicator"]==sel_ind,"unit"].values
        ind_unit = u_vals[0] if len(u_vals) else ""
        cmt_vals = indicators_df.loc[indicators_df["indicator"]==sel_ind,"comment"].values
        if len(cmt_vals) and cmt_vals[0]:
            st.markdown(f'<div class="info-box">{cmt_vals[0]}</div>', unsafe_allow_html=True)

    st.divider()

    if sel_ind:
        n_with = int(long_df[long_df["indicator"]==sel_ind]["has_data"].sum())
        n_tot  = len(countries_df)
        pct_c  = round(n_with / n_tot * 100) if n_tot else 0
        st.markdown(
            f'<div style="font-size:0.68rem;color:#6B7A8D;margin-bottom:4px;">'
            f'<b>{n_with}</b>/{n_tot} countries with data</div>'
            f'<div class="cov-bar-bg"><div class="cov-bar-fill" style="width:{pct_c}%;"></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("")

    # Map legend
    st.markdown(
        f'<div style="font-size:0.63rem;color:#7A8A9A;line-height:2.1;">'
        f'<span style="display:inline-block;width:11px;height:8px;background:#C2CDD6;'
        f'border:1px solid #9AA5B0;border-radius:2px;margin-right:5px;vertical-align:middle;"></span>'
        f'In M300 — data not reported<br>'
        f'<span style="display:inline-block;width:11px;height:8px;background:#E8E0D0;'
        f'border:1px solid #B8B0A0;border-radius:2px;margin-right:5px;vertical-align:middle;"></span>'
        f'Not in Mission 300'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown(
        '<div style="font-size:0.62rem;color:#9AA5B0;line-height:1.8;">'
        'Sources<br>M300 National Energy Compacts<br>SEforALL'
        '</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.selected_iso3:
        st.markdown("")
        if st.button("Clear selection", use_container_width=True, key="reset_btn"):
            st.session_state.selected_iso3 = None; st.rerun()


# ══════════════════════════════════════
# CENTER — tabs
# ══════════════════════════════════════
with mid_col:
    tab_map, tab_tbl, tab_cat, tab_rank, tab_score, tab_gaps = st.tabs([
        "Map",
        "Data table",
        "By category",
        "Rankings",
        "Scorecard",
        "Data coverage",
    ])

    # ── Build choropleth ──────────────────────────────────────────────────────
    def _build_map():
        iso3_sel = st.session_state.selected_iso3
        if sel_ind:
            mode_type = "current" if disp_mode == "current" else "target"
            ind_vals  = long_df[
                (long_df["indicator"]==sel_ind) & (long_df["ind_type"]==mode_type)
            ][["iso3","value"]].copy()
            map_df = countries_df[["iso3","country_name_en","country_name_fr"]].merge(
                ind_vals, on="iso3", how="left"
            )
            return build_choropleth(map_df, sel_ind, ind_unit, lang, iso3_sel)
        return build_completeness_map(countries_df, long_df, lang)

    # ── MAP tab ───────────────────────────────────────────────────────────────
    with tab_map:
        st.markdown('<div class="map-wrap">', unsafe_allow_html=True)
        map_fig   = _build_map()
        map_event = st.plotly_chart(
            map_fig, use_container_width=True,
            on_select="rerun", key="main_map",
            config={"displayModeBar": False, "scrollZoom": False},
        )
        st.markdown('</div>', unsafe_allow_html=True)
        _handle_map_click(map_event)

        # DEBUG TEMPORAIRE — à retirer après
        if map_event and hasattr(map_event, "selection") and map_event.selection:
            st.write("DEBUG click data:", map_event.selection)

    # ── DATA TABLE tab ────────────────────────────────────────────────────────
    with tab_tbl:
        nc_col = _nc()
        if sel_ind:
            mtype = "current" if disp_mode == "current" else "target"
            ind_r = long_df[
                (long_df["indicator"]==sel_ind) & (long_df["ind_type"]==mtype)
            ][["iso3","value","source","has_data"]].copy()
            tbl = countries_df[["iso3",nc_col]].merge(ind_r, on="iso3", how="left")
            tbl["has_data"] = tbl["has_data"].fillna(False).map({True:"Reported", False:"Not reported"})
            tbl["source"]   = tbl["source"].fillna("—")
            tbl["value"]    = tbl["value"].apply(lambda v: f"{v:,.1f}" if pd.notna(v) else "—")
            tbl = tbl.rename(columns={
                nc_col:"Country","value":ind_unit or "Value","source":"Source","has_data":"Data"
            }).sort_values("Country").reset_index(drop=True)
            st.dataframe(tbl, use_container_width=True, hide_index=True, height=490)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as wr:
                tbl.to_excel(wr, index=False, sheet_name="NEC")
            st.download_button("Export (Excel)", buf.getvalue(),
                               f"NEC_{sel_ind[:25].replace(' ','_')}.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

    # ── BY CATEGORY tab ───────────────────────────────────────────────────────
    with tab_cat:
        iso3 = st.session_state.selected_iso3
        if iso3:
            nm = countries_df.loc[countries_df["iso3"]==iso3, _nc()].values
            st.markdown(f"**{nm[0] if len(nm) else iso3}** — {t(sel_cat, lang)}")
            st.plotly_chart(
                build_category_bar(long_df, iso3, sel_cat, lang),
                use_container_width=True, config={"displayModeBar": False},
            )
        else:
            st.markdown('<div class="no-data-ph">Click a country on the map.</div>',
                        unsafe_allow_html=True)

    # ── RANKINGS tab ─────────────────────────────────────────────────────────
    with tab_rank:
        st.markdown(
            f'<div style="font-size:0.62rem;color:#9AA5B0;margin-bottom:8px;">'
            f'Top & bottom countries for each key indicator (current values)</div>',
            unsafe_allow_html=True,
        )
        r1, r2 = st.columns(2)
        with r1:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(
                build_rankings_chart(key_metrics, countries_df,
                                     "elec_access_cur", "Electricity Access", "%", lang),
                use_container_width=True, config={"displayModeBar": False}, key="rank_elec",
            )
            st.markdown('</div>', unsafe_allow_html=True)
        with r2:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(
                build_rankings_chart(key_metrics, countries_df,
                                     "cooking_cur", "Clean Cooking", "%", lang),
                use_container_width=True, config={"displayModeBar": False}, key="rank_cook",
            )
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")
        r3, r4 = st.columns(2)
        with r3:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(
                build_rankings_chart(key_metrics, countries_df,
                                     "renew_share_cur", "Renewable Share", "%", lang),
                use_container_width=True, config={"displayModeBar": False}, key="rank_ren",
            )
            st.markdown('</div>', unsafe_allow_html=True)
        with r4:
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(
                build_rankings_chart(key_metrics, countries_df,
                                     "private_invest_usd", "Private Investment Required", "USD", lang),
                use_container_width=True, config={"displayModeBar": False}, key="rank_inv",
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── SCORECARD tab ─────────────────────────────────────────────────────────
    with tab_score:
        st.markdown(
            f'<div style="font-size:0.62rem;color:#9AA5B0;margin-bottom:8px;">'
            f'All 30 countries × 4 key indicators — '
            f'<span style="color:{TEAL};">■ Current</span>  '
            f'<span style="color:{ORANGE};">■ 2030 Target</span></div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            build_scorecard_chart(key_metrics, countries_df, lang),
            use_container_width=True, config={"displayModeBar": False}, key="scorecard",
        )

    # ── DATA COVERAGE tab ────────────────────────────────────────────────────
    with tab_gaps:
        st.markdown(
            f'<div style="font-size:0.62rem;color:#9AA5B0;margin-bottom:8px;">'
            f'Indicators reported per country in the National Energy Compacts</div>',
            unsafe_allow_html=True,
        )
        nc_col = _nc()
        gap_df = long_df.groupby(["iso3","category"])["has_data"].sum().reset_index()
        gap_tot = long_df.groupby(["iso3","category"])["has_data"].count().reset_index(name="total")
        gap_df = gap_df.merge(gap_tot, on=["iso3","category"])
        gap_df["pct"] = (gap_df["has_data"] / gap_df["total"] * 100).round(1)
        gap_df = gap_df.merge(countries_df[["iso3",nc_col]], on="iso3", how="left")
        pivot = gap_df.pivot_table(index=nc_col, columns="category", values="pct", aggfunc="first")
        pivot = pivot.sort_index()

        import plotly.graph_objects as go
        fig_gaps = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[c[:18] for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0,"#F5F7FA"],[0.5,TEAL],[1,NAVY]],
            text=[[f"{v:.0f}%" if not np.isnan(v) else "—" for v in row]
                  for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=8.5),
            hoverongaps=False,
            colorbar=dict(title="% reported", tickfont=dict(size=9), len=0.7, thickness=9),
            zmin=0, zmax=100,
        ))
        fig_gaps.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
            margin=dict(l=0, r=0, t=4, b=0),
            height=max(400, len(pivot)*26 + 60),
            xaxis=dict(tickfont=dict(size=8.5), side="top", tickangle=-25),
            yaxis=dict(tickfont=dict(size=9), autorange="reversed"),
        )
        st.plotly_chart(fig_gaps, use_container_width=True,
                        config={"displayModeBar": False}, key="gaps_chart")


# ══════════════════════════════════════
# RIGHT — Country profile
# ══════════════════════════════════════
with right_col:
    st.markdown('<div class="panel-title">Country Profile</div>', unsafe_allow_html=True)
    iso3 = st.session_state.selected_iso3

    if not iso3:
        st.markdown(
            '<div class="no-data-ph">Click a country<br>on the map.</div>',
            unsafe_allow_html=True,
        )
    else:
        c_row  = countries_df[countries_df["iso3"]==iso3]
        cname  = c_row[_nc()].values[0] if len(c_row) else iso3
        n_ind  = c_row["n_indicators"].values[0] if len(c_row) else 0
        d_date = c_row["data_date"].values[0] if ("data_date" in c_row.columns and len(c_row)) else "—"

        km_row = key_metrics[key_metrics["iso3"]==iso3]
        km     = km_row.iloc[0] if not km_row.empty else pd.Series(dtype=float)

        def _g(field):
            try: return float(km[field])
            except: return np.nan

        elec_c = _g("elec_access_cur"); elec_t = _g("elec_access_tgt")
        ren_c  = _g("renew_share_cur"); ren_t  = _g("renew_share_tgt")
        ren_cc = _g("renew_cap_cur");   ren_ct = _g("renew_cap_tgt")
        cook_c = _g("cooking_cur");     cook_t = _g("cooking_tgt")
        p_inv  = _g("private_invest_usd")
        comp   = _g("data_completeness")

        # Country header (no assessment badge)
        st.markdown(
            f'<div class="country-header">'
            f'<div class="country-name">{cname}</div>'
            f'<div class="country-meta">{n_ind} indicators · Compact: {d_date}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Radar chart ───────────────────────────────────────────────────────
        if not km.empty:
            fig_radar = build_radar_chart(km.to_dict(), cname, lang)
            st.plotly_chart(fig_radar, use_container_width=True,
                            config={"displayModeBar": False}, key="radar")

        def _kpi_block(title, cur_val, cur_sfx, tgt_val, tgt_sfx, show_bar=True):
            ratio = None
            if cur_val is not None and tgt_val is not None and tgt_val > 0:
                ratio = min(100, round(cur_val / tgt_val * 100))
            bar_html = ""
            if show_bar and ratio is not None:
                bar_html = (
                    f'<div class="prog-bar-wrap">'
                    f'<div class="prog-bar-label">'
                    f'<span>Current vs. 2030</span><span>{ratio}%</span></div>'
                    + _bar(ratio)
                    + '</div>'
                )
            cv = _f(cur_val, sfx=cur_sfx) if cur_val is not None else "—"
            tv = _f(tgt_val, sfx=tgt_sfx) if tgt_val is not None else "—"
            return (
                f'<div class="kpi-block">'
                f'<div class="kpi-block-title">{title}</div>'
                f'<div class="kpi-block-row">'
                f'<div class="kpi-block-item">'
                f'<div class="kpi-num-cur">{cv}</div>'
                f'<div class="kpi-sub kpi-sub-cur">Current</div></div>'
                f'<div class="kpi-block-item">'
                f'<div class="kpi-num-tgt">{tv}</div>'
                f'<div class="kpi-sub kpi-sub-tgt">2030 Target</div></div></div>'
                + bar_html + '</div>'
            )

        # KPI 1 — Electricity Access
        if not (np.isnan(elec_c) and np.isnan(elec_t)):
            st.markdown(_kpi_block(
                "Electricity Access",
                elec_c if not np.isnan(elec_c) else None, "%",
                elec_t if not np.isnan(elec_t) else None, "%",
            ), unsafe_allow_html=True)

        # KPI 2 — Renewable Energy
        use_share = not (np.isnan(ren_c) and np.isnan(ren_t))
        if use_share:
            st.markdown(_kpi_block(
                "Renewable Share",
                ren_c if not np.isnan(ren_c) else None, "%",
                ren_t if not np.isnan(ren_t) else None, "%",
            ), unsafe_allow_html=True)
        elif not (np.isnan(ren_cc) and np.isnan(ren_ct)):
            st.markdown(_kpi_block(
                "Renewable Capacity",
                ren_cc if not np.isnan(ren_cc) else None, "MW",
                ren_ct if not np.isnan(ren_ct) else None, "MW",
            ), unsafe_allow_html=True)

        # KPI 3 — Clean Cooking
        if not (np.isnan(cook_c) and np.isnan(cook_t)):
            st.markdown(_kpi_block(
                "Clean Cooking Access",
                cook_c if not np.isnan(cook_c) else None, "%",
                cook_t if not np.isnan(cook_t) else None, "%",
            ), unsafe_allow_html=True)

        # KPI 4 — Private Investment (target only — no current baseline in Compacts)
        if not np.isnan(p_inv):
            inv_str = (f"${p_inv/1e9:.2f}B" if p_inv >= 1e9 else
                       f"${p_inv/1e6:.1f}M"  if p_inv >= 1e6 else
                       f"${p_inv:,.0f}")
            # Show as % of a reference (total programme for scale)
            inv_pct = min(100, round(p_inv / inv_tot * 100, 1)) if not np.isnan(inv_tot) and inv_tot > 0 else None
            bar_html = ""
            if inv_pct is not None:
                bar_html = (
                    f'<div class="prog-bar-wrap">'
                    f'<div class="prog-bar-label">'
                    f'<span>Share of M300 total</span><span>{inv_pct:.1f}%</span></div>'
                    + _bar(inv_pct)
                    + '</div>'
                )
            st.markdown(
                f'<div class="kpi-block">'
                f'<div class="kpi-block-title">Private Investment Required</div>'
                f'<div class="kpi-num-invest">{inv_str}</div>'
                f'<div class="kpi-sub kpi-sub-tgt">USD — 2030 Target</div>'
                + bar_html + '</div>',
                unsafe_allow_html=True,
            )

        # Data completeness
        st.markdown('<hr class="section-sep"/>', unsafe_allow_html=True)
        comp_v = max(0, comp if not np.isnan(comp) else 0)
        st.markdown(
            f'<div style="font-size:0.58rem;text-transform:uppercase;letter-spacing:.07em;'
            f'color:#9AA5B0;margin-bottom:4px;">Data completeness</div>'
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<div class="cov-bar-bg" style="flex:1;">'
            f'<div class="cov-bar-fill" style="width:{comp_v:.0f}%;"></div></div>'
            f'<span style="font-size:0.75rem;font-weight:700;color:{TEAL};">{comp_v:.0f}%</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # View all indicators
        n_avail = int(
            long_df[(long_df["iso3"]==iso3) & (long_df["has_data"]==True)]["indicator"].nunique()
        )
        st.markdown("")
        if st.button(f"View all indicators ({n_avail})", use_container_width=True, key="open_modal"):
            show_indicators_modal(iso3)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="method-note" style="margin-top:12px;">'
    f'<div class="method-note-title">Data note</div>'
    f'{nav.get("disclaimer","")}'
    f'</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="footer">'
    f'<div class="footer-text">Sources: M300 National Energy Compacts · SEforALL</div>'
    f'<div class="footer-text">Last updated: {date_str}</div>'
    f'</div>',
    unsafe_allow_html=True,
)
