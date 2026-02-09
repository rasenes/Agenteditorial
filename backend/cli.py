from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.core.config import SETTINGS
from backend.core.utils import now_ts
from backend.models.tweet import GenerateTweetsRequest
from backend.providers.ollama import OllamaClient
from backend.providers.openai import OpenAIClient
from backend.providers.groq import GroqClient


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


async def doctor() -> int:
    print("== Doctor ==")
    print(f"LLM_PROVIDER={SETTINGS.llm.primary_provider}")
    print(f"OLLAMA_BASE_URL={SETTINGS.ollama.base_url}")
    print(f"OLLAMA_MODEL={SETTINGS.ollama.model}")

    ok_any = False

    ollama = OllamaClient()
    ok_ollama = await ollama.healthcheck(timeout=3.0)
    print(f"Ollama: {'OK' if ok_ollama else 'NOT READY'}")
    ok_any = ok_any or ok_ollama

    openai = OpenAIClient()
    ok_openai = await openai.healthcheck(timeout=1.0)
    print(f"OpenAI: {'OK' if ok_openai else 'NOT CONFIGURED'}")
    ok_any = ok_any or ok_openai

    groq = GroqClient()
    ok_groq = await groq.healthcheck(timeout=1.0)
    print(f"Groq: {'OK' if ok_groq else 'NOT CONFIGURED'}")
    ok_any = ok_any or ok_groq

    if not ok_any:
        print("")
        print("No provider ready.")
        print("- For Ollama: install a model, ex: `ollama pull llama3` then set OLLAMA_MODEL if needed.")
        print("- Or set OPENAI_API_KEY / GROQ_API_KEY.")
        return 2

    return 0


async def run_once(args: argparse.Namespace) -> int:
    from backend.agent.orchestrator import orchestrator

    trends = await orchestrator.fetch_trends(limit=args.trends, force_refresh=True)
    if not trends:
        print("No trends fetched. Check your network or RSS sources.")
        return 2

    trend = trends[0]
    theme = args.theme or trend.theme

    request = GenerateTweetsRequest(
        trend_id=trend.id,
        trend_text=None,
        theme=theme,
        style=args.style,
        language="fr",
        count=args.count,
        include_remix=args.remix,
        draft_mode=args.draft,
    )

    try:
        response = await orchestrator.generate(request)
    except Exception as exc:  # noqa: BLE001
        print("Generation failed:")
        print(repr(exc))
        print("")
        print("Tip: run `python -m backend.cli doctor` and ensure at least one provider is OK.")
        return 3

    providers = sorted(set(t.provider_used for t in response.all_candidates))

    print("")
    print("== Editorial Agent (AUTO) ==")
    print(f"Providers: {', '.join(providers)}")
    print(f"Trend: {trend.title}")
    print("")

    for idx, tweet in enumerate(response.top3, start=1):
        print(f"#{idx} score={tweet.score} style={tweet.style} angle={tweet.angle} provider={tweet.provider_used}")
        print(tweet.text)
        print("")

    payload = {
        "generated_at": now_ts(),
        "trend": trend.model_dump(),
        "top3": [t.model_dump() for t in response.top3],
        "all_candidates": [t.model_dump() for t in response.all_candidates[: min(len(response.all_candidates), 30)]],
        "memory": response.metadata.get("memory_stats", {}),
        "settings": {
            "llm_provider": SETTINGS.llm.primary_provider,
            "ollama_model": SETTINGS.ollama.model,
        },
    }

    out = Path(args.out)
    _write_json(out, payload)
    print(f"Saved: {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="editorial-agent")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="Check LLM providers")

    run = sub.add_parser("run", help="Fetch trends and generate top tweets")
    run.add_argument("--trends", type=int, default=10)
    run.add_argument("--count", type=int, default=12)
    run.add_argument("--theme", type=str, default="")
    run.add_argument("--style", type=str, default="insight")
    run.add_argument("--remix", action="store_true")
    run.add_argument("--draft", action="store_true")
    run.add_argument("--out", type=str, default="backend/data/latest_run.json")

    args = parser.parse_args()

    import asyncio

    if args.cmd == "doctor":
        return asyncio.run(doctor())

    if args.cmd == "run":
        return asyncio.run(run_once(args))

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
