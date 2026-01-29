import requests
import json

class Ollama:
    def __init__(self, model: str):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 60  # limite forte pour éviter les blocages
            }
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )
        except requests.exceptions.Timeout:
            return "[ERREUR] Timeout Ollama"
        except Exception as e:
            return f"[ERREUR] {e}"

        if response.status_code != 200:
            return f"[ERREUR HTTP] {response.status_code}"

        try:
            data = response.json()
        except json.JSONDecodeError:
            return "[ERREUR] Réponse Ollama invalide"

        return data.get("response", "").strip()

def generate(prompt: str) -> str:
    """
    Wrapper standard utilisé par l'agent éditorial
    """
    return ask_ollama(prompt)  # <-- remplace par TA vraie fonction
