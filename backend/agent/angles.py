# backend/agent/angles.py

from dataclasses import dataclass
from typing import List


@dataclass
class Angle:
    name: str
    weight: float
    tags: List[str]


# 🔥 REGISTRE CENTRAL DES ANGLES
ALL_ANGLES: List[Angle] = [

    Angle("miroir", 1.0, ["psychologie", "implicite"]),
    Angle("minimal", 0.9, ["court", "silence"]),
    Angle("confession", 0.95, ["émotion", "humain"]),
    Angle("renversement", 1.1, ["surprise", "contradiction"]),
    Angle("observateur_froid", 1.0, ["lucide", "extérieur"]),

    Angle("business_froid", 1.1, ["argent", "pouvoir"]),
    Angle("tech_lucide", 1.0, ["tech", "réalité"]),
    Angle("meta_systeme", 1.05, ["système", "structure"]),
    Angle("humour_noir", 0.85, ["ironie", "provocation"]),

    # extensible à l’infini
]


# 🎯 SCORE D’UN ANGLE SELON LE CONTEXTE
def score_angle(angle: Angle, context: str) -> float:
    score = angle.weight

    ctx = context.lower()

    for tag in angle.tags:
        if tag in ctx:
            score += 0.15

    return round(score, 2)


# 🧠 SHORTLIST ADAPTATIVE
def shortlist_angles(context: str,
                     min_angles: int = 3,
                     max_angles: int = 9,
                     threshold: float = 0.72) -> List[str]:

    scored = [
        (angle.name, score_angle(angle, context))
        for angle in ALL_ANGLES
    ]

    scored.sort(key=lambda x: x[1], reverse=True)

    selected = [name for name, score in scored if score >= threshold]

    # garde-fous
    if len(selected) < min_angles:
        selected = [name for name, _ in scored[:min_angles]]

    if len(selected) > max_angles:
        selected = selected[:max_angles]

    return selected
