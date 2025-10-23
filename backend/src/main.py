from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from .config.database import engine
from .modules.users import models as user_models
from .modules.teams import models as team_models
from .modules.leagues.router import router as leagues_router


# Create tables
user_models.Base.metadata.create_all(bind=engine)
team_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- MEDIA: create dir and mount safely
BASE_DIR = Path(__file__).resolve().parent           
MEDIA_DIR = BASE_DIR / "media"                       
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
( MEDIA_DIR / "teams" ).mkdir(parents=True, exist_ok=True)

app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# Routers
from .modules.users.router import router as users_router
from .modules.teams.router import router as teams_router
app.include_router(users_router, tags=["users"])
app.include_router(teams_router, prefix="/teams", tags=["teams"])
app.include_router(leagues_router, prefix="/leagues", tags=["leagues"])


# 422 handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body = await request.body()
        print(f"Raw request body (first 300B): {body[:300]!r}")
    except Exception as e:
        print(f"Error reading body: {e}")
    return JSONResponse(status_code=422, content={"detail": "Error de validación", "errors": exc.errors()})
