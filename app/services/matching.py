"""Resume-job matching engine (FR-06), skill gap (FR-07) and explanations (FR-09).

Owner: Anirudh N (PES1UG24AM041)
Implements SAD 4.2 exactly:
    score = 100 x (0.75 x skill_overlap + 0.25 x keyword_similarity), clamped to [0, 100]
    skill_overlap = matched_required_skills / number_of_required_skills
    keyword_similarity = cosine similarity of resume text and job title + description
Fallback when a job has no required skills: score = 100 x keyword_similarity.
"""
import math
import re
from collections import Counter

from app.services.skills import normalize_skill

SKILL_WEIGHT, KEYWORD_WEIGHT = 0.75, 0.25
TOKEN = re.compile(r"[a-z0-9+#.]+")
STOPWORDS = {"and", "the", "a", "an", "of", "to", "in", "for", "with", "on", "is", "are", "we", "you",
             "our", "your", "using", "role", "work", "will", "be", "as", "at", "by", "or"}


def _vector(text: str) -> Counter:
    return Counter(t for t in TOKEN.findall((text or "").lower()) if t not in STOPWORDS)


def cosine_similarity(a: str, b: str) -> float:
    va, vb = _vector(a), _vector(b)
    dot = sum(va[t] * vb[t] for t in va.keys() & vb.keys())
    norm = math.sqrt(sum(v * v for v in va.values())) * math.sqrt(sum(v * v for v in vb.values()))
    return 0.0 if norm == 0 else dot / norm


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def build_explanation(matched: list[str], missing: list[str], has_required: bool) -> list[str]:
    """FR-09: every sentence is backed by the job's requirements or the parsed resume."""
    lines = []
    if matched:
        lines.append(f"Your resume lists {_join(matched)}, which this job requires.")
    if missing:
        verb = "is" if len(missing) == 1 else "are"
        lines.append(f"{_join(missing)} {verb} required but not found in your parsed resume.")
    if not has_required:
        lines.append("This job lists no required skills, so the score uses text similarity only.")
    return lines


def compute_match(profile: dict, job) -> dict:
    resume_skills = {normalize_skill(s) for s in (profile.get("skills") or [])}
    required = list(dict.fromkeys(normalize_skill(s) for s in (job.required_skills or [])))
    matched = [s for s in required if s in resume_skills]
    missing = [s for s in required if s not in resume_skills]
    keyword = cosine_similarity(profile.get("raw_text", ""), f"{job.title} {job.description}")
    if required:
        overlap = len(matched) / len(required)
        score = 100 * (SKILL_WEIGHT * overlap + KEYWORD_WEIGHT * keyword)
    else:
        overlap = 0.0
        score = 100 * keyword            # documented fallback, no division by zero
    return {
        "job_id": job.id,
        "score": round(max(0.0, min(100.0, score)), 1),
        "matched_skills": matched,
        "missing_skills": missing,
        "components": {"skill_overlap": round(overlap, 2), "keyword_similarity": round(keyword, 2)},
        "explanation": build_explanation(matched, missing, bool(required)),
    }
