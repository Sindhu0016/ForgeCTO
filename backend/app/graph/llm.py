import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from pydantic import BaseModel

from app.config import get_settings

T = TypeVar("T", bound=BaseModel)


def _resolve_model_name(settings, model: str | None, provider: str, *, tier: str = "planner") -> str:
    if provider == "gemini":
        if model and not model.startswith("gpt-"):
            return model
        if model == settings.heavy_model or tier == "heavy":
            return settings.gemini_heavy_model
        if tier == "docs":
            return settings.gemini_docs_model
        return settings.gemini_planner_model
    return model or settings.planner_model


def get_llm(model: str | None = None, temperature: float = 0.2, *, tier: str = "planner"):
    settings = get_settings()
    provider = settings.active_llm_provider
    # #region agent log
    try:
        import time as _time
        from pathlib import Path as _Path
        _log = _Path(__file__).resolve().parents[2] / "debug-5a40ce.log"
        with _log.open("a", encoding="utf-8") as _f:
            _f.write(
                json.dumps(
                    {
                        "sessionId": "5a40ce",
                        "hypothesisId": "A",
                        "location": "llm.py:get_llm",
                        "message": "provider selected for LLM call",
                        "data": {
                            "provider": provider,
                            "llm_provider_pref": settings.llm_provider,
                            "gemini_configured": settings.gemini_configured,
                            "openai_configured": settings.openai_configured,
                            "gemini_key_len": len(settings.gemini_api_key or ""),
                            "model_requested": model,
                        },
                        "timestamp": int(_time.time() * 1000),
                        "runId": "pre-fix",
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion
    if not provider:
        raise RuntimeError(
            "No LLM configured. Add GEMINI_API_KEY (free) or OPENAI_API_KEY to the "
            "project root .env, then restart the backend."
        )

    # Infer tier from OpenAI model names passed by nodes
    if model == settings.heavy_model:
        tier = "heavy"
    elif model == settings.docs_model:
        tier = "docs"

    model_name = _resolve_model_name(settings, model, provider, tier=tier)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=settings.gemini_api_key,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=settings.openai_api_key,
    )


async def invoke_structured(
    schema: type[T],
    system: str,
    user: str,
    *,
    model: str | None = None,
    timeout: int | None = None,
    retries: int | None = None,
) -> T:
    settings = get_settings()
    timeout = timeout if timeout is not None else settings.node_timeout_seconds
    retries = retries if retries is not None else settings.max_node_retries
    llm = get_llm(model=model).with_structured_output(schema)

    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            result = await asyncio.wait_for(
                llm.ainvoke(
                    [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ]
                ),
                timeout=timeout,
            )
            if isinstance(result, schema):
                return result
            return schema.model_validate(result)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            # #region agent log
            try:
                import time as _time
                from pathlib import Path as _Path
                _log = _Path(__file__).resolve().parents[2] / "debug-5a40ce.log"
                err_s = str(exc)
                with _log.open("a", encoding="utf-8") as _f:
                    _f.write(
                        json.dumps(
                            {
                                "sessionId": "5a40ce",
                                "hypothesisId": "B",
                                "location": "llm.py:invoke_structured",
                                "message": "LLM invoke failed",
                                "data": {
                                    "attempt": attempt,
                                    "provider": settings.active_llm_provider,
                                    "is_quota": "insufficient_quota" in err_s or "429" in err_s,
                                    "error_type": type(exc).__name__,
                                    "error_snip": err_s[:180],
                                },
                                "timestamp": int(_time.time() * 1000),
                                "runId": "pre-fix",
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # #endregion
            if attempt < retries:
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            raise last_err from exc
    raise RuntimeError("unreachable")


def dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump()


def dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, default=str)


ProgressCallback = Callable[[str, str, str, dict | None], Awaitable[None]]
