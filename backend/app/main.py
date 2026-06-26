from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import groups, payments, reports, students, ui, webhooks_artpay
from app.config import get_settings
from app.db import SessionLocal, create_db_and_tables
from app.migrations import run_migrations
from app.services.default_groups import ensure_default_groups

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    run_migrations()
    db = SessionLocal()
    try:
        ensure_default_groups(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(groups.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(webhooks_artpay.router, prefix="/api")
app.include_router(ui.router)
