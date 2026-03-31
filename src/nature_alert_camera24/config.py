from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("NATURE_ALERT_CAMERA24_DATABASE_URL", "sqlite:///./nature_alert_camera24.db")
    smtp_server: str = os.getenv("NATURE_ALERT_CAMERA24_SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("NATURE_ALERT_CAMERA24_SMTP_PORT", "465"))
    email_address: str | None = os.getenv("NATURE_ALERT_CAMERA24_EMAIL_ADDRESS")
    email_password: str | None = os.getenv("NATURE_ALERT_CAMERA24_EMAIL_PASSWORD")
    email_default_recipient: str | None = os.getenv("NATURE_ALERT_CAMERA24_DEFAULT_RECIPIENT")
    server_host: str = os.getenv("NATURE_ALERT_CAMERA24_SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("NATURE_ALERT_CAMERA24_SERVER_PORT", "8000"))
    upload_url: str = os.getenv("NATURE_ALERT_CAMERA24_UPLOAD_URL", "http://127.0.0.1:8000/upload/")
    detection_interval_seconds: float = float(os.getenv("NATURE_ALERT_CAMERA24_DETECTION_INTERVAL", "5"))
    custom_model_path: str = os.getenv("NATURE_ALERT_CAMERA24_CUSTOM_MODEL_PATH", "datasets/wages/best.pt")
    fallback_model_path: str = os.getenv("NATURE_ALERT_CAMERA24_FALLBACK_MODEL_PATH", "yolov8n.pt")


settings = Settings()


