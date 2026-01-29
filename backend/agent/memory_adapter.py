from agent.memory_engine import register_success


def learn_from_result(modes, top_tweets):
    if not top_tweets:
        return

    best_tweet = top_tweets[0]

    for mode in modes:
        register_success(mode, best_tweet)
