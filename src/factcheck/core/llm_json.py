"""
Robust JSON LLM invocation with retries, repair attempts, and fallback.
"""

import json
import logging
import re
from typing import Any, TypeVar, cast

from openai import APIConnectionError, APITimeoutError, RateLimitError
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from factcheck.core.llm import get_client

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


@retry(
    retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIConnectionError)),
    wait=wait_exponential(multiplier=2, max=30),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _chat(messages: list[dict[str, Any]], temperature: float) -> str:
    client, model = get_client()
    r = client.chat.completions.create(
        model=model, messages=cast(Any, messages), temperature=temperature, timeout=30
    )
    return r.choices[0].message.content or ""


def _extract_json(text: str) -> Any:
    text = re.sub(r"```(?:json)?", "", text).strip()
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    ends = [i for i in (text.rfind("}"), text.rfind("]")) if i != -1]
    if not starts or not ends:
        raise ValueError("no JSON found in response")
    return json.loads(text[min(starts) : max(ends) + 1])


def call_json(
    schema: type[T],
    system: str,
    user: str,
    *,
    fallback: T | None = None,
    list_key: str | None = None,  # wrap a bare JSON array: {"questions": [...]}
    temperature: float = 0.0,
    max_repairs: int = 1,
) -> T:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    last_err: Exception | None = None

    for attempt in range(max_repairs + 1):
        try:
            raw = _chat(messages, temperature)
        except Exception as e:  # API still failing after backoff
            log.error("llm_call_failed", extra={"error": str(e)})
            last_err = e
            break
        try:
            data = _extract_json(raw)
            if list_key and isinstance(data, list):
                data = {list_key: data}
            return schema.model_validate(data)
        except (ValueError, ValidationError) as e:
            last_err = e
            log.warning("invalid_llm_output", extra={"attempt": attempt, "error": str(e)})
            messages += [
                {"role": "assistant", "content": raw},
                {
                    "role": "user",
                    "content": (
                        f"Your output was invalid: {e}. Reply again with ONLY valid JSON "
                        f"matching the required schema, with no extra text."
                    ),
                },
            ]

    if fallback is not None:
        log.error("using_fallback", extra={"schema": schema.__name__, "error": str(last_err)})
        return fallback
    raise RuntimeError(f"{schema.__name__}: failed after retries: {last_err}")
