def analyze_subject(subject: str) -> dict:
    if not subject:
        return {"summary": ""}

    # Analyse simple mais stable
    if "mais" in subject or "quand même" in subject:
        summary = "Tension implicite, potentiel miroir"
    else:
        summary = "Observation générale"

    return {
        "summary": summary
    }

def compute_journalism_level(subject: str, source: str = "trend") -> int:
    subject = subject.lower()

    if any(k in subject for k in ["loi", "sénat", "gouvernement", "justice"]):
        return 55
    if any(k in subject for k in ["mort", "drame", "attaque", "incendie"]):
        return 35
    if any(k in subject for k in ["ia", "tech", "startup", "business"]):
        return 45
    if source == "rss":
        return 50

    return 40
