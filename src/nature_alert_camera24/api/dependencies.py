from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from nature_alert_camera24.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


