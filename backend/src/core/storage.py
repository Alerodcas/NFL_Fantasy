from typing import Iterable
from sqlalchemy.orm import Session


def commit_and_refresh(db: Session, *objs: Iterable[object]) -> None:
    """Commit the current transaction and refresh the provided objects from the DB.

    On error, performs a rollback and re-raises the exception.
    """
    try:
        db.commit()
        for o in objs:
            try:
                db.refresh(o)
            except Exception:
                # Don't fail the whole commit if refresh fails for an object
                pass
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        raise


def commit(db: Session) -> None:
    """Commit the current transaction; on error rollback and re-raise."""
    try:
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        raise


def rollback(db: Session) -> None:
    """Rollback the current transaction (best-effort)."""
    try:
        db.rollback()
    except Exception:
        pass
