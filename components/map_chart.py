"""
Map & chart components — v4
SEforALL palette: Teal #00A19A (current) · Orange #F7941D (target) · Navy #1B3A5C
No trajectory chart. Map is full-width. Radar + multi-type comparison added.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from data.config import ISLAND_MARKERS, TARGET_YEAR, CURRENT_YEAR

# ── SEforALL palette ──────────────────────────────────────────────────────────
TEAL   = "#00A19A"   # current values
ORANGE = "#F7941D"   # 2030 targets
NAVY   = "#1B3A5C"   # headers / accents
TEAL_L = "#E8F7F7"   # light teal bg
ORG_L  = "#FEF4E6"   # light orange bg
GREY_D = "#C2CDD6"   # M300 no-data
GREY_L = "#E8E0D0"   # non-M300 countries

OCEAN_C  = "#EBF3FA"
LAND_C   = "#F2EEE9"
BORDER_C = "#C5CDD6"

# ── M300 countries ────────────────────────────────────────────────────────────
M300_ISO3 = {
    "BDI","BEN","BWA","CIV","CMR","COD","COG","COM","ETH","GHA",
    "GIN","GMB","KEN","LBR","LSO","MDG","MOZ","MRT","MWI","NAM",
    "NER","NGA","SEN","SLE","STP","TCD","TGO","TZA","ZMB","ZWE",
}
ALL_AFRICA_ISO3 = [
    "DZA","AGO","BEN","BWA","BFA","BDI","CPV","CMR","CAF","TCD","COM","COD","COG",
    "CIV","DJI","EGY","GNQ","ERI","SWZ","ETH","GAB","GMB","GHA","GIN","GNB","KEN",
    "LSO","LBR","LBY","MDG","MWI","MLI","MRT","MUS","MAR","MOZ","NAM","NER","NGA",
    "RWA","STP","SEN","SYC","SLE","SOM","ZAF","SSD","SDN","TZA","TGO","TUN","UGA",
    "ZMB","ZWE",
]
NON_M300_ISO3 = [c for c in ALL_AFRICA_ISO3 if c not in M300_ISO3]

# ── Colour scales (SEforALL-inspired) ────────────────────────────────────────
SCALES = {
    "access":       [[0,"#E0F7F7"],[0.35,"#66C5C2"],[0.7,"#00A19A"],[1,"#006B66"]],
    "renewable":    [[0,"#E8F8F7"],[0.35,"#5CC0BC"],[0.7,"#009B94"],[1,"#005C58"]],
    "cooking":      [[0,"#FEF4E6"],[0.35,"#FBBB6A"],[0.7,"#F7941D"],[1,"#C16B00"]],
    "investment":   [[0,"#EDF2F8"],[0.35,"#7BA8C9"],[0.7,"#2E6FA3"],[1,"#1B3A5C"]],
    "capacity":     [[0,"#EDF2F8"],[0.4,"#90B8D4"],[0.8,"#1B3A5C"],[1,"#0D1E2E"]],
    "progress":     [[0,"#FEF4E6"],[0.4,"#F7C27A"],[0.7,"#F7941D"],[1,"#1B3A5C"]],
    "gap":          [[0,"#E0F7F7"],[0.35,"#F7C27A"],[0.7,"#F7941D"],[1,"#B71C1C"]],
    "default":      [[0,"#EDF2F8"],[0.5,"#7BA8C9"],[1,"#1B3A5C"]],
}

LINE_PALETTE = [
    TEAL, ORANGE, NAVY, "#E8643C", "#1E8C6E",
    "#7B4FBF", "#C9A227", "#3D7EBF", "#C0392B", "#27AE60",
    "#8E44AD", "#D35400", "#1A5276", "#196F3D", "#7D6608",
]


def _infer_scale(indicator: str) -> str:
    n = indicator.lower()
    if "access" in n and "cooking" not in n: return "access"
    if "cooking" in n:   return "cooking"
    if "renew" in n:     return "renewable"
    if "invest" in n or "financ" in n: return "investment"
    if "capacity" in n or "generat" in n: return "capacity"
    if "progress" in n:  return "progress"
    if "gap" in n:       return "gap"
    return "default"


def _lerp_cs(cs, norm):
    norm = max(0.0, min(1.0, norm))
    for i in range(len(cs) - 1):
        t0, c0 = cs[i]; t1, c1 = cs[i + 1]
        if t0 <= norm <= t1:
            f = (norm - t0) / (t1 - t0) if t1 > t0 else 0.0
            def h2r(h):
                h = h.lstrip("#")
                return tuple(int(h[j:j+2], 16) for j in (0, 2, 4))
            r0,g0,b0 = h2r(c0); r1,g1,b1 = h2r(c1)
            return "#{:02x}{:02x}{:02x}".format(
                int(r0+f*(r1-r0)), int(g0+f*(g1-g0)), int(b0+f*(b1-b0)))
    return cs[-1][1]


# ═══════════════════════════════════════════════════════
# CHOROPLETH MAP
# ═══════════════════════════════════════════════════════
def build_choropleth(data_df, indicator_label, unit="", lang="en",
                     selected_iso3=None, colorscale_name=None):
    df = data_df.copy()
    df["_v"] = pd.to_numeric(df.get("value"), errors="coerce")
    nc = "country_name_en" if lang == "en" else "country_name_fr"
    if nc not in df.columns:
        nc = next((c for c in ["country_name_en","country_name_fr"] if c in df.columns), df.columns[0])

    has_d = df[df["_v"].notna() & df["iso3"].isin(M300_ISO3)].copy()
    no_d  = df[df["_v"].isna()  & df["iso3"].isin(M300_ISO3)].copy()
    cs    = colorscale_name or _infer_scale(indicator_label)

    fig = go.Figure()

    # Non-M300 layer (beige)
    fig.add_trace(go.Choropleth(
        name="Not in Mission 300",
        locations=NON_M300_ISO3, z=[0]*len(NON_M300_ISO3),
        colorscale=[[0, GREY_L],[1, GREY_L]],
        autocolorscale=False, showscale=False,
        marker_line_color=BORDER_C, marker_line_width=0.5,
        hovertemplate="<b>%{location}</b><br><i>Not in Mission 300 programme</i><extra></extra>",
        zmin=0, zmax=1,
    ))

    # M300 with data
    if not has_d.empty:
        fig.add_trace(go.Choropleth(
            name=indicator_label,
            locations=has_d["iso3"], z=has_d["_v"],
            customdata=has_d[[nc]].values,
            hovertemplate=(f"<b>%{{customdata[0]}}</b><br>"
                           f"{indicator_label}: <b>%{{z:.1f}} {unit}</b><extra></extra>"),
            colorscale=SCALES.get(cs, SCALES["default"]),
            autocolorscale=False,
            zmin=has_d["_v"].min(), zmax=has_d["_v"].max(),
            marker_line_color=BORDER_C, marker_line_width=0.6,
            colorbar=dict(
                title=dict(text=unit, font=dict(size=9, color="#6B7A8D")),
                tickfont=dict(size=8.5, color="#6B7A8D"),
                bgcolor="rgba(255,255,255,0.92)",
                bordercolor="#DDE2E8", borderwidth=1,
                len=0.42, thickness=9, x=1.01,
            ),
        ))

    # M300 without data (grey)
    if not no_d.empty:
        cn = no_d[[nc]].values if nc in no_d.columns else no_d[["iso3"]].values
        fig.add_trace(go.Choropleth(
            name="In M300 — data not reported",
            locations=no_d["iso3"], z=[0]*len(no_d),
            customdata=cn,
            hovertemplate="<b>%{customdata[0]}</b><br><i>In M300 — data not reported</i><extra></extra>",
            colorscale=[[0, GREY_D],[1, GREY_D]],
            autocolorscale=False, showscale=False,
            marker_line_color=BORDER_C, marker_line_width=0.6,
            zmin=0, zmax=1,
        ))

    # Selected border
    if selected_iso3:
        fig.add_trace(go.Choropleth(
            name="_sel", locations=[selected_iso3], z=[1],
            colorscale=[[0,"rgba(0,0,0,0)"],[1,"rgba(0,0,0,0)"]],
            showscale=False,
            marker_line_color=ORANGE, marker_line_width=2.8,
            hoverinfo="skip", zmin=0, zmax=1,
        ))

    # Island markers
    _add_island_markers(fig, df, lang, selected_iso3,
                        SCALES.get(cs, SCALES["default"]), unit, indicator_label)

    # Legend entries
    if not no_d.empty:
        fig.add_trace(go.Scattergeo(
            name="In M300 — data not reported", lat=[None], lon=[None],
            mode="markers",
            marker=dict(size=11, color=GREY_D, symbol="square",
                        line=dict(width=1, color="#9E9E9E")),
            showlegend=True,
        ))
    fig.add_trace(go.Scattergeo(
        name="Not in Mission 300", lat=[None], lon=[None],
        mode="markers",
        marker=dict(size=11, color=GREY_L, symbol="square",
                    line=dict(width=1, color="#B0A898")),
        showlegend=True,
    ))

    fig.update_geos(
        scope="africa", showframe=False,
        showcoastlines=True, coastlinecolor="#A8B4C0", coastlinewidth=0.7,
        showland=True, landcolor=LAND_C,
        showocean=True, oceancolor=OCEAN_C,
        showlakes=True, lakecolor=OCEAN_C,
        showcountries=True, countrycolor=BORDER_C, countrywidth=0.5,
        bgcolor="#FAFAFA",
        projection_type="natural earth",
        lataxis_range=[-37, 38], lonaxis_range=[-20, 55],
    )
    fig.update_layout(
        paper_bgcolor="#FAFAFA", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=0, t=0, b=0),
        height=540, dragmode=False,
        legend=dict(
            x=0.01, y=0.04,
            bgcolor="rgba(255,255,255,0.94)",
            bordercolor="#DDE2E8", borderwidth=1,
            font=dict(size=7.5, color="#6B7A8D"),
            tracegroupgap=1,
        ),
    )
    return fig


def _add_island_markers(fig, data_df, lang, selected_iso3, colorscale, unit, label):
    val_map = {}
    if "value" in data_df.columns:
        val_map = data_df.dropna(subset=["value"]).set_index("iso3")["value"].to_dict()
    vals = pd.to_numeric(data_df.get("value", pd.Series()), errors="coerce")
    vmin, vmax = vals.min(), vals.max()
    vrange = (vmax - vmin) if (pd.notna(vmax) and pd.notna(vmin) and vmax > vmin) else 1
    nc = f"name_{lang}"

    for iso3, info in ISLAND_MARKERS.items():
        val   = val_map.get(iso3, np.nan)
        name  = info.get(nc, info.get("name_en", iso3))
        is_sel = (iso3 == selected_iso3)

        if pd.notna(val) and not (isinstance(val, float) and np.isnan(val)):
            norm   = max(0.0, min(1.0, (float(val) - vmin) / vrange))
            mcolor = _lerp_cs(colorscale, norm)
            htxt   = f"<b>{name}</b><br>{label}: <b>{float(val):.1f} {unit}</b><br><i>Click for profile</i>"
        else:
            mcolor = GREY_D
            htxt   = f"<b>{name}</b><br><i>In M300 — data not reported</i><br><i>Click for profile</i>"

        fig.add_trace(go.Scattergeo(
            lat=[info["lat"]], lon=[info["lon"]],
            customdata=[[iso3, name]],
            mode="markers+text",
            text=[name], textposition="top center",
            textfont=dict(size=8, color="#3A4A5A"),
            marker=dict(
                size=20 if is_sel else 13, color=mcolor, symbol="circle",
                line=dict(width=2.8 if is_sel else 1.5,
                          color=ORANGE if is_sel else "#6B7A8D"),
            ),
            hovertemplate=htxt + "<extra></extra>",
            showlegend=False, name=f"island_{iso3}",
        ))


def build_completeness_map(countries_df, long_df, lang="en"):
    comp = long_df.groupby("iso3").apply(
        lambda g: round(g["has_data"].sum() / len(g) * 100, 1)
    ).reset_index(name="value")
    comp = comp.merge(countries_df[["iso3","country_name_en","country_name_fr"]], on="iso3", how="left")
    return build_choropleth(comp, "Data Completeness (%)", "%", lang, colorscale_name="default")


# ═══════════════════════════════════════════════════════
# RADAR CHART — country profile
# ═══════════════════════════════════════════════════════
def build_radar_chart(km_row: dict, country_name: str, lang: str = "en") -> go.Figure:
    """
    Radar with 4 axes, each normalised 0-100 against regional max or absolute max.
    Two traces: Current (teal filled) + 2030 Target (orange dashed).
    """
    def _gv(k):
        v = km_row.get(k, np.nan)
        return float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else None

    elec_c = _gv("elec_access_cur");  elec_t = _gv("elec_access_tgt")
    ren_c  = _gv("renew_share_cur");  ren_t  = _gv("renew_share_tgt")
    cook_c = _gv("cooking_cur");      cook_t = _gv("cooking_tgt")
    inv_t  = _gv("private_invest_usd")

    # Labels
    labels = ["Electricity\nAccess", "Renewable\nShare", "Clean\nCooking", "Investment\n(normalised)"]
    cats   = labels + [labels[0]]  # close polygon

    # Normalise each axis to 0-100
    # Electricity, renewable share, cooking: already 0-100%
    # Investment: normalise to max $10B (cap at 100)
    INV_MAX = 10e9

    def _norm_inv(v):
        return min(100, round(v / INV_MAX * 100, 1)) if v is not None else None

    cur_vals = [elec_c, ren_c, cook_c, _norm_inv(inv_t)]
    tgt_vals = [elec_t, ren_t, cook_t, _norm_inv(inv_t)]   # investment: same (target only)

    # Replace None with 0 for the chart
    cur_clean = [v if v is not None else 0 for v in cur_vals]
    tgt_clean = [v if v is not None else 0 for v in tgt_vals]

    # Close polygon
    cur_r = cur_clean + [cur_clean[0]]
    tgt_r = tgt_clean + [tgt_clean[0]]

    fig = go.Figure()

    # Target trace (orange, dashed, behind)
    if any(v > 0 for v in tgt_clean):
        fig.add_trace(go.Scatterpolar(
            r=tgt_r, theta=cats,
            fill="toself", fillcolor=f"rgba(247,148,29,0.10)",
            line=dict(color=ORANGE, width=2, dash="dash"),
            name="2030 Target", mode="lines",
        ))

    # Current trace (teal, solid, front)
    if any(v > 0 for v in cur_clean):
        fig.add_trace(go.Scatterpolar(
            r=cur_r, theta=cats,
            fill="toself", fillcolor=f"rgba(0,161,154,0.18)",
            line=dict(color=TEAL, width=2.5),
            name="Current", mode="lines+markers",
            marker=dict(size=5, color=TEAL),
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=8, color="#6B7A8D"),
                gridcolor="#DDE2E8", linecolor="#DDE2E8",
                ticksuffix="%",
            ),
            angularaxis=dict(
                tickfont=dict(size=8.5, color="#1B2E3C"),
                linecolor="#DDE2E8",
            ),
            bgcolor="#FAFAFA",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", x=0.5, xanchor="center", y=-0.08,
            font=dict(size=9, color="#1B2E3C"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=20, r=20, t=20, b=30),
        height=240,
        showlegend=True,
    )
    return fig


# ═══════════════════════════════════════════════════════
# COMPARISON CHARTS
# ═══════════════════════════════════════════════════════

# The 4 Key Indicators used for all comparison views
KPI_DEFS = [
    ("Electricity Access",  "elec_access_cur",  "elec_access_tgt",  "%"),
    ("Renewable Share",     "renew_share_cur",  "renew_share_tgt",  "%"),
    ("Clean Cooking",       "cooking_cur",      "cooking_tgt",      "%"),
    ("Private Investment",  "private_invest_usd", None,             "USD"),
]


def _get_comparison_data(key_metrics, iso3_list, nc_map):
    """Build a wide DataFrame for comparison charts."""
    rows = []
    for iso3 in iso3_list:
        km = key_metrics[key_metrics["iso3"] == iso3]
        if km.empty: continue
        km = km.iloc[0]
        def _gv(f):
            try: return float(km[f])
            except: return np.nan
        rows.append({
            "iso3":    iso3,
            "country": nc_map.get(iso3, iso3),
            "elec_cur":   _gv("elec_access_cur"),
            "elec_tgt":   _gv("elec_access_tgt"),
            "ren_cur":    _gv("renew_share_cur"),
            "ren_tgt":    _gv("renew_share_tgt"),
            "cook_cur":   _gv("cooking_cur"),
            "cook_tgt":   _gv("cooking_tgt"),
            "inv":        _gv("private_invest_usd"),
        })
    return pd.DataFrame(rows)


def build_comparison_grouped_bar(df):
    """Grouped bar: current vs target for each of 4 KPIs, one group per country."""
    if df.empty:
        return go.Figure()

    kpis = [
        ("Electricity Access (%)",  "elec_cur", "elec_tgt"),
        ("Renewable Share (%)",     "ren_cur",  "ren_tgt"),
        ("Clean Cooking (%)",       "cook_cur", "cook_tgt"),
    ]
    fig = go.Figure()
    countries = df["country"].tolist()

    for label, cur_col, tgt_col in kpis:
        fig.add_trace(go.Bar(
            name=f"{label} — Current",
            x=countries, y=df[cur_col],
            marker_color=TEAL, marker_opacity=0.9,
            legendgroup=cur_col,
            hovertemplate=f"<b>%{{x}}</b><br>{label} current: <b>%{{y:.1f}}%</b><extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name=f"{label} — 2030",
            x=countries, y=df[tgt_col],
            marker_color=ORANGE, marker_opacity=0.55,
            marker_line_color=ORANGE, marker_line_width=1.2,
            legendgroup=tgt_col,
            hovertemplate=f"<b>%{{x}}</b><br>{label} 2030: <b>%{{y:.1f}}%</b><extra></extra>",
        ))

    fig.update_layout(
        barmode="group", bargap=0.18, bargroupgap=0.04,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=0, t=8, b=0), height=380,
        xaxis=dict(tickfont=dict(size=10), showgrid=False),
        yaxis=dict(title="%", showgrid=True, gridcolor="#EEF0F3", tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.06, font=dict(size=9),
                    bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    return fig


def build_comparison_radar(df, lang="en"):
    """Radar / spider chart: one polygon per country, 4 normalised axes."""
    if df.empty or len(df) < 2:
        return go.Figure()

    axes_labels = ["Electricity<br>Access", "Renewable<br>Share",
                   "Clean<br>Cooking", "Investment<br>(norm.)"]
    axes = axes_labels + [axes_labels[0]]
    INV_MAX = df["inv"].max() if df["inv"].notna().any() else 10e9
    if pd.isna(INV_MAX) or INV_MAX == 0: INV_MAX = 10e9

    fig = go.Figure()
    for i, row in df.iterrows():
        inv_norm = min(100, float(row["inv"]) / INV_MAX * 100) if pd.notna(row["inv"]) else 0
        cur_vals = [
            row["elec_cur"] if pd.notna(row["elec_cur"]) else 0,
            row["ren_cur"]  if pd.notna(row["ren_cur"])  else 0,
            row["cook_cur"] if pd.notna(row["cook_cur"]) else 0,
            inv_norm,
        ]
        r_vals = cur_vals + [cur_vals[0]]
        color = LINE_PALETTE[i % len(LINE_PALETTE)]
        fig.add_trace(go.Scatterpolar(
            r=r_vals, theta=axes,
            fill="toself", fillcolor=f"rgba(0,0,0,0.03)",
            line=dict(color=color, width=2),
            name=row["country"],
            mode="lines+markers",
            marker=dict(size=5, color=color),
            hovertemplate=(f"<b>{row['country']}</b><br>"
                           f"Elec: <b>%{{r:.1f}}</b><extra></extra>"),
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(size=8, color="#6B7A8D"),
                            gridcolor="#DDE2E8", linecolor="#DDE2E8",
                            ticksuffix="%"),
            angularaxis=dict(tickfont=dict(size=9, color="#1B2E3C"),
                             linecolor="#DDE2E8"),
            bgcolor="#FAFAFA",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="v", x=1.05, y=0.95,
                    font=dict(size=8.5, color="#1B2E3C"),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="#DDE2E8", borderwidth=1),
        margin=dict(l=20, r=120, t=20, b=20),
        height=420,
    )
    return fig


def build_comparison_lollipop(df):
    """Dot/lollipop chart: sorted by electricity access for quick ranking."""
    if df.empty:
        return go.Figure()

    d = df.dropna(subset=["elec_cur"]).sort_values("elec_cur", ascending=True)
    fig = go.Figure()

    # Horizontal lines (stems)
    for _, row in d.iterrows():
        fig.add_shape(
            type="line",
            x0=0, x1=row["elec_tgt"] if pd.notna(row["elec_tgt"]) else row["elec_cur"],
            y0=row["country"], y1=row["country"],
            line=dict(color="#DDE2E8", width=1.5),
        )

    # Current (teal dots)
    fig.add_trace(go.Scatter(
        x=d["elec_cur"], y=d["country"],
        mode="markers",
        name="Current",
        marker=dict(size=10, color=TEAL, line=dict(width=1.5, color="white")),
        hovertemplate="<b>%{y}</b><br>Current: <b>%{x:.1f}%</b><extra></extra>",
    ))

    # Target (orange diamonds)
    fig.add_trace(go.Scatter(
        x=d["elec_tgt"], y=d["country"],
        mode="markers",
        name="2030 Target",
        marker=dict(size=10, color=ORANGE, symbol="diamond",
                    line=dict(width=1.5, color="white")),
        hovertemplate="<b>%{y}</b><br>2030 Target: <b>%{x:.1f}%</b><extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=0, t=8, b=0),
        height=max(350, len(d) * 26),
        xaxis=dict(title="Electricity Access (%)", range=[0, 105],
                   showgrid=True, gridcolor="#EEF0F3", tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.04, font=dict(size=10)),
        hovermode="y unified",
    )
    return fig


def build_comparison_heatmap(df):
    """Heatmap: countries × 4 KPIs (current values, normalised 0-100)."""
    if df.empty:
        return go.Figure()

    d = df.copy()
    INV_MAX = d["inv"].max() if d["inv"].notna().any() else 10e9
    if pd.isna(INV_MAX) or INV_MAX == 0: INV_MAX = 10e9

    d["inv_n"] = d["inv"].apply(lambda v: min(100, v/INV_MAX*100) if pd.notna(v) else np.nan)
    cols = ["elec_cur","ren_cur","cook_cur","inv_n"]
    labels = ["Electricity\nAccess %","Renewable\nShare %","Clean\nCooking %","Investment\n(norm.)"]

    matrix   = d[cols].values
    countries = d["country"].tolist()

    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=labels, y=countries,
        colorscale=[[0,TEAL_L],[0.5,TEAL],[1,NAVY]],
        text=[[f"{v:.1f}" if pd.notna(v) else "—" for v in row] for row in matrix],
        texttemplate="%{text}",
        textfont=dict(size=10, color="white"),
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> — %{x}<br>Value: <b>%{z:.1f}</b><extra></extra>",
        colorbar=dict(
            title="Value (0-100)", tickfont=dict(size=9),
            len=0.8, thickness=10,
        ),
        zmin=0, zmax=100,
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=0, t=8, b=0),
        height=max(280, len(countries) * 28),
        xaxis=dict(tickfont=dict(size=10), side="top"),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    return fig


# ═══════════════════════════════════════════════════════
# CATEGORY BAR (existing — keeps working)
# ═══════════════════════════════════════════════════════
def build_category_bar(long_df, iso3, category, lang="en"):
    df = long_df[(long_df["iso3"]==iso3) & (long_df["category"]==category)].copy()
    cur = df[df["ind_type"]=="current"].set_index("indicator")["value"]
    tgt = df[df["ind_type"]=="target"].set_index("indicator")["value"]
    all_i = sorted(set(cur.index.tolist() + tgt.index.tolist()))

    rows = []
    for ind in all_i:
        c = cur.get(ind, np.nan); t_ = tgt.get(ind, np.nan)
        if not (np.isnan(c) and np.isnan(t_)):
            short = (ind.replace("– Current","").replace("- Current","")
                        .replace("– 2030 Target","").replace("- 2030","").strip())
            rows.append({"ind": short, "c": c, "t": t_})

    if not rows:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text="No data available", x=0.5, y=0.5,
                              showarrow=False, font=dict(color="#A8B4C0"))],
            height=160,
        )
        return fig

    d = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Current", y=d["ind"], x=d["c"], orientation="h",
        marker_color=TEAL,
        text=d["c"].apply(lambda v: f"{v:,.1f}" if pd.notna(v) else "—"),
        textposition="outside", textfont=dict(size=9),
    ))
    fig.add_trace(go.Bar(
        name="2030 Target", y=d["ind"], x=d["t"], orientation="h",
        marker_color=ORANGE, marker_opacity=0.6,
        marker_line_color=ORANGE, marker_line_width=1.2,
        text=d["t"].apply(lambda v: f"{v:,.1f}" if pd.notna(v) else "—"),
        textposition="outside", textfont=dict(size=9),
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=80, t=4, b=0),
        height=max(180, len(d)*48),
        xaxis=dict(showgrid=True, gridcolor="#EEF0F3", zeroline=False, tickfont=dict(size=9)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=9)),
        legend=dict(orientation="h", y=1.04, font=dict(size=10)),
    )
    return fig


# ═══════════════════════════════════════════════════════
# RANKINGS CHART
# ═══════════════════════════════════════════════════════
def build_rankings_chart(key_metrics, countries_df, kpi_col, kpi_label, unit,
                         lang="en", top_n=5):
    """Horizontal bar ranking (top + bottom countries for a given KPI)."""
    nc = "country_name_en" if lang == "en" else "country_name_fr"
    df = key_metrics[["iso3", kpi_col]].copy()
    df = df.merge(countries_df[["iso3", nc]], on="iso3", how="left")
    df = df.dropna(subset=[kpi_col]).sort_values(kpi_col, ascending=False).reset_index(drop=True)
    if df.empty:
        return go.Figure()

    top = df.head(top_n)
    bot = df.tail(top_n).sort_values(kpi_col, ascending=True)
    combined = pd.concat([top.assign(_grp="Top"), bot.assign(_grp="Bottom")]).drop_duplicates("iso3")
    combined = combined.sort_values(kpi_col, ascending=True)

    colors = [TEAL if g == "Top" else "#A8B4C0" for g in combined["_grp"]]
    fig = go.Figure(go.Bar(
        x=combined[kpi_col], y=combined[nc],
        orientation="h",
        marker_color=colors,
        text=combined[kpi_col].apply(lambda v: f"{v:.1f} {unit}"),
        textposition="outside", textfont=dict(size=9.5),
        hovertemplate="<b>%{y}</b>: <b>%{x:.1f} " + unit + "</b><extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=80, t=36, b=0),
        height=max(240, len(combined)*26),
        xaxis=dict(title=unit, showgrid=True, gridcolor="#EEF0F3",
                   tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, tickfont=dict(size=9.5)),
        title=dict(text=f"<b>{kpi_label}</b>",
           font=dict(size=11, color="#1B2E3C"), x=0,
           pad=dict(l=0, t=12)),
    )
    return fig


# ═══════════════════════════════════════════════════════
# SCORECARD TABLE CHART
# ═══════════════════════════════════════════════════════
def build_scorecard_chart(key_metrics, countries_df, lang="en"):
    """All countries × 4 KPIs — colour-coded heatmap-style table."""
    nc = "country_name_en" if lang == "en" else "country_name_fr"
    df = key_metrics[["iso3","elec_access_cur","elec_access_tgt",
                       "renew_share_cur","renew_share_tgt",
                       "cooking_cur","cooking_tgt",
                       "private_invest_usd"]].copy()
    df = df.merge(countries_df[["iso3", nc]], on="iso3", how="left")
    df = df.sort_values(nc).reset_index(drop=True)

    cols_cur = ["elec_access_cur","renew_share_cur","cooking_cur"]
    cols_tgt = ["elec_access_tgt","renew_share_tgt","cooking_tgt"]
    col_headers = ["Country",
                   "Electricity\nCurrent", "Electricity\n2030",
                   "Renewable\nCurrent",   "Renewable\n2030",
                   "Cooking\nCurrent",     "Cooking\n2030",
                   "Invest.\nRequired"]

    def _fmt(v, is_inv=False):
        if pd.isna(v): return "—"
        if is_inv:
            if v >= 1e9: return f"${v/1e9:.1f}B"
            if v >= 1e6: return f"${v/1e6:.0f}M"
            return f"${v:,.0f}"
        return f"{v:.1f}%"

    cell_vals = []
    for _, row in df.iterrows():
        cell_vals.append([
            row[nc],
            _fmt(row["elec_access_cur"]), _fmt(row["elec_access_tgt"]),
            _fmt(row["renew_share_cur"]), _fmt(row["renew_share_tgt"]),
            _fmt(row["cooking_cur"]),     _fmt(row["cooking_tgt"]),
            _fmt(row["private_invest_usd"], is_inv=True),
        ])

    # Header colours
    header_colors = [NAVY]*1 + [TEAL, ORANGE]*3 + [NAVY]
    fig = go.Figure(go.Table(
        header=dict(
            values=[f"<b>{h}</b>" for h in col_headers],
            fill_color=header_colors,
            font=dict(color="white", size=9),
            align="center",
            height=34,
            line=dict(color="#FFFFFF", width=1),
        ),
        cells=dict(
            values=list(zip(*cell_vals)),
            fill_color=["#F5F7FA"] + ["white"]*7,
            font=dict(color=["#1B2E3C"]*1 + ["#00A19A","#F7941D"]*3 + ["#1B3A5C"],
                      size=9.5),
            align=["left"] + ["center"]*7,
            height=26,
            line=dict(color="#DDE2E8", width=0.5),
        ),
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=4, b=0),
        height=max(350, len(df) * 28 + 50),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
