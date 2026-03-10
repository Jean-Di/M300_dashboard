"""
PDF factsheet — M300 NEC v3
SEforALL palette · No assessment language · Key indicators first
"""
from io import BytesIO
import datetime
import math
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
from reportlab.platypus import Flowable

# ── SEforALL palette ──────────────────────────────────────────────────────────
C_NAVY   = colors.HexColor("#1B3A5C")
C_TEAL   = colors.HexColor("#00A19A")
C_ORANGE = colors.HexColor("#F7941D")
C_TEAL_L = colors.HexColor("#E8F7F7")
C_ORG_L  = colors.HexColor("#FEF4E6")
C_WHITE  = colors.white
C_DARK   = colors.HexColor("#1B2E3C")
C_GRAY   = colors.HexColor("#6B7A8D")
C_LIGHT  = colors.HexColor("#F5F7FA")
C_BORDER = colors.HexColor("#DDE2E8")
C_BG_KPI = colors.HexColor("#F0F4F8")   # neutral card background
C_BAR_BG = colors.HexColor("#DDE2E8")   # progress bar track


class ProgressBar(Flowable):
    """A simple horizontal progress bar for ReportLab."""
    def __init__(self, width, pct, color, height=4, radius=2):
        Flowable.__init__(self)
        self.bar_width = width
        self.pct       = min(100, max(0, pct or 0))
        self.color     = color
        self.height    = height
        self.radius    = radius
        self.width     = width
        self.hh        = height

    def draw(self):
        # Background track
        self.canv.setFillColor(C_BAR_BG)
        self.canv.roundRect(0, 0, self.bar_width, self.height,
                            self.radius, fill=1, stroke=0)
        # Fill
        fill_w = self.bar_width * self.pct / 100
        if fill_w > 0:
            self.canv.setFillColor(self.color)
            self.canv.roundRect(0, 0, fill_w, self.height,
                                self.radius, fill=1, stroke=0)


def _safe(val, fmt="{:.1f}", suffix="", fallback="—"):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return fallback
    return fmt.format(val) + (" " + suffix if suffix else "")


