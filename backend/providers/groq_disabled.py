import os
from backend.providers.groq import Groq

def generate(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY manquant")

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "Tu es un excellent créateur de tweets en français."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
    )

    return completion.choices[0].message.content.strip()
