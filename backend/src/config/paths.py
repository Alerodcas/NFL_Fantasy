"""Centralized filesystem path constants for the backend.

Modules should import path names from here instead of using hardcoded strings.
This file intentionally contains only logical path names (relative to the media
directory) and a computed `MEDIA_ROOT` for convenience.
"""
from pathlib import Path

# Resolve backend/src directory (same approach as other modules)
BASE_DIR = Path(__file__).resolve().parents[1]

# Filesystem root for media files (backend/src/media)
MEDIA_ROOT = BASE_DIR / "media"

# Media subdirectories (use these with `ensure_subdir(...)` or join with MEDIA_ROOT)
PATH_PLAYERS = "players"
PATH_PLAYERS_PROCESSED = "players/processed"
PATH_TEAMS = "teams"
PATH_FANTASY_TEAMS = "fantasy_teams"

# Add more path constants here as needed by other modules
