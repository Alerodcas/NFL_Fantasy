"""
Shared media utilities for downloading images and generating thumbnails.

This centralizes logic used by different modules (e.g., teams, fantasy_teams)
to avoid duplication and keep thumbnail behavior consistent.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple, Union
from datetime import datetime

import requests
from PIL import Image

# Resolve backend/src directory from this file (backend/src/core/media.py)
BASE_DIR = Path(__file__).resolve().parents[1]
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

THUMB_SIZE: Tuple[int, int] = (256, 256)


def public_url(fs_path: Path) -> str:
    """Return a URL path like /media/<relative_path> for a file stored under MEDIA_ROOT."""
    rel = fs_path.relative_to(MEDIA_ROOT).as_posix()
    return f"/media/{rel}"


def ensure_subdir(subdir: str) -> Path:
    """Ensure MEDIA_ROOT/subdir exists and return its Path."""
    d = MEDIA_ROOT / subdir
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_thumb_from_path(image_path: Path) -> Path:
    """Generate a centered thumbnail PNG from an existing image file and return the thumb path."""
    thumb_path = image_path.with_name(image_path.stem + "_thumb.png")
    with Image.open(image_path) as im:
        im = im.convert("RGB")
        im.thumbnail(THUMB_SIZE, Image.LANCZOS)
        canvas = Image.new("RGB", THUMB_SIZE, (255, 255, 255))
        x = (THUMB_SIZE[0] - im.width) // 2
        y = (THUMB_SIZE[1] - im.height) // 2
        canvas.paste(im, (x, y))
        canvas.save(thumb_path, format="PNG")
    return thumb_path


def try_download_and_thumb(image_url: str, subdir: str) -> Optional[str]:
    """
    Download an image from 'image_url' into MEDIA_ROOT/subdir, generate a 256x256
    centered thumbnail PNG next to it, and return the public URL to the thumbnail.
    If anything fails (network, invalid image), return None.
    """
    try:
        target_dir = ensure_subdir(subdir)
        uid = uuid.uuid4().hex
        ext = os.path.splitext(image_url)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
            ext = ".png"
        image_path = target_dir / f"{uid}{ext}"

        r = requests.get(image_url, timeout=10)
        r.raise_for_status()
        with open(image_path, "wb") as f:
            f.write(r.content)

        thumb_path = make_thumb_from_path(image_path)
        return public_url(thumb_path)
    except Exception:
        return None


def save_upload_file(upload_file, subdir: str) -> Tuple[str, str]:
    """Save an uploaded file (FastAPI UploadFile-like) into MEDIA_ROOT/subdir,
    generate a thumbnail, and return (public_image_url, public_thumb_url).

    This centralizes saving uploaded files so routers and services don't handle filesystem I/O.
    """
    target_dir = ensure_subdir(subdir)
    ext = os.path.splitext(upload_file.filename or "")[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        ext = ".png"

    uid = uuid.uuid4().hex
    image_path = target_dir / f"{uid}{ext}"

    # Read and write bytes
    with open(image_path, "wb") as f:
        content = upload_file.file.read()
        f.write(content)
    try:
        upload_file.file.seek(0)
    except Exception:
        pass

    thumb_path = make_thumb_from_path(image_path)
    return public_url(image_path), public_url(thumb_path)


def save_processed_copy(content: Union[bytes, str], subdir: str, prefix: str = "batch") -> Path:
    """Save a processed copy (e.g. uploaded JSON) into MEDIA_ROOT/subdir with a timestamped filename.

    Returns the Path to the written file. Does not raise on errors; any exception will propagate.
    """
    target_dir = ensure_subdir(subdir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    fname = f"{prefix}__{ts}.json"
    out_path = target_dir / fname

    # Write bytes or string
    with open(out_path, "wb") as pf:
        if isinstance(content, bytes):
            pf.write(content)
        else:
            pf.write(str(content).encode("utf-8"))

    return out_path
