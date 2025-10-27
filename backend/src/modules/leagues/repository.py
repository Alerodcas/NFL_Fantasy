from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ...config import auth as security
from ..teams import models as team_models
from . import models, schemas

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

def get_current_season(db: Session) -> models.Season | None:
    return db.execute(
        select(models.Season).where(models.Season.is_current == True)  # noqa: E712
    ).scalar_one_or_none()

def name_exists(db: Session, league_name: str) -> bool:
    return db.execute(
        select(models.League.id).where(models.League.name == league_name)
    ).scalar_one_or_none() is not None

def get_team_by_name_case_insensitive(db: Session, team_name: str) -> team_models.Team | None:
    return db.execute(
        select(team_models.Team).where(func.lower(team_models.Team.name) == func.lower(team_name))
    ).scalar_one_or_none()

def create_league_with_commissioner_team(
    db: Session,
    creator_user_id: int,
    payload: schemas.LeagueCreate,
):
    # Validar nombre de liga único
    if name_exists(db, payload.name):
        print("[DEBUG] Liga con ese nombre ya existe")
        raise ValueError("A league with that name already exists.")

    # Temporada actual
    season = get_current_season(db)
    print(f"[DEBUG] Temporada actual: {season}")
    if not season:
        raise RuntimeError("No current season is set. An administrator must mark one season as current.")

    # Buscar equipo por id
    team = db.execute(
        select(team_models.Team).where(team_models.Team.id == payload.team_id)
    ).scalar_one_or_none()
    if not team:
        # evitar filtrar info de existencia vs dueño → 404 genérico
        raise LookupError("Team not found.")
    if team.created_by != creator_user_id:
        # seguridad: no puedes usar equipo ajeno
        raise PermissionError("Solo puedes asignar un equipo propio.")
    print(f"[DEBUG] team.league_id value: {team.league_id!r}, type: {type(team.league_id)}")
    if team.league_id is not None:
        raise ValueError("This team is already assigned to a league.")

    # Hash contraseña de liga
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

    # Transactional create
    try:
        db.add(lg)
        db.flush()  

        # Asignar equipo existente a la liga
        team.league_id = lg.id
        db.add(team)
        
        # Crear el registro de miembro para el comisionado
        member = models.LeagueMember(
            league_id=lg.id,
            user_id=creator_user_id,
            team_id=team.id,
            user_alias=team.name  # El alias inicial es el nombre del equipo
        )
        db.add(member)

        db.commit()
        db.refresh(lg)
        return lg, team
    except Exception:
        db.rollback()
        raise


def search_leagues(db: Session, filters: schemas.LeagueSearchFilters):
    """
    Busca ligas aplicando filtros opcionales de nombre, temporada y estado.
    Solo devuelve ligas activas (pre_draft, draft, in_season).
    """
    query = select(models.League).join(models.Season)
    
    # Filtrar solo ligas activas (no completadas por defecto)
    if filters.status:
        query = query.where(models.League.status == filters.status)
    else:
        # Por defecto, excluir ligas completadas
        query = query.where(models.League.status.in_(["pre_draft", "draft", "in_season"]))
    
    # Filtro de nombre (búsqueda parcial, case-insensitive)
    if filters.name:
        query = query.where(
            func.lower(models.League.name).contains(func.lower(filters.name.strip()))
        )
    
    # Filtro de temporada
    if filters.season_id:
        query = query.where(models.League.season_id == filters.season_id)
    
    query = query.order_by(models.League.created_at.desc())
    
    leagues = db.execute(query).scalars().all()
    
    # Calcular slots disponibles para cada liga
    results = []
    for league in leagues:
        # Contar cuántos miembros tiene la liga
        member_count = db.execute(
            select(func.count(models.LeagueMember.id))
            .where(models.LeagueMember.league_id == league.id)
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
    league_id: int,
    user_id: int,
    payload: schemas.JoinLeagueRequest,
):
    """
    Une un usuario a una liga con las validaciones completas:
    - Liga debe existir y estar activa
    - Contraseña debe ser correcta
    - Debe haber cupos disponibles
    - El usuario no debe estar ya en la liga
    - El equipo debe existir, pertenecer al usuario y no estar asignado
    - El alias y nombre de equipo deben ser únicos en la liga
    """
    
    # 1. Buscar la liga
    league = db.execute(
        select(models.League).where(models.League.id == league_id)
    ).scalar_one_or_none()
    
    if not league:
        raise LookupError("Liga no encontrada.")
    
    # 2. Validar que la liga esté activa (no completada)
    if league.status == "completed":
        raise ValueError("Esta liga ya ha finalizado y no acepta nuevos miembros.")
    
    # 3. Validar contraseña (error genérico por seguridad)
    if not security.verify_password(payload.password, league.password_hash):
        raise PermissionError("Credenciales inválidas.")
    
    # 4. Verificar si el usuario ya está en la liga
    existing_member = db.execute(
        select(models.LeagueMember)
        .where(
            models.LeagueMember.league_id == league_id,
            models.LeagueMember.user_id == user_id
        )
    ).scalar_one_or_none()
    
    if existing_member:
        raise ValueError("Ya eres miembro de esta liga.")
    
    # 5. Contar miembros actuales y validar cupos
    member_count = db.execute(
        select(func.count(models.LeagueMember.id))
        .where(models.LeagueMember.league_id == league_id)
    ).scalar()
    
    if member_count >= league.max_teams:
        raise ValueError("Esta liga no tiene cupos disponibles.")
    
    # 6. Validar el equipo
    team = db.execute(
        select(team_models.Team).where(team_models.Team.id == payload.team_id)
    ).scalar_one_or_none()
    
    if not team:
        raise LookupError("Equipo no encontrado.")
    
    if team.created_by != user_id:
        raise PermissionError("Solo puedes usar tus propios equipos.")
    
    if team.league_id is not None:
        raise ValueError("Este equipo ya está asignado a otra liga.")
    
    # 7. Validar que el alias sea único en la liga
    alias_exists = db.execute(
        select(models.LeagueMember.id)
        .where(
            models.LeagueMember.league_id == league_id,
            func.lower(models.LeagueMember.user_alias) == func.lower(payload.user_alias.strip())
        )
    ).scalar_one_or_none()
    
    if alias_exists:
        raise ValueError(f"El alias '{payload.user_alias}' ya está en uso en esta liga. Por favor elige otro.")
    
    # 8. Validar que el nombre del equipo sea único en la liga
    team_name_exists = db.execute(
        select(team_models.Team.id)
        .where(
            team_models.Team.league_id == league_id,
            func.lower(team_models.Team.name) == func.lower(team.name)
        )
    ).scalar_one_or_none()
    
    if team_name_exists:
        raise ValueError(f"Ya existe un equipo con el nombre '{team.name}' en esta liga. Por favor usa otro equipo o renómbralo.")
    
    # 9. Todo validado, proceder a unirse
    try:
        # Asignar equipo a la liga
        team.league_id = league_id
        db.add(team)
        
        # Crear registro de membresía
        member = models.LeagueMember(
            league_id=league_id,
            user_id=user_id,
            team_id=team.id,
            user_alias=payload.user_alias.strip()
        )
        db.add(member)
        
        db.commit()
        db.refresh(member)
        
        return member
    except Exception:
        db.rollback()
        raise

