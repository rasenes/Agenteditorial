from __future__ import annotations

import asyncio
import hashlib
import json
import random
import re
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


async def async_retry(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    retries: int = 2,
    delay: float = 0.4,
    backoff: float = 2.0,
    jitter: float = 0.1,
    **kwargs: Any,
) -> T:
    current_delay = delay
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt >= retries:
                break
            await asyncio.sleep(current_delay + random.uniform(0, jitter))
            current_delay *= backoff
    raise RuntimeError(f"retry exhausted: {last_exc}") from last_exc



def parse_json_loose(text: str) -> Any | None:
    if not text:
        return None
    text = text.strip()

    for candidate in (text, text.removeprefix("```json").removesuffix("```").strip()):
        try:
            return json.loads(candidate)
        except Exception:  # noqa: BLE001
            pass

    first_obj = text.find("{")
    last_obj = text.rfind("}")
    if first_obj >= 0 and last_obj > first_obj:
        try:
            return json.loads(text[first_obj : last_obj + 1])
        except Exception:  # noqa: BLE001
            pass

    first_arr = text.find("[")
    last_arr = text.rfind("]")
    if first_arr >= 0 and last_arr > first_arr:
        try:
            return json.loads(text[first_arr : last_arr + 1])
        except Exception:  # noqa: BLE001
            pass

    return None



def normalize_text(text: str) -> str:
    cleaned = " ".join(text.split())
    return "".join(ch for ch in cleaned if ch.isprintable())



def estimate_tweet_length(text: str) -> int:
    urls = re.findall(r"https?://\S+", text)
    if not urls:
        return len(text)
    raw = len(text)
    return raw - sum(len(url) for url in urls) + (23 * len(urls))



def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))



def short_hash(text: str) -> str:
    return hashlib.sha1(text.strip().lower().encode("utf-8")).hexdigest()[:16]



def jaccard_similarity(a: str, b: str) -> float:
    tokens_a = set(re.findall(r"\w+", a.lower()))
    tokens_b = set(re.findall(r"\w+", b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)



def now_ts() -> float:
    return time.time()
