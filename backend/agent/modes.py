ALL_MODES = {
    "miroir": "Identification implicite",
    "confession": "Vulnérabilité maîtrisée",
    "bugderire": "Ironie douce",
    "humour_noir": "Lucidité sombre",
    "renversement": "Surprise calme",
    "minimal": "Impact pur",

    "meta_systeme": "Règles implicites",
    "observateur_froid": "Distance analytique",
    "contre_narratif": "Opposition calme",
    "desenchante": "Lucidité fatiguée",

    "tech_lucide": "Anti-hype technologique",
    "hacker": "Démystification système",
    "business_froid": "Logique économique nue"
}

MECHANIC_TO_MODES = {
    "social": ["miroir", "bugderire", "renversement"],
    "systeme": ["meta_systeme", "observateur_froid"],
    "tech": ["tech_lucide", "hacker"],
    "emotion": ["confession", "miroir"]
}

def choose_modes(mechanic: str, forced_mode: str | None = None, bias: list[str] | None = None):
    # sécurité : mode invalide → auto
    if forced_mode and forced_mode not in ALL_MODES and forced_mode != "auto":
        forced_mode = "auto"

    if forced_mode and forced_mode != "auto":
        return [forced_mode]

    modes = MECHANIC_TO_MODES.get(mechanic, ["miroir"]).copy()

    if bias:
        for b in bias:
            if b in ALL_MODES and b not in modes:
                modes.append(b)

    return modes[:3]

def allowed_modes_by_level(level: int) -> list[str]:
    if level >= 70:
        return ["journalisme_x", "observateur_froid"]
    if level >= 50:
        return ["journalisme_x", "miroir", "en_clair"]
    if level >= 30:
        return ["miroir", "renversement", "implicite"]
    return ["implicite", "minimal", "silence"]
