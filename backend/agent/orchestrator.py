from agent.modes import shortlist_modes
from agent.generator import generate_variants
from agent.scoring import rank_tweets
from agent.memory_adapter import learn_from_result


def run_agent(subject: str) -> dict:
    # 1️⃣ Choix intelligent des angles
    modes = shortlist_modes(subject)

    # 2️⃣ Génération
    tweets = generate_variants(
        subject=subject,
        modes=modes,
        n=12
    )

    # 3️⃣ Scoring
    top_tweets = rank_tweets(tweets, top_k=5)

    # 4️⃣ Apprentissage
    learn_from_result(modes, top_tweets)

    return {
        "analysis": "Observation générale",
        "modes": modes,
        "tweets": tweets,
        "top_tweets": top_tweets
    }
