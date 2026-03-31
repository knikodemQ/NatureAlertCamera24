from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from nature_alert_camera24.config import settings
from nature_alert_camera24.models import Detection
from nature_alert_camera24.services.email_service import EmailService


class DetectionService:
    def __init__(self, db: Session, email_service: EmailService | None = None) -> None:
        self._db = db
        self._email_service = email_service or EmailService()

    def create_detection(self, label: str, confidence: str, image_data: bytes) -> Detection:
        detection = Detection(
            label=label,
            confidence=confidence,
            timestamp=datetime.now(),
            image_data=image_data,
        )
        self._db.add(detection)
        self._db.commit()
        self._db.refresh(detection)
        return detection

    def notify_detection(self, detection: Detection, recipient: str | None = None) -> bool:
        effective_recipient = recipient or settings.email_default_recipient
        if not effective_recipient:
            return False

        subject = f"Detection: {detection.label}"
        body = {
            "label": detection.label,
            "confidence": detection.confidence,
            "timestamp": detection.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return self._email_service.send_detection_email(
            subject=subject,
            body=body,
            recipient=effective_recipient,
            image_bytes=detection.image_data,
        )

    def latest_detection(self) -> Detection | None:
        return self._db.query(Detection).order_by(Detection.timestamp.desc()).first()

    def list_recent(self, limit: int = 20) -> list[Detection]:
        return self._db.query(Detection).order_by(Detection.timestamp.desc()).limit(limit).all()


