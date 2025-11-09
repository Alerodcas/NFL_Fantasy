from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ....config import auth as security
from ....core.media import try_download_and_thumb
from ...fantasy_teams import repository as ftrepo
from ...fantasy_teams import models as ft_models
from .. import models, schemas

# Default roster & scoring pulled from the user story
DEFAULT_ROSTER = {
    "QB": 1, "RB": 2, "K": 1, "DEF": 1, "WR": 2, "FLEX_RB_WR": 1, "TE": 1, "BENCH": 6, "IR": 3
}
DEFAULT_SCORING = {
    "passing_yards_per_point": 25,
    "passing_td": 4,
    "interception": -2,
    "rushing_yards_per_point": 10,
    "reception": 1,
    "receiving_yards_per_point": 10,
    "rush_recv_td": 6,
    "sack": 1,
    "def_interception": 2,
    "fumble_recovered": 2,
    "safety": 2,
    "any_td": 6,
    "team_def_2pt_return": 2,
    "pat_made": 1,
    "fg_made_0_50": 3,
    "fg_made_50_plus": 5,
    "points_allowed_le_10": 5,
    "points_allowed_le_20": 2,
    "points_allowed_le_30": 0,
    "points_allowed_gt_30": -2,
}


def _get_current_season(db: Session) -> models.Season | None:
    return db.execute(
        select(models.Season).where(models.Season.is_current == True)  # noqa: E712
    ).scalar_one_or_none()


def _league_name_exists(db: Session, league_name: str) -> bool:
    return db.execute(
        select(models.League.id).where(models.League.name == league_name)
    ).scalar_one_or_none() is not None


def create_league_with_commissioner_team(
    db: Session,
    *,
    creator_user_id: int,
    payload: schemas.LeagueCreate,
):
    # Unique league name
    if _league_name_exists(db, payload.name):
        raise ValueError("A league with that name already exists.")

    # Current season
    season = _get_current_season(db)
    if not season:
        raise RuntimeError("No current season is set. An administrator must mark one season as current.")

    ft_payload = payload.fantasy_team

    # Hash password
    pwd_hash = security.get_password_hash(payload.password)

    lg = models.League(
        name=payload.name.strip(),
        description=(payload.description or "").strip() or None,
        max_teams=payload.max_teams,
        password_hash=pwd_hash,
        status="pre_draft",
        allow_decimal_scoring=payload.allow_decimal_scoring,
        playoff_format=payload.playoff_format,
        created_by=creator_user_id,
        season_id=season.id,
        trade_deadline=None,
        max_trades_per_team=None,
        max_free_agents_per_team=None,
        roster_schema=DEFAULT_ROSTER,
        scoring_schema=DEFAULT_SCORING,
    )

    try:
        db.add(lg)
        db.flush()

        # Unique fantasy team name within league (case-insensitive)
        existing_ft = ftrepo.get_by_name_in_league_ci(db, league_id=lg.id, name=ft_payload.name)
        if existing_ft:
            raise ValueError("Ya existe un equipo con ese nombre en esta liga.")

        # Thumbnail if provided
        thumb_url = None
        if getattr(ft_payload, "image_url", None):
            img = str(ft_payload.image_url)
            if img.startswith("/media/"):
                base, _dot, _ext = img.rpartition(".")
                thumb_url = f"{base}_thumb.png"
            else:
                thumb_url = try_download_and_thumb(img, subdir="fantasy_teams")

        fantasy_team = ftrepo.create_fantasy_team(
            db,
            name=ft_payload.name.strip(),
            image_url=str(ft_payload.image_url) if getattr(ft_payload, "image_url", None) else None,
            thumbnail_url=thumb_url,
            user_id=creator_user_id,
            league_id=lg.id,
        )

        member = models.LeagueMember(
            league_id=lg.id,
            user_id=creator_user_id,
            fantasy_team_id=fantasy_team.id,
            user_alias=ft_payload.name.strip(),
        )
        db.add(member)

        db.commit()
        db.refresh(lg)
        return lg, fantasy_team
    except Exception:
        db.rollback()
        raise


