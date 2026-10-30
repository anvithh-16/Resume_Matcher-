"""FR-07 skill normalizer tests. Owner: Anirudh N."""
from app.services.skills import SKILL_ALIASES, extract_skills, normalize_skill


def test_normalize_aliases_and_case():
    assert normalize_skill("  Python3 ") == "python"
    assert normalize_skill("PostgreSQL") == "sql"
    assert normalize_skill("React.js") == "react"
    assert normalize_skill("Rust") == "rust"          # unknown skills pass through, lower-cased


def test_extract_whole_words_only():
    text = "Skills: Python, MySQL, React.js, C++, Machine Learning. Excellent communication skills. JavaScript"
    found = set(extract_skills(text))
    assert {"python", "sql", "react", "c++", "machine learning", "communication", "javascript"} <= found
    assert "java" not in found and "excel" not in found


def test_extract_from_team_fixture_resume():
    text = ("Skills\nPython, SQL, FastAPI, Git, Machine Learning, Docker\n"
            "Software Engineering Intern, Demo Labs: built REST APIs in Python\n"
            "Resume matcher using FastAPI and SQLite")
    found = set(extract_skills(text))
    assert {"python", "sql", "fastapi", "git", "machine learning", "docker", "rest api"} <= found


def test_extract_empty_text():
    assert extract_skills("") == [] and extract_skills(None) == []


def test_canonical_names_are_their_own_canon():
    for canon in SKILL_ALIASES:
        assert normalize_skill(canon) == canon
