from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from ..teams.repository import get_by_name_ci
from .repository import get_by_name_ci_for_team

ALLOWED_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DST", "FLEX"}


def validate_players_batch(db: Session, data: list) -> List[dict]:
    """Validate a batch of player items (list of dicts).

    Returns a list of validated items with fields: name, position, team_id, image_url.
    Raises ValueError with joined error messages if any validation fails.
    """
    if not isinstance(data, list):
        raise ValueError("JSON must contain an array of players")

    errors: List[str] = []
    validated_items: List[dict] = []
    seen_pairs = set()

    # Cache team lookups to avoid repeated DB calls for the same team name
    team_cache: Dict[str, Any] = {}

    for idx, item in enumerate(data, start=1):
        # Basic shape checks
        item_errors: List[str] = []

        name_raw = item.get("name")
        if not isinstance(name_raw, str) or not name_raw.strip():
            item_errors.append(f"Row {idx}: missing field 'name'")
            name = ""
        else:
            name = name_raw.strip()

        pos = item.get("position")
        if not pos or not isinstance(pos, str) or not pos.strip():
            item_errors.append(f"Row {idx}: missing field 'position'")
            pos_up = ""
        else:
            pos_up = pos.strip().upper()
            if pos_up not in ALLOWED_POSITIONS:
                allowed = ", ".join(sorted(ALLOWED_POSITIONS))
                item_errors.append(f"Row {idx}: invalid position '{pos}'. Allowed values: {allowed}")

        team_name_raw = item.get("team")
        if not isinstance(team_name_raw, str) or not team_name_raw.strip():
            item_errors.append(f"Row {idx}: missing field 'team'")
            team_name = ""
        else:
            team_name = team_name_raw.strip()

        image = item.get("image")
        if not image:
            item_errors.append(f"Row {idx}: missing field 'image'")

        # Duplicate checks within file
        if not item_errors:
            pair_key = (name.lower(), team_name.lower())
            if pair_key in seen_pairs:
                item_errors.append(f"Row {idx}: player '{name}' is duplicated inside the file for team '{team_name}'")
            else:
                seen_pairs.add(pair_key)

        if item_errors:
            errors.extend(item_errors)
            continue

        # Resolve or cache team object
        team_obj = None
        if team_name in team_cache:
            team_obj = team_cache[team_name]
        else:
            team_obj = get_by_name_ci(db, team_name)
            team_cache[team_name] = team_obj

        # Build payload for single-item validator and reuse it (avoid duplicating validation)
        payload = {
            "name": name,
            "position": pos_up,
            "team_id": team_obj.id if team_obj else None,
            "image_url": image,
        }

        try:
            validated = validate_single_player(db=db, payload=payload, uploaded_file=None, team_obj=team_obj)
        except ValueError as ve:
            # Prepend row info
            err_text = str(ve)
            # Ensure messages are per-row for easier debugging
            errors.append(f"Row {idx}: {err_text}")
            continue

        validated_items.append(validated)

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(errors))

    return validated_items


def validate_single_player(db: Session, payload: dict, uploaded_file: Optional[object] = None, team_obj: Optional[Any] = None) -> dict:
    """Validate a single player payload.

    payload should contain: name, position, team_id (int) or team (name str), image_url (optional)
    If uploaded_file is provided, image_url may be None.
    Returns a cleaned dict suitable for creating a Player: name, position, team_id, image_url
    Raises ValueError on validation errors.
    """
    errors: List[str] = []

    name = (payload.get("name") or "").strip()
    if not name:
        errors.append("Name is required")
    elif len(name) < 2:
        errors.append("Name must be at least 2 characters.")

    pos = payload.get("position")
    if not pos or not isinstance(pos, str) or not pos.strip():
        errors.append("Position is required")
    else:
        pos_up = pos.strip().upper()
        if pos_up not in ALLOWED_POSITIONS:
            allowed = ", ".join(sorted(ALLOWED_POSITIONS))
            errors.append(f"Invalid position '{pos}'. Allowed: {allowed}")

    team_id = payload.get("team_id")
    if not team_id:
        errors.append("team_id is required")
    else:
        # Verify team exists (use provided team_obj if available to avoid extra DB lookup)
        if team_obj is None:
            from ..teams.repository import get_by_id as _get_team_by_id
            team = _get_team_by_id(db, team_id)
            if not team:
                errors.append("Team not found.")
        else:
            team = team_obj

        if team:
            # Check uniqueness within the team
            existing = get_by_name_ci_for_team(db, team_id=team_id, name=name)
            if existing:
                errors.append("Jugador con ese nombre ya existe en este equipo.")

    image_url = payload.get("image_url")
    if not image_url and not uploaded_file:
        errors.append("Image is required")

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(errors))

    return {
        "name": name,
        "position": pos_up,
        "team_id": team_id,
        "image_url": image_url,
    }
