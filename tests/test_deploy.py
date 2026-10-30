import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def start_in_production(tmp_path, secret):
    env = {k: v for k, v in os.environ.items() if k != "SECRET_KEY"}
    env.update(APP_ENV="production", PYTHONPATH=str(ROOT), DATABASE_URL=f"sqlite:///{tmp_path}/p.db")
    if secret is not None:
        env["SECRET_KEY"] = secret
    # Run from tmp_path so a developer's local .env cannot supply a key.
    return subprocess.run([sys.executable, "-c", "import app.main"], cwd=tmp_path, env=env,
                          capture_output=True, text=True)

def test_sr07_production_refuses_default_or_example_secret(tmp_path):
    for secret in (None, "change-me-to-a-long-random-string"):
        r = start_in_production(tmp_path, secret)
        assert r.returncode != 0 and "Set a real SECRET_KEY" in r.stderr

def test_sr07_production_starts_with_real_secret_and_hides_docs(tmp_path):
    code = ("from fastapi.testclient import TestClient; from app.main import app; "
            "c = TestClient(app); print(c.get('/docs').status_code, c.get('/openapi.json').status_code)")
    env = {k: v for k, v in os.environ.items()}
    env.update(APP_ENV="production", SECRET_KEY="x" * 40, PYTHONPATH=str(ROOT),
               DATABASE_URL=f"sqlite:///{tmp_path}/p.db")
    r = subprocess.run([sys.executable, "-c", code], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["404", "404"]
