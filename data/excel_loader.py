"""
Excel loader for M300 National Energy Compacts dataset.

Structure expected (Complete_Data_Quantitative sheet):
  Col A : Category  (forward-filled merged cells)
  Col B : Indicator
  Col C : Data Source
  Col D : Comments
  Col E+: Country names (English)
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

from data.country_mapping import name_to_iso3, get_name_fr, get_name_en
from data.config import TARGET_YEAR, YEARS_LEFT, THRESHOLD_ON_TRACK, THRESHOLD_TO_WATCH

MAIN_SHEET = "Complete_Data_Quantitative"

# ── Keyword classifiers ───────────────────────────────────────────────────────
CURRENT_KW = ["current", "existing", "– current", "- current", "actuel"]
TARGET_KW  = ["target", "2030", "required", "added", "new", "cible", "objectif"]
DATE_KW    = ["last update", "date", "compact start", "compact end"]

# Categories to exclude from the main indicator list (metadata rows)
META_CATEGORIES = {"Compact Timeline", "Population", "Date",
                   "Electricity Access (derived)", "Clean Cooking Access (derived)"}


def _classify(name: str) -> str:
    n = name.lower()
    if any(k in n for k in DATE_KW):    return "date_meta"
    if any(k in n for k in CURRENT_KW): return "current"
    if any(k in n for k in TARGET_KW):  return "target"
    return "other"


def _unit(name: str) -> str:
    m = re.search(r'\(([^)]+)\)', name)
    return m.group(1) if m else ""


def _ffill(s: pd.Series) -> pd.Series:
    return s.replace("", pd.NA).ffill()


def load_nec_excel(filepath: str | Path) -> dict:
    filepath = Path(filepath)
    raw = pd.read_excel(filepath, sheet_name=MAIN_SHEET, header=0, dtype=str)
    cols = list(raw.columns)

    # Detect Comments column (col index 3)
    comment_col = None
    has_comments = False
    if len(cols) > 3:
        c3 = str(cols[3]).strip().lower()
        if any(w in c3 for w in {"comments", "notes", "comment", "note"}):
            comment_col = cols[3]
            has_comments = True

    country_start = 4 if has_comments else 3
    country_cols_raw = [c for c in cols[country_start:] if not str(c).startswith("Unnamed")]

    # Build country → ISO3 mapping
    country_map = {}
    for col in country_cols_raw:
        iso3 = name_to_iso3(str(col).strip())
        if iso3:
            country_map[col] = iso3

    if not country_map:
        raise ValueError("No country columns detected in the Excel file.")

    # Forward-fill Category
    raw.iloc[:, 0] = _ffill(raw.iloc[:, 0])
    raw = raw.dropna(subset=[cols[1]])
    raw = raw[raw.iloc[:, 1].str.strip().str.len() > 0].copy()

    rows = []
    date_per_country = {}

    for _, row in raw.iterrows():
        category  = str(row.iloc[0]).strip()
        indicator = str(row.iloc[1]).strip()
        source    = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else "NEC"
        comment   = str(row[comment_col]).strip() if (comment_col and pd.notna(row.get(comment_col))) else ""
        ind_type  = _classify(indicator)
        unit      = _unit(indicator)
        is_meta   = category in META_CATEGORIES

        for col, iso3 in country_map.items():
            raw_val = row.get(col)
            is_nan  = pd.isna(raw_val) or str(raw_val).strip() in ("", "nan", "None", "-", "N/A")

            if ind_type == "date_meta" or (is_meta and "update" in indicator.lower()):
                if not is_nan:
                    date_per_country[iso3] = str(raw_val).strip()
                continue

            value = np.nan
            if not is_nan:
                try:
                    value = float(str(raw_val).replace(",", "").strip())
                except ValueError:
                    pass

            rows.append({
                "category":        category,
                "indicator":       indicator,
                "unit":            unit,
                "source":          source,
                "comment":         comment,
                "ind_type":        ind_type,
                "is_meta":         is_meta,
                "country_name_en": get_name_en(iso3),
                "country_name_fr": get_name_fr(iso3),
                "iso3":            iso3,
                "value":           value,
                "has_data":        not np.isnan(value) if isinstance(value, float) else True,
            })

    long_df = pd.DataFrame(rows)

    # Filter to non-meta for main indicators
    main_df = long_df[~long_df["is_meta"]].copy()

    # Countries dataframe
    countries_df = (
        main_df[["iso3", "country_name_en", "country_name_fr"]]
        .drop_duplicates("iso3")
        .sort_values("country_name_en")
        .reset_index(drop=True)
    )
    countries_df["data_date"] = countries_df["iso3"].map(date_per_country).fillna("—")
    counts = main_df[main_df["has_data"]].groupby("iso3").size().reset_index(name="n_indicators")
    countries_df = countries_df.merge(counts, on="iso3", how="left")
    countries_df["n_indicators"] = countries_df["n_indicators"].fillna(0).astype(int)

    # Indicators metadata
    indicators_df = (
        main_df[["category", "indicator", "unit", "source", "ind_type", "comment"]]
        .drop_duplicates("indicator")
        .reset_index(drop=True)
    )

    # Pivot tables
    pivot_current = main_df[main_df["ind_type"] == "current"].pivot_table(
        index="indicator", columns="iso3", values="value", aggfunc="first"
    )
    pivot_target = main_df[main_df["ind_type"] == "target"].pivot_table(
        index="indicator", columns="iso3", values="value", aggfunc="first"
    )

    categories = sorted(
        [c for c in main_df["category"].unique() if c not in META_CATEGORIES]
    )

    key_metrics = _compute_key_metrics(main_df)

    return {
        "long":             main_df,
        "countries":        countries_df,
        "indicators":       indicators_df,
        "categories":       categories,
        "pivot_current":    pivot_current,
        "pivot_target":     pivot_target,
        "key_metrics":      key_metrics,
        "evolution":        None,
        "date_per_country": date_per_country,
    }


# ── Key metrics computation ───────────────────────────────────────────────────

def _first_match(df: pd.DataFrame, keyword: str, ind_type: str, require_2030: bool = False) -> pd.Series:
    """Return the first matching value per iso3."""
    mask = (
        df["indicator"].str.lower().str.contains(keyword, na=False, regex=False) &
        (df["ind_type"] == ind_type)
    )
    if require_2030:
        mask &= df["indicator"].str.lower().str.contains("2030", na=False, regex=False)
    return df[mask].groupby("iso3")["value"].first()


def _compute_key_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the 4 priority KPIs per country:
      1. Electricity Access  (current %, target %)
      2. Renewable Share     (current %, target %)
      3. Clean Cooking       (current %, target %)
      4. Private Investment  (target USD — no current baseline in Compacts)
    Plus: installed capacity, progress, gap analysis, data completeness.
    """
    # ── 1. Electricity Access ─────────────────────────────────────────────────
    elec_cur = _first_match(df, "current electricity access rate", "current")
    elec_tgt = _first_match(df, "target electricity access rate", "target", require_2030=True)

    # ── 2. Renewable Share ────────────────────────────────────────────────────
    ren_share_cur = _first_match(df, "renewable share", "current")
    ren_share_tgt = _first_match(df, "renewable share", "target", require_2030=True)

    # Fallback: renewable capacity if share not available
    ren_cap_cur = _first_match(df, "renewable capacity", "current")
    ren_cap_tgt = _first_match(df, "renewable capacity", "target", require_2030=True)

    # ── 3. Clean Cooking ──────────────────────────────────────────────────────
    cook_cur = _first_match(df, "clean cooking access - current", "current")
    # fallback
    if cook_cur.empty:
        cook_cur = _first_match(df, "clean cooking access", "current")
    cook_tgt = _first_match(df, "clean cooking access - 2030", "target")
    if cook_tgt.empty:
        cook_tgt = _first_match(df, "clean cooking access", "target", require_2030=True)

    # ── 4. Private Investment ─────────────────────────────────────────────────
    priv_invest = _first_match(df, "private financing", "target")
    if priv_invest.empty:
        priv_invest = _first_match(df, "private financing", "other")

    # ── Installed Capacity (for secondary panel) ──────────────────────────────
    cap_cur = _first_match(df, "installed capacity", "current")
    cap_tgt = _first_match(df, "installed capacity", "target", require_2030=True)

    # ── System Losses ─────────────────────────────────────────────────────────
    loss_cur = _first_match(df, "system losses", "current")

    rows = []
    for iso3 in df["iso3"].unique():
        ac = elec_cur.get(iso3, np.nan)
        at = elec_tgt.get(iso3, np.nan)

        rsc = ren_share_cur.get(iso3, np.nan)
        rst = ren_share_tgt.get(iso3, np.nan)
        use_share = not (np.isnan(rsc) and np.isnan(rst))

        rcc = ren_cap_cur.get(iso3, np.nan)
        rct = ren_cap_tgt.get(iso3, np.nan)

        cc  = cook_cur.get(iso3, np.nan)
        ct  = cook_tgt.get(iso3, np.nan)
        pi  = priv_invest.get(iso3, np.nan)

        cp  = cap_cur.get(iso3, np.nan)
        cpt = cap_tgt.get(iso3, np.nan)
        lc  = loss_cur.get(iso3, np.nan)

        # Progress on electricity access
        prog = (
            min(100.0, round(ac / at * 100, 1))
            if (not np.isnan(ac) and not np.isnan(at) and at > 0)
            else np.nan
        )
        gap = round(at - ac, 1) if (not np.isnan(ac) and not np.isnan(at)) else np.nan
        annual_needed = round(gap / YEARS_LEFT, 2) if (not np.isnan(gap) and YEARS_LEFT > 0) else np.nan

        if np.isnan(prog):        status = "no_target"
        elif prog >= THRESHOLD_ON_TRACK: status = "on_track"
        elif prog >= THRESHOLD_TO_WATCH: status = "to_watch"
        else:                     status = "behind"

        # Data completeness
        cd    = df[df["iso3"] == iso3]
        n_tot = len(cd)
        comp  = round(cd["has_data"].sum() / n_tot * 100, 1) if n_tot > 0 else 0.0

        rows.append({
            "iso3":                 iso3,
            # Priority 4 KPIs
            "elec_access_cur":      ac,
            "elec_access_tgt":      at,
            "renew_share_cur":      rsc if use_share else np.nan,
            "renew_share_tgt":      rst if use_share else np.nan,
            "renew_cap_cur":        rcc,
            "renew_cap_tgt":        rct,
            "renew_use_share":      use_share,
            "cooking_cur":          cc,
            "cooking_tgt":          ct,
            "private_invest_usd":   pi,
            # Secondary
            "cap_current_mw":       cp,
            "cap_target_mw":        cpt,
            "system_losses_pct":    lc,
            # Progress / status
            "progress_access":      prog,
            "gap_access_pts":       gap,
            "annual_pts_needed":    annual_needed,
            "status":               status,
            "data_completeness":    comp,
            # Legacy aliases (for PDF generator compatibility)
            "access_current":       ac,
            "access_target_2030":   at,
            "capacity_current_mw":  cp,
            "capacity_target_mw":   cpt,
            "renew_current_mw":     rcc,
            "renew_target_mw":      rct,
            "system_losses_pct":    lc,
            "cooking_target_2030":  ct,
            "renew_share_target_2030": rst,
            "private_financing_usd": pi,
        })

    return pd.DataFrame(rows)
