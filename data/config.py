"""
NEC Platform — Configuration
Edit this file to update dates, narrative texts, and thresholds.
No Python knowledge required for text edits.
"""

LAST_UPDATED    = "Mars 2026"
LAST_UPDATED_EN = "March 2026"

TARGET_YEAR  = 2030
CURRENT_YEAR = 2024
YEARS_LEFT   = TARGET_YEAR - CURRENT_YEAR  # 6

NARRATIVE = {
    "fr": {
        "headline": "Plateforme Africaine des Pacts Énergie",
        "subtitle": "Unis vers les Objectifs 2030",
        "intro": (
            "La Mission 300 (M300) est une initiative conjointe du Groupe de la Banque mondiale et de la Banque Africaine de Développement (BAD)," 
            "soutenue par la Fondation Rockefeller, Sustainable Energy for All (SEforALL) et Global Energy Alliance (GEA), qui vise à fournir un accès à l'électricité à 300 millions d'Africains d'ici 2030" 
            "Cet objectif ambitieux vise à réduire de moitié le nombre actuel de personnes sans électricité sur le continent, en favorisant le développement durable" 
            "grâce à la collaboration et à des solutions innovantes "
        ),
        "mission": (
            "Le programme repose sur le leadership des gouvernements africains, qui, en collaboration avec leurs partenaires,  élaborent et mettent en œuvre" 
            " des pactes nationaux sur l'énergie, qui définissent des cibles ambitieuses assorties de calendriers précis pour: (i) développer les infrastructures énergétiques à des coûts compétitifs," 
            " (ii) renforcer l’intégration régionale des réseaux, (iii) promouvoir les énergies renouvelables décentralisées et les solutions de cuisson propre, (iv) encourager la participation du secteur privé et renforcer les entreprises de services publics."
            " Ces Compacts sont entièrement dirigés par les gouvernements, qui sont encouragés à organiser des consultations publiques avec la société civile et les parties prenantes afin d’enrichir leur élaboration"
        ),
        "update_note": "Données issues des Pacts Nationaux Énergie (Mission 300). Dernière mise à jour : {date}.",
        "disclaimer": (
            "Les données présentées sont issues des Pacts Nationaux Énergie (Mission 300). "
            "Elles reflètent les engagements déclarés et ne constituent pas une évaluation indépendante "
            "des performances. Les cellules vides indiquent l'absence de données dans le Pact. "
            "Elles ne sont ni interpolées ni estimées."
        ),
        "years_left": "ans restants",
    },
    "en": {
        "headline": "African Energy Compacts Platform",
        "subtitle": "United toward 2030 Targets",
        "intro": (
            "Mission 300 (M300) is a joint initiative by the World Bank (WB) Group and the African Development Bank (AfDB)," 
            "supported by The Rockefeller Foundation, Sustainable Energy for All (SEforALL), and Global Energy Alliance (GEA), which aims to provide electricity access to 300 million Africans by 2030." 
            "This ambitious goal seeks to halve the current number of people without electricity on the continent, driving sustainable development "
            "through collaboration and innovative solutions"
        ),
        "mission": (
            "The program relies on the leadership of African governments, which, in collaboration with their partners,  develop and implement" 
            " national energy compacts that set ambitious targets with specific timelines for: (i) developing energy infrastructure at competitive costs," 
            " (ii) strengthen regional grid integration, (iii) promote decentralized renewable energy and clean cooking solutions, (iv) encourage private sector participation and strengthen utilities."
            " These Compacts are entirely government-led, with governments encouraged to hold public consultations with civil society and stakeholders to inform their development."
        ),
        "update_note": "Data sourced from National Energy Compacts (Mission 300). Last updated: {date}.",
        "disclaimer": (
            "Data presented are sourced from National Energy Compacts (Mission 300). "
            "They reflect declared commitments and do not constitute an independent performance "
            "assessment. Empty cells indicate absence of data - not interpolated or estimated."
        ),
        "years_left": "years remaining",
    },
}

# Status thresholds (% of target achieved)
THRESHOLD_ON_TRACK = 80
THRESHOLD_TO_WATCH = 50

# Small island markers for choropleth overlay
ISLAND_MARKERS = {
    "COM": {"lat": -11.7, "lon": 43.3,  "name_fr": "Comores",             "name_en": "Comoros"},
    "STP": {"lat":   0.2, "lon":  6.6,  "name_fr": "São Tomé & Príncipe", "name_en": "São Tomé & Príncipe"},
}
