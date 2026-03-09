"""Bilingual translations FR / EN"""

from data.config import LAST_UPDATED, LAST_UPDATED_EN

LABELS = {
    # App
    "app_title":    {"fr": "Trajectoires Énergétiques — Afrique",
                     "en": "Energy Trajectories — Africa"},
    "app_subtitle": {"fr": "Pacts Nationaux Énergie · Mission 300",
                     "en": "National Energy Compacts · Mission 300"},

    # Navigation
    "nav_dashboard":   {"fr": "Tableau de bord",  "en": "Dashboard"},
    "nav_comparison":  {"fr": "Comparaison pays",  "en": "Country Comparison"},
    "nav_evolution":   {"fr": "Évolution",          "en": "Evolution"},
    "nav_methodology": {"fr": "Méthodologie",       "en": "Methodology"},

    # Filters
    "panel_filters":     {"fr": "Filtres",                 "en": "Filters"},
    "select_category":   {"fr": "Catégorie",               "en": "Category"},
    "select_indicator":  {"fr": "Indicateur",              "en": "Indicator"},
    "display_mode":      {"fr": "Mode d'affichage",        "en": "Display mode"},
    "mode_current":      {"fr": "Valeurs actuelles",       "en": "Current values"},
    "mode_target":       {"fr": "Cibles 2030",             "en": "2030 targets"},
    "mode_progress":     {"fr": "Progression vers cible",  "en": "Progress toward target"},
    "mode_gap":          {"fr": "Analyse des écarts",      "en": "Gap analysis"},
    "mode_completeness": {"fr": "Complétude des données",  "en": "Data completeness"},

    # Country profile — 4 priority KPIs
    "panel_country":    {"fr": "Profil pays",               "en": "Country Profile"},
    "hint_click":       {"fr": "Cliquez sur un pays pour afficher son profil",
                         "en": "Click a country to display its profile"},
    "kpi_elec_access":  {"fr": "Accès électricité",         "en": "Electricity Access"},
    "kpi_renew":        {"fr": "Énergie renouvelable",       "en": "Renewable Energy"},
    "kpi_renew_share":  {"fr": "Part renouvelable",          "en": "Renewable Share"},
    "kpi_renew_cap":    {"fr": "Capacité renouvelable",      "en": "Renewable Capacity"},
    "kpi_cooking":      {"fr": "Cuisson propre",             "en": "Clean Cooking"},
    "kpi_investment":   {"fr": "Investissement privé requis","en": "Private Investment Required"},
    "current":          {"fr": "Actuel",    "en": "Current"},
    "target_2030":      {"fr": "Cible 2030","en": "2030 Target"},
    "progress":         {"fr": "Progression","en": "Progress"},

    # KPI bar (aggregated)
    "kpi_countries":       {"fr": "Pays couverts",          "en": "Countries covered"},
    "kpi_indicators":      {"fr": "Indicateurs",            "en": "Indicators"},
    "kpi_avg_elec":        {"fr": "Accès élec. moyen",      "en": "Avg. electricity access"},
    "kpi_avg_cooking":     {"fr": "Cuisson propre moy.",    "en": "Avg. clean cooking"},
    "kpi_avg_renew":       {"fr": "Part renouv. moy.",      "en": "Avg. renewable share"},
    "kpi_total_invest":    {"fr": "Invest. privé total",    "en": "Total private invest."},

    # Secondary panel fields
    "capacity_current":    {"fr": "Capacité installée",     "en": "Installed capacity"},
    "capacity_target":     {"fr": "Cible capacité 2030",    "en": "2030 capacity target"},
    "losses":              {"fr": "Pertes réseau",           "en": "Network losses"},
    "n_indicators":        {"fr": "indicateurs disponibles","en": "indicators available"},
    "compact_year":        {"fr": "Compact signé",          "en": "Compact signed"},
    "data_completeness":   {"fr": "Complétude données",     "en": "Data completeness"},
    "view_all":            {"fr": "Voir tous les indicateurs","en": "View all indicators"},
    "progress_to_target":  {"fr": "Progression vers cible 2030",
                            "en": "Progress toward 2030 target"},

    # Gap
    "gap_pts":        {"fr": "pts d'écart restants", "en": "pts gap remaining"},
    "annual_needed":  {"fr": "pts/an nécessaires",   "en": "pts/yr needed"},

    # Status badges
    "on_track":  {"fr": "En trajectoire", "en": "On Track"},
    "to_watch":  {"fr": "À surveiller",   "en": "To Watch"},
    "behind":    {"fr": "En retard",      "en": "Behind"},
    "no_target": {"fr": "Sans cible",     "en": "No target"},
    "no_data":   {"fr": "Données non disponibles", "en": "Data not available"},

    # Map
    "missing_legend": {"fr": "Gris = pas de données (non interpolé)",
                        "en": "Grey = no data (not interpolated)"},

    # Downloads
    "download_pdf":   {"fr": "Télécharger fiche PDF",    "en": "Download PDF factsheet"},
    "download_excel": {"fr": "Exporter données (Excel)", "en": "Export data (Excel)"},

    # Comparison
    "comparison_title":   {"fr": "Comparaison entre pays", "en": "Country Comparison"},
    "select_countries":   {"fr": "Pays à comparer",        "en": "Countries to compare"},
    "comparison_note":    {
        "fr": ("Les valeurs sont issues des Pacts et reflètent les données déclarées. "
               "Elles sont présentées à titre informatif, sans classement ni jugement sur les performances nationales."),
        "en": ("Values are sourced from Compacts and reflect declared data. "
               "Presented for informational purposes only — no ranking or judgment on national performance."),
    },

    # Methodology
    "methodology":      {"fr": "Note méthodologique",     "en": "Methodology note"},
    "methodology_text": {
        "fr": ("Les données sont issues des Pacts Nationaux Énergie (Mission 300). "
               "Les cellules vides signifient l'absence de données dans le Pact — elles ne sont ni interpolées ni estimées. "
               "La plateforme ne porte aucun jugement sur les performances des pays."),
        "en": ("Data are sourced from National Energy Compacts (Mission 300). "
               "Empty cells indicate absence of data — they are not interpolated or estimated. "
               "The platform makes no judgment on country performance."),
    },

    # Footer
    "sources":      {"fr": "Sources : Pacts Nationaux Énergie · Banque Mondiale · BAD · SEforALL",
                     "en": "Sources: National Energy Compacts · World Bank · AfDB · SEforALL"},
    "last_updated": {"fr": f"Mise à jour : {LAST_UPDATED}",
                     "en": f"Updated: {LAST_UPDATED_EN}"},

    # Controls
    "reset_btn":  {"fr": "Réinitialiser",    "en": "Reset"},
    "hint_map":   {"fr": "Cliquez la carte", "en": "Click the map"},

    # Category translations
    "Electricity Access":           {"fr": "Accès électricité",     "en": "Electricity Access"},
    "Generation Capacity & Supply Mix": {"fr": "Capacité de production", "en": "Generation Capacity"},
    "Demand":                       {"fr": "Demande",               "en": "Demand"},
    "Networks & Losses":            {"fr": "Réseaux & Pertes",      "en": "Networks & Losses"},
    "Connections":                  {"fr": "Connexions",            "en": "Connections"},
    "Finance":                      {"fr": "Finance",               "en": "Finance"},
    "Utility & Tariffs":            {"fr": "Services publics",      "en": "Utility & Tariffs"},
    "Renewables, Climate & Efficiency": {"fr": "Renouvelables & Climat", "en": "Renewables & Climate"},
    "Clean Cooking":                {"fr": "Cuisson propre",        "en": "Clean Cooking"},
}


def t(key: str, lang: str = "en") -> str:
    entry = LABELS.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get("en", key))


def status_badge(prog, lang="en") -> tuple[str, str]:
    """Return (label, css_class) for a progress percentage."""
    from data.config import THRESHOLD_ON_TRACK, THRESHOLD_TO_WATCH
    if prog is None or (isinstance(prog, float) and np.isnan(prog)):
        return t("no_target", lang), "badge-grey"
    if prog >= THRESHOLD_ON_TRACK:
        return t("on_track", lang), "badge-green"
    if prog >= THRESHOLD_TO_WATCH:
        return t("to_watch", lang), "badge-orange"
    return t("behind", lang), "badge-red"


import numpy as np
