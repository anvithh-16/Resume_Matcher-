"""Optional external AI provider adapter (FR-13, SR-06). Owner: Anirudh N.

Off by default. Data leaves the system only when the provider is configured
(EXTERNAL_AI_ENABLED=true) AND the user has given consent. Only job title and skill names are
sent - never resume text or contact details. Any failure falls back to the deterministic
explanation.
"""
import logging

from app.core import config        # read config.EXTERNAL_AI_ENABLED at call time (tests can switch it)

log = logging.getLogger("provider")
TIMEOUT_SECONDS = 5


def _call_provider(payload: dict) -> list[str]:
    """Mock provider. A real one must use TIMEOUT_SECONDS and receive only this minimized payload."""
    return [line for line in payload["explanations"]]


def maybe_polish(recs: list[dict], consent: bool) -> tuple[list[dict], int]:
    """Return (recommendations, number_of_external_calls)."""
    if not (config.EXTERNAL_AI_ENABLED and consent):
        return recs, 0
    calls = 0
    for rec in recs:
        payload = {"job_title": rec.get("title", ""), "matched_skills": rec["matched_skills"],
                   "missing_skills": rec["missing_skills"], "explanations": rec["explanation"]}
        calls += 1
        try:
            rec["explanation"] = _call_provider(payload)
        except Exception as exc:                    # timeout or provider error -> deterministic fallback
            log.warning("provider_failed type=%s; using standard explanation", type(exc).__name__)
            rec.setdefault("warnings", []).append("AI explanation unavailable; showing the standard explanation.")
    return recs, calls
