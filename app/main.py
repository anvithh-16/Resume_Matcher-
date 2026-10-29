import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import APP_ENV, BASE_DIR
from app.core.errors import register_error_handlers
from app.db.database import SessionLocal, init_db
from app.routers import (admin, applications, auth, bookmarks, consent, jobs, matches,
                         recommendations, resumes)
from app.services.job_service import seed_if_empty

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield

PROD = APP_ENV == "production"
app = FastAPI(title="Resume Matcher", version="1.0", lifespan=lifespan,
              docs_url=None if PROD else "/docs", redoc_url=None,
              openapi_url=None if PROD else "/openapi.json")
register_error_handlers(app)

for module in (auth, resumes, jobs, matches, recommendations, bookmarks, applications, consent, admin):
    app.include_router(module.router, prefix="/api/v1")

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

app.mount("/", StaticFiles(directory=BASE_DIR / "app" / "static", html=True), name="static")
