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


def team_name_exists_anywhere(db: Session, team_name: str) -> bool:
    return db.query(team_models.Team.id)\
             .filter(func.lower(team_models.Team.name) == func.lower(team_name))\
             .first() is not None

def create_league_with_commissioner_team(
    db: Session,
    creator_user_id: int,
    payload: schemas.LeagueCreate,
):
    # Validate unique league name at DB-level too (leagues.name unique), but pre-check for nice error
    if name_exists(db, payload.name):
        raise ValueError("A league with that name already exists.")
    
    if team_name_exists_anywhere(db, payload.team_name):
        raise ValueError("A team with that name already exists.")

    # Season
    season = get_current_season(db)
    if not season:
        raise RuntimeError("No current season is set. An administrator must mark one season as current.")

    # Hash league password with the same helper as users
    pwd_hash = security.get_password_hash(payload.password)

    # Prepare league
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
        db.flush()  # get lg.id

        # Commissioner’s team
        team_city = (payload.team_city or "N/A").strip()
        if len(team_city) < 2:   # teams.city CHECK >= 2
            team_city = "N/A"

        commissioner_team = team_models.Team(
            name=payload.team_name.strip(),
            city=team_city,
            created_by=creator_user_id,
            league_id=lg.id,
        )
        db.add(commissioner_team)

        db.commit()
        db.refresh(lg)
        return lg, commissioner_team
    except Exception:
        db.rollback()
        raise
