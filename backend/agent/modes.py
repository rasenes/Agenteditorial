# Tous les angles disponibles

ALL_MODES = [
    "observation_froide",
    "question_directe",
    "ironie_legere",
    "constat_genant",
    "hypocrisie_sociale",
    "liberte_individuelle",
    "absurdite_du_systeme",
    "bon_sens_populaire",
    "minimal",
    "miroir_societe",
    "tech_lucide",
    "humour_noir_soft",
    "journalisme_humain",
]


# Angles sûrs selon le type de sujet
SMART_GROUPS = {
    "politique": [
        "observation_froide",
        "journalisme_humain",
        "hypocrisie_sociale",
        "question_directe",
    ],
    "societe": [
        "miroir_societe",
        "bon_sens_populaire",
        "absurdite_du_systeme",
    ],
    "tech": [
        "tech_lucide",
        "observation_froide",
        "minimal",
    ],
}


def shortlist_modes(subject: str) -> list[str]:
    s = subject.lower()

    if any(k in s for k in ["loi", "etat", "assemblee", "politique"]):
        return SMART_GROUPS["politique"]

    if any(k in s for k in ["ia", "tech", "algorithme"]):
        return SMART_GROUPS["tech"]

    return SMART_GROUPS["societe"]
