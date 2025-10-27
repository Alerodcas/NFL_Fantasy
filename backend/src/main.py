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
from .modules.leagues.routes.season_routes import router as season_router

app.include_router(users_router, tags=["users"])
app.include_router(teams_router, prefix="/teams", tags=["teams"])
app.include_router(leagues_router, tags=["leagues"])
app.include_router(season_router, prefix="/api", tags=["seasons"])


# 422 handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        }
        # Incluir input solo si no es un objeto complejo
        if "input" in error and not isinstance(error["input"], (dict, list)):
            error_dict["input"] = error["input"]
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=422, 
        content={
            "detail": "Error de validación", 
            "errors": errors
        }
    )
