from agent.modes import shortlist_modes
from agent.generator import generate_variants
from agent.remix import remix
from agent.scoring import rank_tweets
from agent.sources import get_trending_subjects
from agent.rss_engine import fetch_rss_ideas
from agent.reddit_engine import fetch_reddit_ideas
from agent.viral_corpus import get_viral_ideas
from agent.memory_adapter import learn_from_result


def run_agent(subject: str | None = None) -> dict:
    ideas = []

    ideas += fetch_rss_ideas()
    ideas += fetch_reddit_ideas()
    ideas += get_viral_ideas()

    if not subject:
        subject = ideas[0] if ideas else get_trending_subjects()[0]

    modes = shortlist_modes(subject)

    tweets = generate_variants(subject, modes, n=20)

    remixed = []
    for t in tweets:
        remixed.append(t)
        remixed.extend(remix(t))

    final = rank_tweets(remixed, top_k=5)

    learn_from_result(modes, final)

    return {
        "analysis": "Pipeline complet : RSS + Reddit + Viral + Remix + Scoring + Memory",
        "subject": subject,
        "modes": modes,
        "tweets": final,
    }
