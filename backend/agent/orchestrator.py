from agent.modes import shortlist_modes
from agent.generator import generate_variants
from agent.scoring import rank_tweets
# ...existing code...

def run_agent(subject: str) -> dict:
    # 1️⃣ Choix intelligent des angles
    modes = shortlist_modes(subject)

    # 2️⃣ Génération
    tweets = generate_variants(
        subject=subject,
        modes=modes,
        n=12
    )

    # 3️⃣ Classement (évite l'utilisation d'une variable non définie au niveau module)
    top_tweets = rank_tweets(tweets, top_k=5)

    return {
        "analysis": "Observation générale",
        "modes": modes,
        "tweets": tweets,
        "top_tweets": top_tweets,
    }