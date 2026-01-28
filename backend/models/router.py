import yaml
from providers.ollama import Ollama

with open("settings.yaml", "r", encoding="utf-8") as f:
    SETTINGS = yaml.safe_load(f)

def get_generator():
    provider = SETTINGS["generation"]["provider"]
    model = SETTINGS["generation"]["model"]

    if provider == "ollama":
        return Ollama(model)

    raise ValueError(f"Provider inconnu : {provider}")
