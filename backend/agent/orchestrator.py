# backend/agent/orchestrator.py

from agent.generator import generate_variants
from agent.filters import filter_variants
from agent.analysis import analyze_subject
from agent.modes import ALL_MODES


def run_agent(
    subject: str,
    n: int = 10,
    forced_mode: str | None = None,
):
    # 1. Analyse simple
    analysis = analyze_subject(subject)

    # 2. Choix des modes
    if forced_mode and forced_mode in ALL_MODES:
        modes = [forced_mode]
    else:
        # AUTO : on en prend plusieurs volontairement
        modes = ALL_MODES[:6]

    # 3. Génération brute
    drafts = generate_variants(
        subject=subject,
        modes=modes,
        n=n
    )

    # Sécurité
    if not drafts:
        drafts = []

    # 4. Filtrage éditorial
    tweets = filter_variants(drafts)

    # Fallback
    if not tweets:
        tweets = [t for t in drafts if isinstance(t, str)]

    return {
        "analysis": analysis.get("summary", ""),
        "modes": modes,
        "tweets": tweets[:5],
    }
