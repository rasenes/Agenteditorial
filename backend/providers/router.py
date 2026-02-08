from providers.ollama import generate as ollama_generate


def generate(prompt: str) -> str:
    return ollama_generate(prompt)
