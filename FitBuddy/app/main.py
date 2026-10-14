from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .database import init_db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    description="Personalized 7-day fitness plans and nutrition/recovery tips using Gemini.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    max_age=60 * 60 * 8,
    same_site="lax",
    https_only=False,  # Set True when deployed behind HTTPS.
)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
app.include_router(router)
