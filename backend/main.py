from fastapi import FastAPI
from agent.orchestrator import run_agent
from agent.trends import get_trends

app = FastAPI(title="Agent éditorial IA")


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/generate")
def generate(payload: dict):
    subject = payload.get("subject")
    if not subject:
        return {"error": "subject manquant"}

    return run_agent(subject)


@app.get("/generate_from_trends")
def generate_from_trends():
    trends = get_trends("rss")

    if not trends:
        return {
            "analysis": "Aucune tendance trouvée",
            "tweets": []
        }

    subject = trends[0]
    return run_agent(subject)
