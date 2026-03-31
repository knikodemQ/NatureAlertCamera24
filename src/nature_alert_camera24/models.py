from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, LargeBinary, String

from nature_alert_camera24.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    confidence = Column(String, nullable=False)


