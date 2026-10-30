"""Skill normalization and extraction (FR-07).

Owner: Anirudh N (PES1UG24AM041)
Ankitha's job data and parser use ONLY the canonical names (the keys of SKILL_ALIASES).
"""
import re

# Canonical skill -> aliases that mean the same thing.
SKILL_ALIASES: dict[str, list[str]] = {
    "python": ["python3"],
    "java": [],
    "javascript": ["ecmascript"],
    "typescript": [],
    "c++": ["cpp"],
    "sql": ["mysql", "postgresql", "postgres", "sqlite", "t-sql"],
    "fastapi": ["fast api"],
    "django": [],
    "flask": [],
    "react": ["reactjs", "react.js"],
    "node.js": ["nodejs", "node"],
    "html": ["html5"],
    "css": ["css3"],
    "git": ["github", "gitlab"],
    "docker": [],
    "kubernetes": ["k8s"],
    "aws": ["amazon web services"],
    "azure": [],
    "linux": [],
    "machine learning": ["ml"],
    "deep learning": [],
    "nlp": ["natural language processing"],
    "pandas": [],
    "numpy": [],
    "tensorflow": [],
    "pytorch": ["torch"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "data analysis": ["data analytics"],
    "rest api": ["rest apis", "restful", "restful api"],
    "mongodb": ["mongo"],
    "excel": ["ms excel", "microsoft excel"],
    "tableau": [],
    "power bi": ["powerbi"],
    "spring": ["spring boot"],
    "communication": ["communication skills"],
}

_ALIAS_TO_CANON = {term: canon for canon, aliases in SKILL_ALIASES.items() for term in [canon, *aliases]}

# Longest terms first. A term only matches as a whole word, so "java" never matches "javascript"
# and "excel" never matches "excellent".
_PATTERNS = [(re.compile(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])"), _ALIAS_TO_CANON[t])
             for t in sorted(_ALIAS_TO_CANON, key=len, reverse=True)]


def normalize_skill(name: str) -> str:
    """'  Python3 ' -> 'python'; unknown skills are returned lower-cased."""
    cleaned = re.sub(r"\s+", " ", (name or "").strip().lower())
    return _ALIAS_TO_CANON.get(cleaned, cleaned)


def extract_skills(text: str) -> list[str]:
    """Return the sorted canonical skills found in free text (never invents skills)."""
    low = re.sub(r"\s+", " ", (text or "").lower())
    return sorted({canon for pattern, canon in _PATTERNS if pattern.search(low)})
