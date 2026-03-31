from __future__ import annotations

from fastapi import Depends, FastAPI, File, Form, UploadFile
from sqlalchemy.orm import Session

from nature_alert_camera24.api.dependencies import get_db
from nature_alert_camera24.db import init_db
from nature_alert_camera24.services.detection_service import DetectionService


init_db()
app = FastAPI(title="NatureAlertCamera24 API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload/")
async def upload_detection(
    label: str = Form(...),
    confidence: str = Form("0.0"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    image_data = await file.read()
    service = DetectionService(db)

    detection = service.create_detection(label=label, confidence=confidence, image_data=image_data)
    service.notify_detection(detection)

    return {"message": "Detection saved"}


