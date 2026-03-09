"""
Comprehensive mapping of African country names (English) to ISO 3166-1 alpha-3 codes.
Used by excel_loader.py to auto-detect country columns.
"""

# Primary mapping: exact English name → ISO3
COUNTRY_NAME_TO_ISO3 = {
    # A
    "Algeria": "DZA",
    "Angola": "AGO",
    # B
    "Benin": "BEN",
    "Botswana": "BWA",
    "Burkina Faso": "BFA",
    "Burundi": "BDI",
    # C
    "Cabo Verde": "CPV",
    "Cape Verde": "CPV",
    "Cameroon": "CMR",
    "Central African Republic": "CAF",
    "Chad": "TCD",
    "Comoros": "COM",
    "Congo": "COG",
    "Congo, Dem. Rep.": "COD",
    "Congo, Rep.": "COG",
    "DRC": "COD",
    "DR Congo": "COD",
    "Democratic Republic of Congo": "COD",
    "Democratic Republic of the Congo": "COD",
    "Republic of Congo": "COG",
    "Côte d'Ivoire": "CIV",
    "Cote d'Ivoire": "CIV",
    "Côte D'Ivoire": "CIV",
    "Ivory Coast": "CIV",
    # D
    "Djibouti": "DJI",
    # E
    "Egypt": "EGY",
    "Equatorial Guinea": "GNQ",
    "Eritrea": "ERI",
    "Eswatini": "SWZ",
    "Swaziland": "SWZ",
    "Ethiopia": "ETH",
    # G
    "Gabon": "GAB",
    "Gambia": "GMB",
    "The Gambia": "GMB",
    "Ghana": "GHA",
    "Guinea": "GIN",
    "Guinea-Bissau": "GNB",
    # K
    "Kenya": "KEN",
    # L
    "Lesotho": "LSO",
    "Liberia": "LBR",
    "Libya": "LBY",
    # M
    "Madagascar": "MDG",
    "Malawi": "MWI",
    "Mali": "MLI",
    "Mauritania": "MRT",
    "Mauritius": "MUS",
    "Morocco": "MAR",
    "Mozambique": "MOZ",
    # N
    "Namibia": "NAM",
    "Niger": "NER",
    "Nigeria": "NGA",
    # R
    "Rwanda": "RWA",
    # S
    "São Tomé and Príncipe": "STP",
    "Sao Tome and Principe": "STP",
    "São Tomé & Príncipe": "STP",
    "Sao Tome & Principe": "STP",
    "São Tomé-et-Príncipe": "STP",
    "Saint Thomas and Prince": "STP",
    "Senegal": "SEN",
    "Seychelles": "SYC",
    "Sierra Leone": "SLE",
    "Somalia": "SOM",
    "South Africa": "ZAF",
    "South Sudan": "SSD",
    "Sudan": "SDN",
    # T
    "Tanzania": "TZA",
    "United Republic of Tanzania": "TZA",
    "Togo": "TGO",
    "Tunisia": "TUN",
    # U
    "Uganda": "UGA",
    # Z
    "Zambia": "ZMB",
    "Zimbabwe": "ZWE",
}

# French name → ISO3 (bonus)
COUNTRY_NAME_FR_TO_ISO3 = {
    "Algérie": "DZA",
    "Angola": "AGO",
    "Bénin": "BEN",
    "Botswana": "BWA",
    "Burkina Faso": "BFA",
    "Burundi": "BDI",
    "Cabo Verde": "CPV",
    "Cameroun": "CMR",
    "Centrafrique": "CAF",
    "République centrafricaine": "CAF",
    "Tchad": "TCD",
    "Comores": "COM",
    "Congo": "COG",
    "RD Congo": "COD",
    "République démocratique du Congo": "COD",
    "Côte d'Ivoire": "CIV",
    "Djibouti": "DJI",
    "Égypte": "EGY",
    "Guinée équatoriale": "GNQ",
    "Érythrée": "ERI",
    "Eswatini": "SWZ",
    "Éthiopie": "ETH",
    "Gabon": "GAB",
    "Gambie": "GMB",
    "Ghana": "GHA",
    "Guinée": "GIN",
    "Guinée-Bissau": "GNB",
    "Kenya": "KEN",
    "Lesotho": "LSO",
    "Liberia": "LBR",
    "Libye": "LBY",
    "Madagascar": "MDG",
    "Malawi": "MWI",
    "Mali": "MLI",
    "Mauritanie": "MRT",
    "Maurice": "MUS",
    "Maroc": "MAR",
    "Mozambique": "MOZ",
    "Namibie": "NAM",
    "Niger": "NER",
    "Nigéria": "NGA",
    "Rwanda": "RWA",
    "Sénégal": "SEN",
    "Seychelles": "SYC",
    "Sierra Leone": "SLE",
    "Somalie": "SOM",
    "Afrique du Sud": "ZAF",
    "Soudan du Sud": "SSD",
    "Soudan": "SDN",
    "Tanzanie": "TZA",
    "Togo": "TGO",
    "Tunisie": "TUN",
    "Ouganda": "UGA",
    "Zambie": "ZMB",
    "Zimbabwe": "ZWE",
}

# ISO3 → French name
ISO3_TO_NAME_FR = {v: k for k, v in COUNTRY_NAME_FR_TO_ISO3.items() if k == list(COUNTRY_NAME_FR_TO_ISO3.keys())[list(COUNTRY_NAME_FR_TO_ISO3.values()).index(v)]}

# Build reverse lookups
ISO3_TO_NAME_EN = {v: k for k, v in COUNTRY_NAME_TO_ISO3.items()}

def name_to_iso3(name: str) -> str | None:
    """
    Convert a country name (any casing, EN or FR) to ISO3.
    Returns None if not found.
    """
    if not name or not isinstance(name, str):
        return None
    # Try exact match first
    for mapping in [COUNTRY_NAME_TO_ISO3, COUNTRY_NAME_FR_TO_ISO3]:
        if name in mapping:
            return mapping[name]
    # Try case-insensitive
    name_lower = name.strip().lower()
    for mapping in [COUNTRY_NAME_TO_ISO3, COUNTRY_NAME_FR_TO_ISO3]:
        for k, v in mapping.items():
            if k.lower() == name_lower:
                return v
    # Partial match as fallback
    for mapping in [COUNTRY_NAME_TO_ISO3, COUNTRY_NAME_FR_TO_ISO3]:
        for k, v in mapping.items():
            if name_lower in k.lower() or k.lower() in name_lower:
                return v
    return None


def get_name_en(iso3: str) -> str:
    return ISO3_TO_NAME_EN.get(iso3, iso3)


def get_name_fr(iso3: str) -> str:
    return ISO3_TO_NAME_FR.get(iso3, get_name_en(iso3))
