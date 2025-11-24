from typing import Tuple
from ...core.media import save_upload_file
from ...config.paths import PATH_PLAYERS


def save_upload(upload_file, subdir: str) -> Tuple[str, str]:
    """Generic save wrapper that stores `upload_file` under `subdir` and returns (image_url, thumb_url)."""
    return save_upload_file(upload_file, subdir)


def save_player_upload(upload_file) -> Tuple[str, str]:
    """Backward-compatible helper for player uploads."""
    return save_upload(upload_file, PATH_PLAYERS)