def _fmt_inv(val):
    """Format investment value nicely."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "—"
    if val >= 1e9: return f"${val/1e9:.2f}B"
    if val >= 1e6: return f"${val/1e6:.1f}M"
    return f"${val:,.0f}"


def generate_country_pdf(
    country_name: str,
    iso3: str,
    key_metrics: dict,
    country_indicators: dict,
    lang: str = "en",
) -> bytes:
    buf = BytesIO()
    w, h = A4
    margin = 15 * mm
    cw = w - 2 * margin

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=12 * mm, bottomMargin=10 * mm,
    )

    # ── Label strings (EN / FR) ───────────────────────────────────────────────
    if lang == "fr":
        L = {
            "subtitle":    "Compact National Énergie · Mission 300",
            "key_ind":     "Indicateurs clés",
            "elec_lbl":    "Accès à l'électricité",
            "ren_lbl":     "Part des énergies renouvelables",
            "cook_lbl":    "Accès à la cuisson propre",
            "inv_lbl":     "Financement privé requis",
            "pub_lbl":     "Financement public requis",
            "tot_lbl":     "Investissement total requis",
            "current_lbl": "Actuel",
            "target_lbl":  "Cible 2030",
            "all_ind":     "Indicateurs sélectionnés",
            "sources":     "Sources : M300 National Energy Compacts · SEforALL",
            "note":        ("Les données reflètent les engagements déclarés dans les Compacts Nationaux Énergie "
                            "et ne constituent pas une évaluation indépendante. "
                            "Les cellules vides indiquent l'absence de données dans le Compact."),
            "generated":   f"Généré le {datetime.date.today().strftime('%d/%m/%Y')}",
        }
    else:
        L = {
            "subtitle":    "National Energy Compact · Mission 300",
            "key_ind":     "Key Indicators",
            "elec_lbl":    "Electricity Access",
            "ren_lbl":     "Renewable Energy Share",
            "cook_lbl":    "Clean Cooking Access",
            "inv_lbl":     "Private Financing Required",
            "pub_lbl":     "Public Financing Required",
            "tot_lbl":     "Total Investment Required",
            "current_lbl": "Current",
            "target_lbl":  "2030 Target",
            "all_ind":     "Selected Indicators",
            "sources":     "Sources: M300 National Energy Compacts · SEforALL",
            "note":        ("Data reflect commitments declared in National Energy Compacts and do not "
                            "constitute an independent assessment. Empty cells indicate absence of "
                            "data in the Compact."),
            "generated":   f"Generated {datetime.date.today().strftime('%Y-%m-%d')}",
        }

    # ── Paragraph styles ─────────────────────────────────────────────────────
    def ps(name, **kw):
        kw.setdefault("fontName", "Helvetica")
        return ParagraphStyle(name, **kw)

    s_title   = ps("t", fontSize=19, textColor=C_WHITE,  fontName="Helvetica-Bold", leading=23)
    s_sub     = ps("s", fontSize=8.5,textColor=colors.HexColor("#7BA8C9"), leading=11)
    s_sec     = ps("sc",fontSize=7.5, textColor=C_TEAL,  fontName="Helvetica-Bold",
                   leading=10, spaceBefore=8, spaceAfter=3)
    s_lbl     = ps("lb",fontSize=7,  textColor=C_GRAY,   leading=9)
    s_cur     = ps("cu",fontSize=11, textColor=C_TEAL,   fontName="Helvetica-Bold", leading=13)
    s_tgt     = ps("tg",fontSize=11, textColor=C_ORANGE, fontName="Helvetica-Bold", leading=13)
    s_inv     = ps("iv",fontSize=11, textColor=C_NAVY,   fontName="Helvetica-Bold", leading=13)
    s_body    = ps("bo",fontSize=8.5,textColor=C_DARK,   leading=13)
    s_small   = ps("sm",fontSize=7,  textColor=C_GRAY,   leading=10)
    s_cat     = ps("ca",fontSize=8.5,textColor=C_NAVY,   fontName="Helvetica-Bold",
                   leading=11, spaceBefore=5, spaceAfter=2)
    s_note    = ps("nt",fontSize=7,  textColor=C_GRAY,   fontName="Helvetica-Oblique", leading=10)

    elems = []
    km = key_metrics

    # ═══════════════════════════════════════
    # HEADER — navy background
    # ═══════════════════════════════════════
    hdr = Table(
        [[Paragraph(country_name, s_title),
          Paragraph(iso3, ps("ic", fontSize=14, textColor=colors.HexColor("#7BA8C9"),
                             fontName="Helvetica-Bold", leading=18))]],
        colWidths=[cw * 0.75, cw * 0.25],
    )
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_NAVY),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",         (1,0),(1,0),   "RIGHT"),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(0,0),   10),
        ("RIGHTPADDING",  (1,0),(1,0),   10),
    ]))
    elems.append(hdr)
    sub_row = Table(
        [[Paragraph(L["subtitle"], s_sub)]],
        colWidths=[cw],
    )
    sub_row.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
    ]))
    elems.append(sub_row)
    elems.append(HRFlowable(width="100%", thickness=2.5, color=C_TEAL, spaceAfter=8, spaceBefore=1))

    # ═══════════════════════════════════════
    # KEY INDICATORS — always first
    # ═══════════════════════════════════════
    elems.append(Paragraph(L["key_ind"], s_sec))

    def kpi_card(label, cur_val_raw, cur_str, tgt_val_raw, tgt_str):
        """
        New KPI card design:
        - Neutral grey background
        - Indicator name top-left
        - Current (teal) left | Target (orange) right
        - Progress bar: current/target ratio below
        """
        # Compute progress pct
        try:
            pct = min(100, round(float(cur_val_raw) / float(tgt_val_raw) * 100, 1)) \
                  if cur_val_raw and tgt_val_raw and float(tgt_val_raw) > 0 else None
        except Exception:
            pct = None

        bar_w = cw - 18  # bar width in points

        # Label row
        lbl_t = Table([[Paragraph(label, ps("kl", fontSize=7, textColor=C_GRAY,
                                             fontName="Helvetica-Bold",
                                             letterSpacing=0.5, leading=9))]],
                      colWidths=[cw])
        lbl_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 2),
            ("LEFTPADDING",   (0,0),(-1,-1), 9),
        ]))

        # Values row
        col_w = (cw - 4) / 2
        val_t = Table([[
            [Paragraph(L["current_lbl"],
                       ps("cl2", fontSize=6.5, textColor=C_TEAL,
                          fontName="Helvetica-Bold", leading=9)),
             Paragraph(cur_str,
                       ps("cv", fontSize=16, textColor=C_TEAL,
                          fontName="Helvetica-Bold", leading=19))],
            [Paragraph(L["target_lbl"],
                       ps("tl2", fontSize=6.5, textColor=C_ORANGE,
                          fontName="Helvetica-Bold", leading=9)),
             Paragraph(tgt_str,
                       ps("tv", fontSize=16, textColor=C_ORANGE,
                          fontName="Helvetica-Bold", leading=19))],
        ]], colWidths=[col_w, col_w])
        val_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("TOPPADDING",    (0,0),(-1,-1), 2),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 9),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
            ("LINEAFTER",     (0,0),(0,-1),  0.5, C_BORDER),
        ]))

        # Progress bar row
        if pct is not None:
            pb_label = f"{pct:.0f}% of 2030 target" if lang == "en" else f"{pct:.0f}% de la cible 2030"
            bar_tbl = Table([[
                ProgressBar(bar_w, pct, C_TEAL),
                Paragraph(pb_label, ps("pb", fontSize=6.5, textColor=C_TEAL,
                                        fontName="Helvetica-Bold", leading=8)),
            ]], colWidths=[bar_w * 0.65, bar_w * 0.35])
            bar_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
                ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
                ("TOPPADDING",    (0,0),(-1,-1), 0),
                ("BOTTOMPADDING", (0,0),(-1,-1), 7),
                ("LEFTPADDING",   (0,0),(0,0),   9),
                ("LEFTPADDING",   (1,0),(1,0),   6),
            ]))
        else:
            bar_tbl = Table([[Paragraph("", ps("e", fontSize=4, leading=4))]],
                            colWidths=[cw])
            bar_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0),(-1,-1), C_BG_KPI),
                ("TOPPADDING", (0,0),(-1,-1), 0),
                ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ]))

        # Outer wrapper with left accent border
        outer = Table([
            [lbl_t],
            [val_t],
            [bar_tbl],
        ], colWidths=[cw], spaceBefore=4, spaceAfter=4)
        outer.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
            ("LINEBELOW",     (0,-1),(-1,-1), 0.5, C_BORDER),
            ("LINEBEFORE",    (0,0),(0,-1),   3,   C_TEAL),
            ("BOX",           (0,0),(-1,-1),  0.5, C_BORDER),
            ("TOPPADDING",    (0,0),(-1,-1),  0),
            ("BOTTOMPADDING", (0,0),(-1,-1),  0),
            ("LEFTPADDING",   (0,0),(-1,-1),  0),
            ("RIGHTPADDING",  (0,0),(-1,-1),  0),
        ]))
        return outer

    def kpi_card_single(label, val_str, val_raw=None, total_raw=None):
        """Single-value KPI card for investment (no current baseline)."""
        try:
            pct = min(100, round(float(val_raw) / float(total_raw) * 100, 1)) \
                  if val_raw and total_raw and float(total_raw) > 0 else None
        except Exception:
            pct = None

        bar_w = cw - 18

        lbl_t = Table([[Paragraph(label, ps("kl2", fontSize=7, textColor=C_GRAY,
                                              fontName="Helvetica-Bold",
                                              letterSpacing=0.5, leading=9))]],
                      colWidths=[cw])
        lbl_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 2),
            ("LEFTPADDING",   (0,0),(-1,-1), 9),
        ]))

        val_t = Table([[
            Paragraph(L["target_lbl"],
                      ps("tl3", fontSize=6.5, textColor=C_ORANGE,
                         fontName="Helvetica-Bold", leading=9)),
            Paragraph(val_str,
                      ps("vs", fontSize=16, textColor=C_NAVY,
                         fontName="Helvetica-Bold", leading=19)),
        ]], colWidths=[cw * 0.25, cw * 0.75])
        val_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
            ("VALIGN",        (0,0),(-1,-1), "BOTTOM"),
            ("TOPPADDING",    (0,0),(-1,-1), 2),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 9),
        ]))

        if pct is not None:
            pb_label = f"{pct:.1f}% of M300 total"
            bar_tbl = Table([[
                ProgressBar(bar_w * 0.65, pct, C_NAVY),
                Paragraph(pb_label, ps("pb2", fontSize=6.5, textColor=C_NAVY,
                                        fontName="Helvetica-Bold", leading=8)),
            ]], colWidths=[bar_w * 0.65, bar_w * 0.35])
            bar_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
                ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
                ("TOPPADDING",    (0,0),(-1,-1), 0),
                ("BOTTOMPADDING", (0,0),(-1,-1), 7),
                ("LEFTPADDING",   (0,0),(0,0),   9),
                ("LEFTPADDING",   (1,0),(1,0),   6),
            ]))
        else:
            bar_tbl = Table([[Paragraph("", ps("e2", fontSize=4, leading=4))]],
                            colWidths=[cw])
            bar_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
                ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ]))

        outer = Table([[lbl_t], [val_t], [bar_tbl]],
                      colWidths=[cw], spaceBefore=4, spaceAfter=4)
        outer.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_BG_KPI),
            ("LINEBEFORE",    (0,0),(0,-1),   3,   C_ORANGE),
            ("BOX",           (0,0),(-1,-1),  0.5, C_BORDER),
            ("TOPPADDING",    (0,0),(-1,-1),  0),
            ("BOTTOMPADDING", (0,0),(-1,-1),  0),
            ("LEFTPADDING",   (0,0),(-1,-1),  0),
            ("RIGHTPADDING",  (0,0),(-1,-1),  0),
        ]))
        return outer

    # Electricity access
    elec_c = km.get("elec_access_cur") or km.get("access_current")
    elec_t = km.get("elec_access_tgt") or km.get("access_target_2030")
    elems.append(kpi_card(
        L["elec_lbl"],
        elec_c, _safe(elec_c, suffix="%"),
        elec_t, _safe(elec_t, suffix="%"),
    ))

    # Renewable share
    ren_c = km.get("renew_share_cur")
    ren_t = km.get("renew_share_tgt") or km.get("renew_share_target_2030")
    elems.append(kpi_card(
        L["ren_lbl"],
        ren_c, _safe(ren_c, suffix="%"),
        ren_t, _safe(ren_t, suffix="%"),
    ))

    # Clean cooking
    cook_c = km.get("cooking_cur")
    cook_t = km.get("cooking_tgt") or km.get("cooking_target_2030")
    elems.append(kpi_card(
        L["cook_lbl"],
        cook_c, _safe(cook_c, suffix="%"),
        cook_t, _safe(cook_t, suffix="%"),
    ))

    # Private investment — total for % share calculation
    p_inv   = km.get("private_invest_usd") or km.get("private_financing_usd")
    tot_inv = km.get("total_invest_usd")
    elems.append(kpi_card_single(L["inv_lbl"], _fmt_inv(p_inv),
                                  val_raw=p_inv, total_raw=tot_inv))

    elems.append(Spacer(1, 4))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER, spaceAfter=6))

    # ═══════════════════════════════════════
    # SELECTED INDICATORS BY CATEGORY
    # ═══════════════════════════════════════
    if country_indicators:
        elems.append(Paragraph(L["all_ind"], s_sec))

        for cat, ind_list in country_indicators.items():
            if not ind_list:
                continue
            elems.append(Paragraph(cat, s_cat))

            rows = []
            for ind_label, value, unit, ind_type in ind_list:
                val_str  = _safe(value, "{:,.1f}", unit)
                lbl_str  = L["current_lbl"] if ind_type == "current" else (
                           L["target_lbl"]  if ind_type == "target"  else "")
                lbl_col  = C_TEAL if ind_type == "current" else C_ORANGE
                rows.append([
                    Paragraph(ind_label, ps("il", fontName="Helvetica", fontSize=7.5,
                                             textColor=C_DARK, leading=10)),
                    Paragraph(val_str,   ps("iv", fontName="Helvetica-Bold", fontSize=8,
                                             textColor=C_DARK, leading=10)),
                    Paragraph(lbl_str,   ps("it", fontName="Helvetica-Bold", fontSize=7,
                                             textColor=lbl_col, leading=10)),
                ])

            if rows:
                t = Table(rows, colWidths=[cw*0.58, cw*0.25, cw*0.17])
                t.setStyle(TableStyle([
                    ("ROWBACKGROUNDS", (0,0),(-1,-1), [C_WHITE, C_LIGHT]),
                    ("TOPPADDING",    (0,0),(-1,-1), 3),
                    ("BOTTOMPADDING", (0,0),(-1,-1), 3),
                    ("LEFTPADDING",   (0,0),(-1,-1), 5),
                    ("RIGHTPADDING",  (0,0),(-1,-1), 5),
                    ("LINEBELOW",     (0,-1),(-1,-1), 0.3, C_BORDER),
                    ("LINEAFTER",     (0,0),(1,-1),   0.2, C_BORDER),
                ]))
                elems.append(t)

    # ═══════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════
    elems.append(Spacer(1, 8))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=C_TEAL, spaceAfter=4))
    elems.append(Paragraph(L["note"], s_note))
    elems.append(Spacer(1, 3))
    foot = Table(
        [[Paragraph(L["sources"], s_small),
          Paragraph(L["generated"], ps("gn", fontName="Helvetica", fontSize=7,
                                        textColor=C_GRAY, leading=10, alignment=2))]],
        colWidths=[cw*0.70, cw*0.30],
    )
    foot.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
    elems.append(foot)

    doc.build(elems)
    return buf.getvalue()