def search_leagues(db: Session, filters: schemas.LeagueSearchFilters):
    query = select(models.League).join(models.Season)

    # Status filter
    if filters.status:
        query = query.where(models.League.status == filters.status)
    else:
        query = query.where(models.League.status.in_(["pre_draft", "draft", "in_season"]))

    # Name contains (case-insensitive)
    if filters.name:
        query = query.where(
            func.lower(models.League.name).contains(func.lower(filters.name.strip()))
        )

    # Season filter
    if filters.season_id:
        query = query.where(models.League.season_id == filters.season_id)

    query = query.order_by(models.League.created_at.desc())

    leagues = db.execute(query).scalars().all()

    results = []
    for league in leagues:
        member_count = db.execute(
            select(func.count(models.LeagueMember.id)).where(models.LeagueMember.league_id == league.id)
        ).scalar()

        slots_available = league.max_teams - member_count

        results.append({
            "id": league.id,
            "uuid": str(league.uuid) if league.uuid else None,
            "name": league.name,
            "description": league.description,
            "status": league.status,
            "max_teams": league.max_teams,
            "season_id": league.season_id,
            "season_name": league.season.name,
            "slots_available": slots_available,
            "created_at": league.created_at,
        })

    return results


def join_league(
    db: Session,
    *,
    league_id: int,
    user_id: int,
    payload: schemas.JoinLeagueRequest,
):
    # 1) League exists
    league = db.execute(select(models.League).where(models.League.id == league_id)).scalar_one_or_none()
    if not league:
        raise LookupError("Liga no encontrada.")

    # 2) Not completed
    if league.status == "completed":
        raise ValueError("Esta liga ya ha finalizado y no acepta nuevos miembros.")

    # 3) Password check (generic error)
    if not security.verify_password(payload.password, league.password_hash):
        raise PermissionError("Credenciales inválidas.")

    # 4) Existing membership
    existing_member = db.execute(
        select(models.LeagueMember).where(
            models.LeagueMember.league_id == league_id,
            models.LeagueMember.user_id == user_id,
        )
    ).scalar_one_or_none()
    if existing_member:
        raise ValueError("Ya eres miembro de esta liga.")

    # 5) Capacity
    member_count = db.execute(
        select(func.count(models.LeagueMember.id)).where(models.LeagueMember.league_id == league_id)
    ).scalar()
    if member_count >= league.max_teams:
        raise ValueError("Esta liga no tiene cupos disponibles.")

    # 6) Fantasy team payload
    ft = payload.fantasy_team
    if not ft or not ft.name:
        raise ValueError("Debe proporcionar los datos del equipo de fantasía (nombre).")

    # 7) Unique alias
    alias_exists = db.execute(
        select(models.LeagueMember.id).where(
            models.LeagueMember.league_id == league_id,
            func.lower(models.LeagueMember.user_alias) == func.lower(payload.user_alias.strip()),
        )
    ).scalar_one_or_none()
    if alias_exists:
        raise ValueError(f"El alias '{payload.user_alias}' ya está en uso en esta liga. Por favor elige otro.")

    # 8) Unique team name in league
    if ftrepo.get_by_name_in_league_ci(db, league_id=league_id, name=ft.name):
        raise ValueError(f"Ya existe un equipo con el nombre '{ft.name}' en esta liga. Por favor elige otro.")

    # 9) Create records
    try:
        thumb_url = None
        if getattr(ft, "image_url", None):
            img = str(ft.image_url)
            if img.startswith("/media/"):
                base, _dot, _ext = img.rpartition(".")
                thumb_url = f"{base}_thumb.png"
            else:
                thumb_url = try_download_and_thumb(img, subdir="fantasy_teams")

        fantasy_team = ftrepo.create_fantasy_team(
            db,
            name=ft.name.strip(),
            image_url=str(ft.image_url) if getattr(ft, "image_url", None) else None,
            thumbnail_url=thumb_url,
            user_id=user_id,
            league_id=league_id,
        )

        member = models.LeagueMember(
            league_id=league_id,
            user_id=user_id,
            fantasy_team_id=fantasy_team.id,
            user_alias=payload.user_alias.strip(),
        )
        db.add(member)

        db.commit()
        db.refresh(member)
        return member
    except Exception:
        db.rollback()
        raise
