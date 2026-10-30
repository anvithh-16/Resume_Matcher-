"""Allowlisted agent tools (SR-05). Owner: Anirudh N.

The agent can ONLY run the four functions registered here. Arguments are schema-validated;
unknown tools or bad arguments are refused and audited. Tool outputs and resume/job text are
treated as data, never as instructions.
"""
from dataclasses import dataclass, field
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.security import get_owned_or_404
from app.db.models import Job, Resume, User
from app.services.job_service import search_jobs
from app.services.matching import compute_match


class ToolError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class AgentContext:
    db: Session
    user: User
    trace: list = field(default_factory=list)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")     # unknown arguments are rejected


class ProfileArgs(Strict):
    resume_id: int


class SearchArgs(Strict):
    skills: list[str] = Field(max_length=50)
    location: str | None = Field(default=None, max_length=100)
    limit: int = Field(default=50, ge=1, le=100)


class ScoreArgs(Strict):
    resume_id: int
    job_ids: list[int] = Field(max_length=100)


class RankArgs(Strict):
    results: list[dict] = Field(max_length=100)
    top_k: int = Field(default=5, ge=1, le=10)


REGISTRY: dict[str, tuple[type[BaseModel], Callable]] = {}


def tool(name: str, args_model: type[BaseModel]):
    def register(fn):
        REGISTRY[name] = (args_model, fn)
        return fn
    return register


def call_tool(name: str, args, ctx: AgentContext):
    """The ONLY way the agent runs anything. Unknown tools and bad arguments are refused."""
    if name not in REGISTRY:
        audit(ctx.db, "agent_tool_rejected", ctx.user.id, f"unknown tool {str(name)[:40]}")
        raise ToolError("unknown_tool")
    model, fn = REGISTRY[name]
    try:
        if not isinstance(args, dict):
            raise TypeError
        parsed = model(**args)
    except (ValidationError, TypeError):
        audit(ctx.db, "agent_tool_rejected", ctx.user.id, f"invalid arguments for {name}")
        raise ToolError("invalid_arguments")
    ctx.trace.append(name)
    return fn(parsed, ctx)


@tool("get_resume_profile", ProfileArgs)
def _get_profile(a: ProfileArgs, ctx: AgentContext) -> dict:
    return get_owned_or_404(ctx.db, Resume, a.resume_id, ctx.user).parsed_profile or {}


@tool("search_jobs", SearchArgs)
def _search(a: SearchArgs, ctx: AgentContext) -> list[int]:
    return [j.id for j in search_jobs(ctx.db, skills=a.skills, location=a.location, limit=a.limit)]


@tool("score_jobs", ScoreArgs)
def _score(a: ScoreArgs, ctx: AgentContext) -> list[dict]:
    profile = get_owned_or_404(ctx.db, Resume, a.resume_id, ctx.user).parsed_profile or {}
    results = []
    for job_id in a.job_ids:
        job = ctx.db.get(Job, job_id)
        if job is not None and job.active:
            m = compute_match(profile, job)
            m.update({"title": job.title, "company": job.company, "location": job.location})
            results.append(m)
    return results


@tool("rank_results", RankArgs)
def _rank(a: RankArgs, ctx: AgentContext) -> list[dict]:
    return sorted(a.results, key=lambda m: (-m.get("score", 0), m.get("job_id", 0)))[: a.top_k]
