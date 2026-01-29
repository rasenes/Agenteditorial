from fastapi import FastAPI
from agent.orchestrator import run_agent

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Agent Editorial Ready"}

@app.get("/generate")
def generate(subject: str | None = None):
    return run_agent(subject)
