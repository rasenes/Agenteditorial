from fastapi import FastAPI
from agent.orchestrator import run_agent

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/generate")
def generate(subject: str):
    print(">>> ROUTE /generate APPELÉE AVEC :", subject)
    result = run_agent(subject)
    print(">>> RÉSULTAT OK")
    return result

@app.get("/generate_from_trends")
def generate_from_trends():
    print(">>> ROUTE /generate_from_trends")
    return run_agent("tendances actuelles")
