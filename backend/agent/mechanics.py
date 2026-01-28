def detect_mechanic(analysis: dict):
    if not analysis or not isinstance(analysis, dict):
        return "neutral"

    return analysis.get("mechanic", "neutral")
