"""
Map and chart components — v3
• Island markers (São Tomé, Comores, etc.)
• Gap analysis colorscale
• Mobile-friendly sizing
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data.config import ISLAND_MARKERS

TEAL   = "#00A19A"
ORANGE = "#F7941D"
NAVY   = "#1B3A5C"
TEAL_L = "#E8F7F7"

LINE_PALETTE = [
    "#00A19A", "#F7941D", "#1B3A5C", "#E8643C", "#1E8C6E",
    "#7B4FBF", "#C9A227", "#3D7EBF", "#C0392B", "#27AE60",
]

COLORSCALES = {
    "access":       [[0,"#FFF3CD"],[0.4,"#FFCA28"],[0.7,"#FF8F00"],[1,"#2E7D32"]],
    "capacity":     [[0,"#E3F2FD"],[0.4,"#42A5F5"],[0.7,"#1565C0"],[1,"#0D47A1"]],
    "renewable":    [[0,"#F1F8E9"],[0.4,"#AED581"],[0.7,"#558B2F"],[1,"#1B5E20"]],
    "losses":       [[0,"#E8F5E9"],[0.4,"#FFCC80"],[0.7,"#EF6C00"],[1,"#B71C1C"]],
    "connections":  [[0,"#FFF8E1"],[0.4,"#FFE082"],[0.7,"#FFB300"],[1,"#E65100"]],
    "progress":     [[0,"#FFEBEE"],[0.3,"#FFCA28"],[0.7,"#66BB6A"],[1,"#1B5E20"]],
    "gap":          [[0,"#1B5E20"],[0.4,"#FFCA28"],[0.7,"#EF6C00"],[1,"#B71C1C"]],
    "completeness": [[0,"#FAFAFA"],[0.5,"#90CAF9"],[1,"#1565C0"]],
    "default":      [[0,"#FFF9C4"],[0.5,"#FFB300"],[1,"#E65100"]],
}

NO_DATA_COLOR = "#D9D9D9"
MAP_BG        = "#FAFAFA"
OCEAN_COLOR   = "#EAF4FB"
LAND_COLOR    = "#F5F0E8"
COUNTRY_LINE  = "#BDBDBD"


def _infer_colorscale(indicator: str) -> str:
    n = indicator.lower()
    if "access" in n:            return "access"
    if any(x in n for x in ["renewable","solar","wind","hydro"]): return "renewable"
    if "capacity" in n:          return "capacity"
    if "loss" in n:              return "losses"
    if "connection" in n:        return "connections"
    if "progress" in n:          return "progress"
    if "gap" in n or "écart" in n: return "gap"
    if "completeness" in n:      return "completeness"
    return "default"


def build_choropleth(
    data_df: pd.DataFrame,
    indicator_label: str,
    unit: str,
    lang: str = "fr",
    selected_iso3: str = None,
    colorscale_name: str = None,
    show_no_data_as_grey: bool = True,
    mobile: bool = False,
) -> go.Figure:
    df = data_df.copy()
    df["value_num"] = pd.to_numeric(df.get("value"), errors="coerce")
    name_col = f"country_name_{lang}"
    if name_col not in df.columns:
        name_col = "country_name_en"

    has_data = df[df["value_num"].notna()].copy()
    no_data  = df[df["value_num"].isna()].copy()
    cs_name  = colorscale_name or _infer_colorscale(indicator_label)

    if lang == "fr":
        hover = "<b>%{customdata[0]}</b><br>" + f"{indicator_label} : <b>%{{z:.1f}} {unit}</b><extra></extra>"
        no_data_label = "Données non disponibles"
    else:
        hover = "<b>%{customdata[0]}</b><br>" + f"{indicator_label}: <b>%{{z:.1f}} {unit}</b><extra></extra>"
        no_data_label = "Data not available"

    fig = go.Figure()

    # ── Countries WITH data ───────────────────────────────────────────────────
    if not has_data.empty:
        fig.add_trace(go.Choropleth(
            name=indicator_label,
            locations=has_data["iso3"],
            z=has_data["value_num"],
            customdata=has_data[[name_col]].values,
            hovertemplate=hover,
            colorscale=COLORSCALES.get(cs_name, COLORSCALES["default"]),
            autocolorscale=False,
            zmin=has_data["value_num"].min(),
            zmax=has_data["value_num"].max(),
            marker_line_color=COUNTRY_LINE,
            marker_line_width=0.7,
            colorbar=dict(
                title=dict(text=unit, font=dict(size=10, color="#424242")),
                tickfont=dict(size=9, color="#424242"),
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="#E0E0E0",
                borderwidth=1,
                len=0.45,
                thickness=12,
                x=1.01,
            ),
            showscale=True,
        ))

    # ── Countries WITHOUT data (grey) ─────────────────────────────────────────
    if show_no_data_as_grey and not no_data.empty:
        fig.add_trace(go.Choropleth(
            name=no_data_label,
            locations=no_data["iso3"],
            z=[0] * len(no_data),
            customdata=no_data[[name_col]].values if name_col in no_data.columns else no_data[["iso3"]].values,
            hovertemplate=f"<b>%{{customdata[0]}}</b><br><i>{no_data_label}</i><extra></extra>",
            colorscale=[[0, NO_DATA_COLOR],[1, NO_DATA_COLOR]],
            autocolorscale=False,
            showscale=False,
            marker_line_color=COUNTRY_LINE,
            marker_line_width=0.7,
            zmin=0, zmax=1,
        ))

    # ── Selected country highlight ────────────────────────────────────────────
    if selected_iso3:
        sel = df[df["iso3"] == selected_iso3]
        if not sel.empty:
            fig.add_trace(go.Choropleth(
                name="selected",
                locations=sel["iso3"],
                z=[1],
                colorscale=[[0,"rgba(0,0,0,0)"],[1,"rgba(0,0,0,0)"]],
                showscale=False,
                marker_line_color="#E65100",
                marker_line_width=3,
                hoverinfo="skip",
                zmin=0, zmax=1,
            ))

    # ── Island markers ────────────────────────────────────────────────────────
    _add_island_markers(fig, data_df, lang, selected_iso3, cs_name, unit, indicator_label)

    # ── Legend entry for no-data ──────────────────────────────────────────────
    if show_no_data_as_grey and not no_data.empty:
        fig.add_trace(go.Scattergeo(
            name=no_data_label,
            lat=[None], lon=[None],
            mode="markers",
            marker=dict(size=12, color=NO_DATA_COLOR, symbol="square",
                        line=dict(width=1, color="#9E9E9E")),
            showlegend=True,
        ))

    height = 380 if mobile else 560
    fig.update_geos(
        scope="africa",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#90A4AE",
        coastlinewidth=0.8,
        showland=True,
        landcolor=LAND_COLOR,
        showocean=True,
        oceancolor=OCEAN_COLOR,
        showlakes=True,
        lakecolor=OCEAN_COLOR,
        showcountries=True,
        countrycolor=COUNTRY_LINE,
        countrywidth=0.5,
        bgcolor=MAP_BG,
        projection_type="natural earth",
        lataxis_range=[-37, 38],
        lonaxis_range=[-20, 55],
    )
    fig.update_layout(
        geo=dict(bgcolor=MAP_BG),
        paper_bgcolor=MAP_BG,
        plot_bgcolor=MAP_BG,
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        dragmode=False,
        legend=dict(
            x=0.01, y=0.05,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E0E0E0",
            borderwidth=1,
            font=dict(size=9, color="#424242"),
        ),
    )
    return fig


def _add_island_markers(fig, data_df, lang, selected_iso3, cs_name, unit, indicator_label):
    """Add visible markers for island/micro-state countries."""
    colorscale = COLORSCALES.get(cs_name, COLORSCALES["default"])

    if "value" in data_df.columns:
        val_map = data_df.set_index("iso3")["value"].to_dict()
    else:
        val_map = {}

    vmin = pd.to_numeric(data_df.get("value", pd.Series()), errors="coerce").min()
    vmax = pd.to_numeric(data_df.get("value", pd.Series()), errors="coerce").max()
    vrange = vmax - vmin if (vmax > vmin) else 1

    for iso3, info in ISLAND_MARKERS.items():
        val = val_map.get(iso3, np.nan)
        name = info[f"name_{lang}"]
        is_sel = (iso3 == selected_iso3)

        if pd.notna(val) and not (isinstance(val, float) and np.isnan(val)):
            # Interpolate color from colorscale
            norm = max(0, min(1, (float(val) - vmin) / vrange))
            marker_color = _interpolate_colorscale(colorscale, norm)
            hover_txt = (f"<b>{name}</b><br>{indicator_label} : <b>{float(val):.1f} {unit}</b>"
                         if lang == "fr" else
                         f"<b>{name}</b><br>{indicator_label}: <b>{float(val):.1f} {unit}</b>")
        else:
            marker_color = NO_DATA_COLOR
            nd = "Données non disponibles" if lang == "fr" else "Data not available"
            hover_txt = f"<b>{name}</b><br><i>{nd}</i>"

        fig.add_trace(go.Scattergeo(
            lat=[info["lat"]],
            lon=[info["lon"]],
            mode="markers+text",
            text=[name],
            textposition="top center",
            textfont=dict(size=8, color="#424242"),
            marker=dict(
                size=18 if is_sel else 14,
                color=marker_color,
                symbol="circle",
                line=dict(
                    width=3 if is_sel else 1.5,
                    color="#E65100" if is_sel else "#757575",
                ),
            ),
            hovertemplate=hover_txt + "<extra></extra>",
            showlegend=False,
            name=iso3,
        ))


def _interpolate_colorscale(colorscale: list, norm: float) -> str:
    """Interpolate a hex color from a Plotly colorscale at position norm [0,1]."""
    import re
    norm = max(0.0, min(1.0, norm))
    for i in range(len(colorscale) - 1):
        t0, c0 = colorscale[i]
        t1, c1 = colorscale[i + 1]
        if t0 <= norm <= t1:
            frac = (norm - t0) / (t1 - t0) if (t1 > t0) else 0
            def hex_to_rgb(h):
                h = h.lstrip("#")
                return tuple(int(h[j:j+2], 16) for j in (0, 2, 4))
            r0, g0, b0 = hex_to_rgb(c0)
            r1, g1, b1 = hex_to_rgb(c1)
            r = int(r0 + frac * (r1 - r0))
            g = int(g0 + frac * (g1 - g0))
            b = int(b0 + frac * (b1 - b0))
            return f"#{r:02x}{g:02x}{b:02x}"
    return colorscale[-1][1]


def build_completeness_map(countries_df, long_df, lang="fr", mobile=False):
    comp = long_df.groupby("iso3").apply(
        lambda g: round(g["has_data"].sum() / len(g) * 100, 1)
    ).reset_index(name="value")
    comp = comp.merge(
        countries_df[["iso3", "country_name_en", "country_name_fr"]],
        on="iso3", how="left"
    )
    label = "Complétude des données (%)" if lang == "fr" else "Data Completeness (%)"
    return build_choropleth(
        comp, indicator_label=label, unit="%",
        lang=lang, colorscale_name="completeness",
        show_no_data_as_grey=False, mobile=mobile,
    )


def build_radar_country(metrics, country_name, lang="fr", color="#FF8F00"):
    labels = list(metrics.keys())
    current_pcts, target_vals = [], []
    for lbl, (cur, tgt, unit) in metrics.items():
        if cur is None or (isinstance(cur, float) and np.isnan(cur)):
            current_pcts.append(0)
        elif tgt and tgt > 0:
            current_pcts.append(min(100, round(cur / tgt * 100, 1)))
        else:
            current_pcts.append(0)
        target_vals.append(100)

    lc = labels + [labels[0]]
    cp = current_pcts + [current_pcts[0]]
    tp = target_vals + [target_vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=tp, theta=lc, fill="toself",
        fillcolor="rgba(224,224,224,0.3)",
        line=dict(color="#9E9E9E", dash="dot", width=1.5),
        name="Cible 2030" if lang == "fr" else "2030 Target",
    ))
    fig.add_trace(go.Scatterpolar(
        r=cp, theta=lc, fill="toself",
        fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.25)",
        line=dict(color=color, width=2),
        name="Situation actuelle" if lang == "fr" else "Current situation",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(255,255,255,0.6)",
            radialaxis=dict(visible=True, range=[0,100],
                            tickfont=dict(size=8, color="#757575"),
                            gridcolor="#E0E0E0"),
            angularaxis=dict(tickfont=dict(size=9, color="#424242"), gridcolor="#E0E0E0"),
        ),
        showlegend=True,
        legend=dict(font=dict(size=9), bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#E0E0E0", borderwidth=1,
                    orientation="h", y=-0.12),
        margin=dict(l=30, r=30, t=20, b=40),
        height=280,
    )
    return fig


def build_comparison_bar(
    long_df, countries_list, indicator, unit, lang="fr"
) -> go.Figure:
    """Grouped bar: selected countries × current + target for one indicator."""
    name_col = f"country_name_{lang}"
    current_rows = long_df[
        (long_df["indicator"] == indicator) & (long_df["ind_type"] == "current")
    ].set_index("iso3")
    target_rows = long_df[
        (long_df["indicator"] == indicator) & (long_df["ind_type"] == "target")
    ].set_index("iso3")

    labels, cur_vals, tgt_vals = [], [], []
    for iso3 in countries_list:
        row = long_df[long_df["iso3"] == iso3]
        if row.empty:
            continue
        name = row[name_col].iloc[0] if name_col in row.columns else iso3
        labels.append(name)
        c = current_rows["value"].get(iso3, np.nan)
        t = target_rows["value"].get(iso3, np.nan)
        cur_vals.append(float(c) if pd.notna(c) else None)
        tgt_vals.append(float(t) if pd.notna(t) else None)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Actuel" if lang == "fr" else "Current",
        x=labels, y=cur_vals,
        marker_color="#FF8F00",
        text=[f"{v:.1f} {unit}" if v is not None else "—" for v in cur_vals],
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.add_trace(go.Bar(
        name="Cible 2030" if lang == "fr" else "2030 Target",
        x=labels, y=tgt_vals,
        marker_color="#2E7D32",
        opacity=0.55,
        marker_line_color="#2E7D32",
        marker_line_width=1.5,
        text=[f"{v:.1f} {unit}" if v is not None else "—" for v in tgt_vals],
        textposition="outside",
        textfont=dict(size=10, color="#2E7D32"),
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=380,
        xaxis=dict(tickfont=dict(size=11), showgrid=False),
        yaxis=dict(
            title=unit,
            showgrid=True, gridcolor="#F5F5F5",
            tickfont=dict(size=10),
        ),
        legend=dict(orientation="h", y=1.05, font=dict(size=11)),
        bargap=0.25,
    )
    return fig


def build_evolution_chart(
    evolution_df, countries_list, indicator, lang="fr", show_projection=True
) -> go.Figure:
    """Multi-country line chart over years, with 2030 target dashed line."""
    from data.config import TARGET_YEAR
    name_col = f"country_name_{lang}"
    df = evolution_df[evolution_df["indicator"].str.contains(
        indicator.split("(")[0].strip(), case=False, na=False
    )].copy()

    PALETTE = ["#1565C0","#FF8F00","#2E7D32","#B71C1C","#6A1B9A","#00838F"]

    fig = go.Figure()
    for idx, iso3 in enumerate(countries_list):
        cdf = df[df["iso3"] == iso3].sort_values("year")
        if cdf.empty:
            continue
        name = cdf[name_col].iloc[0] if name_col in cdf.columns else iso3
        color = PALETTE[idx % len(PALETTE)]

        fig.add_trace(go.Scatter(
            x=cdf["year"], y=cdf["value"],
            mode="lines+markers",
            name=name,
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color),
            hovertemplate=f"<b>{name}</b><br>%{{x}} : %{{y:.1f}}<extra></extra>",
        ))

        # Linear projection to 2030
        if show_projection and len(cdf) >= 2:
            x1, y1 = cdf["year"].iloc[-2], cdf["value"].iloc[-2]
            x2, y2 = cdf["year"].iloc[-1], cdf["value"].iloc[-1]
            slope = (y2 - y1) / max(1, x2 - x1)
            proj_y = y2 + slope * (TARGET_YEAR - x2)
            fig.add_trace(go.Scatter(
                x=[x2, TARGET_YEAR],
                y=[y2, proj_y],
                mode="lines",
                name=f"{name} (proj.)" if lang == "en" else f"{name} (proj.)",
                line=dict(color=color, width=1.5, dash="dot"),
                hovertemplate=f"<b>{name}</b> projection<br>%{{x}} : %{{y:.1f}}<extra></extra>",
                showlegend=False,
            ))

    # 2030 target line — horizontal reference
    fig.add_vline(
        x=TARGET_YEAR,
        line=dict(color="#9E9E9E", dash="dash", width=1),
        annotation_text="2030",
        annotation_position="top right",
        annotation_font=dict(size=10, color="#9E9E9E"),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
        margin=dict(l=0, r=0, t=10, b=0),
        height=400,
        xaxis=dict(
            title="Année" if lang == "fr" else "Year",
            tickfont=dict(size=11),
            showgrid=False,
            dtick=1,
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#F5F5F5",
            tickfont=dict(size=10),
        ),
        legend=dict(
            orientation="h", y=-0.18,
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.8)",
        ),
        hovermode="x unified",
    )
    return fig


def build_category_bar(long_df, iso3, category, lang="fr"):
    """Horizontal bar: current vs target for all indicators in a category."""
    df = long_df[(long_df["iso3"] == iso3) & (long_df["category"] == category)].copy()
    current = df[df["ind_type"] == "current"].set_index("indicator")["value"]
    target  = df[df["ind_type"] == "target"].set_index("indicator")["value"]

    all_inds = list(set(current.index.tolist() + target.index.tolist()))
    rows = []
    for ind in all_inds:
        c = current.get(ind, np.nan)
        t_ = target.get(ind, np.nan)
        if not (np.isnan(c) and np.isnan(t_)):
            short = (ind.replace("– Current","").replace("- Current","")
                        .replace("– 2030 Target","").replace(" by 2030","").strip())
            rows.append({"indicator": short, "current": c, "target": t_})

    if not rows:
        return go.Figure().update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text="Aucune donnée" if lang=="fr" else "No data",
                              x=0.5, y=0.5, showarrow=False, font=dict(color="#9E9E9E"))],
        )

    plot_df = pd.DataFrame(rows)
    fig = go.Figure()
    cl = "Actuel" if lang == "fr" else "Current"
    tl = "Cible 2030" if lang == "fr" else "Target 2030"
    fig.add_trace(go.Bar(
        name=cl, y=plot_df["indicator"], x=plot_df["current"],
        orientation="h", marker_color="#FF8F00",
        text=plot_df["current"].apply(lambda v: f"{v:,.0f}" if pd.notna(v) else "—"),
        textposition="outside", textfont=dict(size=9),
    ))
    fig.add_trace(go.Bar(
        name=tl, y=plot_df["indicator"], x=plot_df["target"],
        orientation="h", marker_color="#2E7D32", opacity=0.5,
        marker_line_color="#2E7D32", marker_line_width=1.5,
        text=plot_df["target"].apply(lambda v: f"{v:,.0f}" if pd.notna(v) else "—"),
        textposition="outside", textfont=dict(size=9, color="#2E7D32"),
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=80, t=10, b=0),
        height=max(200, len(plot_df) * 44),
        xaxis=dict(showgrid=True, gridcolor="#F5F5F5", zeroline=False,
                   tickfont=dict(size=9)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=9)),
        legend=dict(orientation="h", y=1.04, font=dict(size=10)),
    )
    return fig


# ═══════════════════════════════════════════════════════
# ADVANCED COMPARISON CHARTS (inspired by provided visuals)
# ═══════════════════════════════════════════════════════

def build_scatter_elec_vs_cooking(key_metrics, countries_df, lang="en"):
    """
    Scatter: Target Electricity Access (x) vs Target Clean Cooking (y).
    One dot per country. Equal-progress diagonal reference line.
    Average lines as crosshairs. Inspired by image 2.
    """
    nc = "country_name_en" if lang == "en" else "country_name_fr"
    df = key_metrics[["iso3","elec_access_tgt","cooking_tgt"]].copy()
    df = df.merge(countries_df[["iso3", nc]], on="iso3", how="left")
    df = df.dropna(subset=["elec_access_tgt","cooking_tgt"])

    avg_e = df["elec_access_tgt"].mean()
    avg_c = df["cooking_tgt"].mean()

    fig = go.Figure()

    # Diagonal equal-progress reference line
    fig.add_shape(type="line", x0=0, y0=0, x1=120, y1=120,
                  line=dict(color="#E05A5A", width=1.5, dash="dash"))
    fig.add_annotation(x=110, y=112, text="Equal Progress Line",
                       showarrow=False, font=dict(size=8, color="#E05A5A"),
                       bgcolor="rgba(255,255,255,0.8)")

    # Average vertical line (electricity)
    fig.add_shape(type="line", x0=avg_e, y0=0, x1=avg_e, y1=105,
                  line=dict(color="#9AA5B0", width=1, dash="dot"))
    # Average horizontal line (cooking)
    fig.add_shape(type="line", x0=0, y0=avg_c, x1=120, y1=avg_c,
                  line=dict(color="#9AA5B0", width=1, dash="dot"))

    # Scatter dots
    fig.add_trace(go.Scatter(
        x=df["elec_access_tgt"], y=df["cooking_tgt"],
        mode="markers+text",
        text=df[nc],
        textposition="top right",
        textfont=dict(size=8, color="#1B2E3C"),
        marker=dict(size=10, color=TEAL,
                    line=dict(width=1.5, color="white")),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Electricity 2030: <b>%{x:.1f}%</b><br>"
            "Clean Cooking 2030: <b>%{y:.1f}%</b><extra></extra>"
        ),
        name="Countries",
    ))

    fig.update_layout(
        title=dict(
            text="Ambition Targets: Clean Cooking vs. Electricity",
            font=dict(size=13, color="#1B2E3C", family="Inter"), x=0.5, xanchor="center",
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=0, t=40, b=0),
        height=480,
        xaxis=dict(
            title="Target Electricity Access by 2030 (%)",
            range=[0, 115], showgrid=True, gridcolor="#EEF0F3",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="Clean Cooking Access — 2030 Target (%)",
            range=[0, 110], showgrid=True, gridcolor="#EEF0F3",
            tickfont=dict(size=10),
        ),
        annotations=[
            dict(x=avg_e + 1, y=2, text=f"Avg. Electricity ({avg_e:.1f}%)",
                 showarrow=False, font=dict(size=8, color="#6B7A8D"), xanchor="left"),
            dict(x=2, y=avg_c + 2, text=f"Avg. Clean Cooking ({avg_c:.1f}%)",
                 showarrow=False, font=dict(size=8, color="#6B7A8D")),
        ],
        showlegend=False,
    )
    return fig


def build_bubble_capacity_investment(key_metrics, countries_df, lang="en"):
    """
    Bubble chart: countries sorted by investment on x-axis,
    additional capacity (MW) on y-axis, bubble size = investment (USD),
    colour = investment intensity. Inspired by image 3.
    """
    nc = "country_name_en" if lang == "en" else "country_name_fr"
    df = key_metrics[["iso3","cap_target_mw","cap_current_mw","private_invest_usd"]].copy()
    df = df.merge(countries_df[["iso3", nc]], on="iso3", how="left")
    df["add_cap"] = df["cap_target_mw"] - df["cap_current_mw"]
    df = df.dropna(subset=["add_cap","private_invest_usd"])
    df = df[df["private_invest_usd"] > 0]
    df = df.sort_values("private_invest_usd").reset_index(drop=True)

    inv_b = df["private_invest_usd"] / 1e9

    fig = go.Figure(go.Scatter(
        x=df[nc],
        y=df["add_cap"],
        mode="markers",
        marker=dict(
            size=inv_b.apply(lambda v: max(8, min(60, v * 3))),
            color=inv_b,
            colorscale=[[0,"#5A4FCF"],[0.4,"#2AB4AE"],[0.8,"#FBBF24"],[1,"#F59E0B"]],
            showscale=True,
            colorbar=dict(
                title=dict(text="Estimated Investment<br>Required (Billion USD)",
                           font=dict(size=9)),
                tickfont=dict(size=9),
                len=0.7, thickness=12,
            ),
            line=dict(width=1, color="white"),
            opacity=0.88,
        ),
        text=df[nc],
        customdata=inv_b,
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Additional Capacity: <b>%{y:,.0f} MW</b><br>"
            "Investment Required: <b>$%{customdata:.1f}B</b><extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(
            text="Additional Generation Capacity vs. Investment Requirements",
            font=dict(size=13, color="#1B2E3C", family="Inter"), x=0.5, xanchor="center",
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=80, t=44, b=60),
        height=480,
        xaxis=dict(
            title="Country (Sorted by Investment Size)",
            tickangle=-35, tickfont=dict(size=9),
            showgrid=False,
        ),
        yaxis=dict(
            title="Additional Generation Capacity (MW)",
            showgrid=True, gridcolor="#EEF0F3", tickfont=dict(size=10),
        ),
        showlegend=False,
    )
    return fig


def build_quadrant_scatter(key_metrics, countries_df, lang="en"):
    """
    Quadrant scatter: normalised performance score (x) vs total investment (y).
    4 coloured quadrants + bubble size = population proxy (electricity gap).
    Inspired by image 1.
    """
    nc = "country_name_en" if lang == "en" else "country_name_fr"
    df = key_metrics[["iso3","elec_access_cur","renew_share_cur",
                       "cooking_cur","private_invest_usd"]].copy()
    df = df.merge(countries_df[["iso3", nc]], on="iso3", how="left")
    df = df.dropna(subset=["private_invest_usd"])

    # Normalised composite score 0-1 from available indicators
    for col in ["elec_access_cur","renew_share_cur","cooking_cur"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["score"] = df[["elec_access_cur","renew_share_cur","cooking_cur"]].mean(axis=1, skipna=True) / 100
    df = df.dropna(subset=["score"])
    df["inv_b"] = df["private_invest_usd"] / 1e9

    # Thresholds for quadrants
    med_score = 0.5
    med_inv   = df["inv_b"].median()

    QUAD_COLORS = {
        "Critical Risk":         "#E05A5A",   # low perf, high inv
        "High Performance":      "#27AE60",   # high perf, high inv
        "Low Performance":       "#D4A017",   # low perf, low inv
        "High Perf / Low Inv":   "#9AA5B0",   # high perf, low inv
    }

    def _quad(row):
        hi_s = row["score"] >= med_score
        hi_i = row["inv_b"] >= med_inv
        if not hi_s and hi_i:  return "Critical Risk"
        if hi_s and hi_i:      return "High Performance"
        if not hi_s and not hi_i: return "Low Performance"
        return "High Perf / Low Inv"

    df["quad"] = df.apply(_quad, axis=1)

    fig = go.Figure()

    # Background quadrant shading
    x_mid, y_mid = med_score, med_inv
    quad_shapes = [
        dict(type="rect", x0=0, x1=x_mid, y0=y_mid, y1=df["inv_b"].max()*1.15,
             fillcolor="rgba(224,90,90,0.07)", line_width=0),
        dict(type="rect", x0=x_mid, x1=1.05, y0=y_mid, y1=df["inv_b"].max()*1.15,
             fillcolor="rgba(39,174,96,0.07)", line_width=0),
        dict(type="rect", x0=0, x1=x_mid, y0=0, y1=y_mid,
             fillcolor="rgba(212,160,23,0.07)", line_width=0),
        dict(type="rect", x0=x_mid, x1=1.05, y0=0, y1=y_mid,
             fillcolor="rgba(154,165,176,0.07)", line_width=0),
    ]
    quad_annotations = [
        dict(x=0.1, y=df["inv_b"].max()*1.05,
             text="<b>CRITICAL<br>RISK GROUP</b>",
             font=dict(size=9, color="#E05A5A"),
             bgcolor="rgba(255,255,255,0.75)", showarrow=False, align="left"),
        dict(x=0.95, y=df["inv_b"].max()*1.05,
             text="High Performance<br>High Investment (Green)",
             font=dict(size=8, color="#27AE60"),
             bgcolor="rgba(255,255,255,0.75)", showarrow=False, align="right"),
        dict(x=0.1, y=y_mid*0.3,
             text="Low Performance<br>Low Investment (Darker Yellow)",
             font=dict(size=8, color="#D4A017"),
             bgcolor="rgba(255,255,255,0.75)", showarrow=False, align="left"),
        dict(x=0.95, y=y_mid*0.3,
             text="High Performance<br>Low Investment (Grey)",
             font=dict(size=8, color="#9AA5B0"),
             bgcolor="rgba(255,255,255,0.75)", showarrow=False, align="right"),
    ]

    for q, color in QUAD_COLORS.items():
        sub = df[df["quad"] == q]
        if sub.empty: continue
        fig.add_trace(go.Scatter(
            x=sub["score"], y=sub["inv_b"],
            mode="markers+text",
            name=q,
            text=sub["iso3"],
            textposition="top center",
            textfont=dict(size=7.5, color="#1B2E3C"),
            marker=dict(
                size=sub["inv_b"].apply(lambda v: max(10, min(45, v * 2.5))),
                color=color, opacity=0.85,
                line=dict(width=1.5, color="white"),
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Performance Score: <b>%{x:.2f}</b><br>"
                "Total Investment: <b>$%{y:.1f}B</b><extra></extra>"
            ),
        ))

    # Crosshair lines
    fig.add_shape(type="line", x0=x_mid, x1=x_mid, y0=0, y1=df["inv_b"].max()*1.15,
                  line=dict(color="#C5CDD6", width=1, dash="dash"))
    fig.add_shape(type="line", x0=0, x1=1.05, y0=y_mid, y1=y_mid,
                  line=dict(color="#C5CDD6", width=1, dash="dash"))

    fig.update_layout(
        title=dict(
            text="Performance vs. Investment Ambition — Quadrant Analysis",
            font=dict(size=13, color="#1B2E3C", family="Inter"), x=0.5, xanchor="center",
        ),
        shapes=quad_shapes,
        annotations=quad_annotations,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=0, t=44, b=0),
        height=500,
        xaxis=dict(
            title="Composite Performance Score (Normalised 0-1)",
            range=[0, 1.05], showgrid=True, gridcolor="#EEF0F3",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="Expansion Ambition (Total Investment, USD Billion)",
            showgrid=True, gridcolor="#EEF0F3", tickfont=dict(size=10),
        ),
        legend=dict(
            orientation="v", x=1.01, y=0.95,
            font=dict(size=8.5), bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#DDE2E8", borderwidth=1,
        ),
    )
    return fig


# ═══════════════════════════════════════════════════════
# ALIASES & MISSING FUNCTIONS needed by app.py v4
# ═══════════════════════════════════════════════════════

def build_radar_chart(km_row: dict, country_name: str, lang: str = "en"):
    """Radar: 4 axes — Electricity, Renewable, Cooking, Investment (normalised)."""
    def _gv(k):
        v = km_row.get(k, np.nan)
        return float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else None

    elec_c = _gv("elec_access_cur");  elec_t = _gv("elec_access_tgt")
    ren_c  = _gv("renew_share_cur");  ren_t  = _gv("renew_share_tgt")
    cook_c = _gv("cooking_cur");      cook_t = _gv("cooking_tgt")
    p_inv  = _gv("private_invest_usd")
    INV_MAX = 10e9

    def _ni(v): return min(100, round(v / INV_MAX * 100, 1)) if v else 0

    labels = ["Electricity\nAccess", "Renewable\nShare", "Clean\nCooking", "Investment\n(norm.)"]
    cats   = labels + [labels[0]]
    cur_r  = [elec_c or 0, ren_c or 0, cook_c or 0, _ni(p_inv)] + [elec_c or 0]
    tgt_r  = [elec_t or 0, ren_t or 0, cook_t or 0, _ni(p_inv)] + [elec_t or 0]

    fig = go.Figure()
    if any(v > 0 for v in tgt_r):
        fig.add_trace(go.Scatterpolar(
            r=tgt_r, theta=cats, fill="toself",
            fillcolor="rgba(247,148,29,0.10)",
            line=dict(color=ORANGE, width=2, dash="dash"),
            name="2030 Target", mode="lines",
        ))
    if any(v > 0 for v in cur_r):
        fig.add_trace(go.Scatterpolar(
            r=cur_r, theta=cats, fill="toself",
            fillcolor="rgba(0,161,154,0.18)",
            line=dict(color=TEAL, width=2.5),
            name="Current", mode="lines+markers",
            marker=dict(size=5, color=TEAL),
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(size=8, color="#6B7A8D"),
                            gridcolor="#DDE2E8", ticksuffix="%"),
            angularaxis=dict(tickfont=dict(size=8.5, color="#1B2E3C"),
                             linecolor="#DDE2E8"),
            bgcolor="#FAFAFA",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.08,
                    font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=20, r=20, t=20, b=30), height=240,
    )
    return fig


def _get_comparison_data(key_metrics, iso3_list, nc_map):
    rows = []
    for iso3 in iso3_list:
        km = key_metrics[key_metrics["iso3"] == iso3]
        if km.empty: continue
        km = km.iloc[0]
        def _gv(f):
            try: return float(km[f])
            except: return np.nan
        rows.append({
            "iso3": iso3, "country": nc_map.get(iso3, iso3),
            "elec_cur": _gv("elec_access_cur"), "elec_tgt": _gv("elec_access_tgt"),
            "ren_cur":  _gv("renew_share_cur"), "ren_tgt":  _gv("renew_share_tgt"),
            "cook_cur": _gv("cooking_cur"),      "cook_tgt": _gv("cooking_tgt"),
            "inv":      _gv("private_invest_usd"),
        })
    return pd.DataFrame(rows)


def build_comparison_grouped_bar(df):
    if df.empty: return go.Figure()
    kpis = [
        ("Electricity Access (%)", "elec_cur", "elec_tgt"),
        ("Renewable Share (%)",    "ren_cur",  "ren_tgt"),
        ("Clean Cooking (%)",      "cook_cur", "cook_tgt"),
    ]
    fig = go.Figure()
    countries = df["country"].tolist()
    for label, cur_col, tgt_col in kpis:
        fig.add_trace(go.Bar(
            name=f"{label} — Current", x=countries, y=df[cur_col],
            marker_color=TEAL, marker_opacity=0.9,
            hovertemplate=f"<b>%{{x}}</b><br>{label} current: <b>%{{y:.1f}}%</b><extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name=f"{label} — 2030", x=countries, y=df[tgt_col],
            marker_color=ORANGE, marker_opacity=0.55,
            marker_line_color=ORANGE, marker_line_width=1.2,
            hovertemplate=f"<b>%{{x}}</b><br>{label} 2030: <b>%{{y:.1f}}%</b><extra></extra>",
        ))
    fig.update_layout(
        barmode="group", bargap=0.18, bargroupgap=0.04,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=0, t=8, b=0), height=380,
        xaxis=dict(tickfont=dict(size=10), showgrid=False),
        yaxis=dict(title="%", showgrid=True, gridcolor="#EEF0F3", tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.06, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    return fig


def build_comparison_radar(df, lang="en"):
    if df.empty or len(df) < 2: return go.Figure()
    axes = ["Electricity<br>Access", "Renewable<br>Share",
            "Clean<br>Cooking", "Investment<br>(norm.)"]
    axes_c = axes + [axes[0]]
    INV_MAX = df["inv"].max() if df["inv"].notna().any() else 10e9
    if pd.isna(INV_MAX) or INV_MAX == 0: INV_MAX = 10e9

    fig = go.Figure()
    for i, row in df.iterrows():
        inv_n = min(100, float(row["inv"]) / INV_MAX * 100) if pd.notna(row["inv"]) else 0
        vals  = [row["elec_cur"] or 0, row["ren_cur"] or 0,
                 row["cook_cur"] or 0, inv_n] + [row["elec_cur"] or 0]
        color = LINE_PALETTE[i % len(LINE_PALETTE)]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=axes_c, fill="toself",
            fillcolor="rgba(0,0,0,0.03)",
            line=dict(color=color, width=2), name=row["country"],
            mode="lines+markers", marker=dict(size=5, color=color),
            hovertemplate=f"<b>{row['country']}</b><br>Score: <b>%{{r:.1f}}</b><extra></extra>",
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(size=8, color="#6B7A8D"),
                            gridcolor="#DDE2E8", ticksuffix="%"),
            angularaxis=dict(tickfont=dict(size=9, color="#1B2E3C")),
            bgcolor="#FAFAFA",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="v", x=1.05, y=0.95, font=dict(size=8.5),
                    bgcolor="rgba(255,255,255,0.9)", bordercolor="#DDE2E8", borderwidth=1),
        margin=dict(l=20, r=120, t=20, b=20), height=420,
    )
    return fig


def build_comparison_lollipop(df):
    if df.empty: return go.Figure()
    d = df.dropna(subset=["elec_cur"]).sort_values("elec_cur", ascending=True)
    fig = go.Figure()
    for _, row in d.iterrows():
        x1 = row["elec_tgt"] if pd.notna(row["elec_tgt"]) else row["elec_cur"]
        fig.add_shape(type="line", x0=0, x1=x1, y0=row["country"], y1=row["country"],
                      line=dict(color="#DDE2E8", width=1.5))
    fig.add_trace(go.Scatter(
        x=d["elec_cur"], y=d["country"], mode="markers", name="Current",
        marker=dict(size=10, color=TEAL, line=dict(width=1.5, color="white")),
        hovertemplate="<b>%{y}</b><br>Current: <b>%{x:.1f}%</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=d["elec_tgt"], y=d["country"], mode="markers", name="2030 Target",
        marker=dict(size=10, color=ORANGE, symbol="diamond", line=dict(width=1.5, color="white")),
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
    if df.empty: return go.Figure()
    d = df.copy()
    INV_MAX = d["inv"].max() if d["inv"].notna().any() else 10e9
    if pd.isna(INV_MAX) or INV_MAX == 0: INV_MAX = 10e9
    d["inv_n"] = d["inv"].apply(lambda v: min(100, v/INV_MAX*100) if pd.notna(v) else np.nan)
    cols   = ["elec_cur","ren_cur","cook_cur","inv_n"]
    labels = ["Electricity\nAccess %","Renewable\nShare %","Clean\nCooking %","Investment\n(norm.)"]
    matrix = d[cols].values
    fig = go.Figure(go.Heatmap(
        z=matrix, x=labels, y=d["country"].tolist(),
        colorscale=[[0,TEAL_L],[0.5,TEAL],[1,NAVY]],
        text=[[f"{v:.1f}" if pd.notna(v) else "—" for v in row] for row in matrix],
        texttemplate="%{text}", textfont=dict(size=10, color="white"),
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> — %{x}<br>Value: <b>%{z:.1f}</b><extra></extra>",
        colorbar=dict(title="Value (0-100)", tickfont=dict(size=9), len=0.8, thickness=10),
        zmin=0, zmax=100,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=0, t=8, b=0),
        height=max(280, len(d) * 28),
        xaxis=dict(tickfont=dict(size=10), side="top"),
        yaxis=dict(tickfont=dict(size=10), autorange="reversed"),
    )
    return fig


def build_rankings_chart(key_metrics, countries_df, kpi_col, kpi_label, unit,
                         lang="en", top_n=5):
    """Top 5 (teal) + Bottom 5 (grey) horizontal bar."""
    nc = "country_name_en" if lang == "en" else "country_name_fr"
    df = key_metrics[["iso3", kpi_col]].copy()
    df = df.merge(countries_df[["iso3", nc]], on="iso3", how="left")
    df = df.dropna(subset=[kpi_col]).sort_values(kpi_col, ascending=False).reset_index(drop=True)
    if df.empty: return go.Figure()

    top = df.head(top_n).assign(_grp="Top")
    bot = df.tail(top_n).assign(_grp="Bottom")
    combined = pd.concat([bot, top]).drop_duplicates("iso3")
    combined  = combined.sort_values(kpi_col, ascending=True)

    colors = [TEAL if g == "Top" else "#A8B4C0" for g in combined["_grp"]]
    fig = go.Figure(go.Bar(
        x=combined[kpi_col], y=combined[nc],
        orientation="h", marker_color=colors,
        text=combined[kpi_col].apply(lambda v: f"{v:.1f} {unit}"),
        textposition="outside", textfont=dict(size=9.5),
        hovertemplate="<b>%{y}</b>: <b>%{x:.1f} " + unit + "</b><extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=f"<b>{kpi_label}</b>",
                   font=dict(size=11, color="#1B2E3C"), x=0,
                   pad=dict(l=0, t=12)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
        margin=dict(l=0, r=80, t=36, b=0),
        height=max(240, len(combined)*28),
        xaxis=dict(title=unit, showgrid=True, gridcolor="#EEF0F3", tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, tickfont=dict(size=9.5)),
    )
    return fig


def build_scorecard_chart(key_metrics, countries_df, lang="en"):
    nc = "country_name_en" if lang == "en" else "country_name_fr"
    df = key_metrics[["iso3","elec_access_cur","elec_access_tgt",
                       "renew_share_cur","renew_share_tgt",
                       "cooking_cur","cooking_tgt","private_invest_usd"]].copy()
    df = df.merge(countries_df[["iso3", nc]], on="iso3", how="left")
    df = df.sort_values(nc).reset_index(drop=True)

    def _fmt(v, is_inv=False):
        if pd.isna(v): return "—"
        if is_inv:
            if v >= 1e9: return f"${v/1e9:.1f}B"
            if v >= 1e6: return f"${v/1e6:.0f}M"
            return f"${v:,.0f}"
        return f"{v:.1f}%"

    col_headers = ["Country",
                   "Electricity\nCurrent","Electricity\n2030",
                   "Renewable\nCurrent","Renewable\n2030",
                   "Cooking\nCurrent","Cooking\n2030",
                   "Investment\nRequired"]
    cell_vals = []
    for _, row in df.iterrows():
        cell_vals.append([
            row[nc],
            _fmt(row["elec_access_cur"]), _fmt(row["elec_access_tgt"]),
            _fmt(row["renew_share_cur"]), _fmt(row["renew_share_tgt"]),
            _fmt(row["cooking_cur"]),     _fmt(row["cooking_tgt"]),
            _fmt(row["private_invest_usd"], is_inv=True),
        ])
    header_colors = [NAVY]*1 + [TEAL, ORANGE]*3 + [NAVY]
    fig = go.Figure(go.Table(
        header=dict(
            values=[f"<b>{h}</b>" for h in col_headers],
            fill_color=header_colors, font=dict(color="white", size=9),
            align="center", height=34, line=dict(color="#FFFFFF", width=1),
        ),
        cells=dict(
            values=list(zip(*cell_vals)),
            fill_color=["#F5F7FA"] + ["white"]*7,
            font=dict(color=["#1B2E3C"]*1 + ["#00A19A","#F7941D"]*3 + ["#1B3A5C"],
                      size=9.5),
            align=["left"] + ["center"]*7, height=26,
            line=dict(color="#DDE2E8", width=0.5),
        ),
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=4, b=0),
        height=max(350, len(df) * 28 + 50),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
