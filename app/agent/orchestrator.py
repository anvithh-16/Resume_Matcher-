"""Bounded agent workflow for job recommendations (FR-08, SRS UC-05). Owner: Anirudh N.

Fixed policy: get profile -> search jobs -> score -> rank -> (optional, consented) polish.
Resume and job text are passed only as data into the matching engine, so prompt injection
inside a resume cannot change which tools run.
"""
from app.agent import provider
from app.agent.tools import AgentContext, ToolError, call_tool
from app.core.errors import AppError

PLAN = ["get_resume_profile", "search_jobs", "score_jobs", "rank_results"]


def _result(ctx, recs, guidance=None, external_calls=0):
    return {"recommendations": recs, "guidance": guidance, "tool_trace": ctx.trace,
            "external_calls": external_calls,
            "note": "Recommendations only. Nothing is submitted or sent anywhere on your behalf."}


def recommend(db, user, resume_id: int, location: str | None = None, top_k: int = 5, consent: bool = False):
    ctx = AgentContext(db=db, user=user)
    try:
        profile = call_tool("get_resume_profile", {"resume_id": resume_id}, ctx)
        skills = profile.get("skills") or []
        if not skills:
            return _result(ctx, [], "No skills were found in this resume. "
                                    "Correct the parsed profile or upload a fuller resume.")
        job_ids = call_tool("search_jobs", {"skills": skills[:50], "location": location, "limit": 50}, ctx)
        if not job_ids:
            return _result(ctx, [], "No jobs match your skills yet. Try removing the location filter.")
        scored = call_tool("score_jobs", {"resume_id": resume_id, "job_ids": job_ids}, ctx)
        ranked = call_tool("rank_results", {"results": scored, "top_k": top_k}, ctx)
    except ToolError as exc:
        raise AppError(400, exc.code, "The recommendation request could not be completed.")
    ranked, calls = provider.maybe_polish(ranked, consent)
    return _result(ctx, ranked, None, calls)
