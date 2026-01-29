from agent.memory_engine import register_success

def learn_from_result(modes: list[str], tweets: list[str]):
    score = len(tweets)
    for mode in modes:
        register_success(mode)
