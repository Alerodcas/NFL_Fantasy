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
    seen_items: List[dict] = []

    for idx, item in enumerate(data, start=1):
        # Basic shape checks
        item_errors: List[str] = []

        if "name" not in item or not isinstance(item["name"], str) or not item["name"].strip():
            item_errors.append(f"Row {idx}: missing field 'name'")
        name = item.get("name", "").strip()

        pos = item.get("position")
        if not pos or not isinstance(pos, str) or not pos.strip():
            item_errors.append(f"Row {idx}: missing field 'position'")
        else:
            pos_up = pos.strip().upper()
            if pos_up not in ALLOWED_POSITIONS:
                allowed = ", ".join(sorted(ALLOWED_POSITIONS))
                item_errors.append(f"Row {idx}: invalid position '{pos}'. Allowed values: {allowed}")

        if "team" not in item or not isinstance(item.get("team"), str) or not item["team"].strip():
            item_errors.append(f"Row {idx}: missing field 'team'")
        team = item.get("team", "").strip()

        if "image" not in item or not item["image"]:
            item_errors.append(f"Row {idx}: missing field 'image'")

        # Duplicate checks within file
        if not item_errors:
            for prev in seen_items:
                if prev["name"].lower() == name.lower() and prev["team"].lower() == team.lower():
                    item_errors.append(f"Row {idx}: player '{name}' is duplicated inside the file for team '{team}'")
                    break
                if item.get("id") and prev.get("id") and item["id"] == prev["id"]:
                    item_errors.append(f"Row {idx}: ID '{item['id']}' is duplicated inside the file")
                    break

        # DB validations
        team_obj = get_by_name_ci(db, team) if team else None
        team_id = team_obj.id if team_obj else None

        if not item_errors:
            # Name length
            if len(name) < 2:
                item_errors.append(f"Row {idx}: Name must be at least 2 characters.")

            if not team_id:
                item_errors.append(f"Row {idx}: Team not found.")

            # Uniqueness in DB
            if team_id:
                existing = get_by_name_ci_for_team(db, team_id=team_id, name=name)
                if existing:
                    item_errors.append(f"Row {idx}: Jugador con ese nombre ya existe en este equipo.")

            if not item.get("image"):
                item_errors.append(f"Row {idx}: Image is required.")

        if item_errors:
            errors.extend(item_errors)
            continue

        seen_items.append({"name": name, "team": team, "id": item.get("id")})
        validated_items.append({
            "name": name,
            "position": pos_up,
            "team_id": team_id,
            "image_url": item.get("image")
        })

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(errors))

    return validated_items


def validate_single_player(db: Session, payload: dict, uploaded_file: Optional[object] = None) -> dict:
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
        # Verify team exists
        from ..teams.repository import get_by_id as _get_team_by_id
        team = _get_team_by_id(db, team_id)
        if not team:
            errors.append("Team not found.")
        else:
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
