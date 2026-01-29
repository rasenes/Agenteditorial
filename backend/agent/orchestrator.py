from agent.analysis import analyze_subject
from agent.angles import shortlist_angles
from agent.generator import generate_variants
from agent.filters import filter_variants


def run_agent(subject: str, forced_mode: str | None = None):
    # 1. Analyse du sujet
    analysis = analyze_subject(subject)

    # 2. Sélection des angles
    if forced_mode:
        modes = [forced_mode]
    else:
        modes = shortlist_angles(subject)

    # Sécurité
    if not modes:
        modes = ["factuel", "opinion"]

    # 3. Génération brute
    drafts = generate_variants(
        subject=subject,
        modes=modes,
        n=12
    )

    # 4. Filtrage éditorial
    tweets = filter_variants(drafts)

    # Fallback
    if not tweets:
        tweets = drafts[:3]

    return {
        "analysis": analysis.get("summary", ""),
        "modes": modes,
        "tweets": tweets[:6]
    }
