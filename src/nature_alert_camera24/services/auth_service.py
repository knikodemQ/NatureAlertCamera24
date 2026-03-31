from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from nature_alert_camera24.models import User
from nature_alert_camera24.security import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def register(self, username: str, email: str, password: str) -> tuple[bool, str]:
        exists = self._db.query(User).filter(or_(User.username == username, User.email == email)).first()
        if exists:
            return False, "User with this username or email already exists."

        user = User(username=username, email=email, password_hash=hash_password(password))
        self._db.add(user)
        self._db.commit()
        return True, "Registration completed."

    def login(self, username: str, password: str) -> tuple[bool, int | str]:
        user = self._db.query(User).filter(User.username == username).first()
        if not user:
            return False, "Invalid credentials."
        if not verify_password(password, user.password_hash):
            return False, "Invalid credentials."
        return True, user.id


