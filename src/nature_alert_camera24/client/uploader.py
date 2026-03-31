from __future__ import annotations

import os

import requests

from nature_alert_camera24.config import settings


class UploaderClient:
    def __init__(self, upload_url: str | None = None) -> None:
        self._url = upload_url or settings.upload_url

    def send_image_bytes(self, image_bytes: bytes, filename: str, label: str, confidence: str) -> requests.Response:
        files = {"file": (filename, image_bytes, "image/jpeg")}
        data = {"label": label, "confidence": confidence}
        return requests.post(self._url, files=files, data=data, timeout=20)

    def send_image_file(self, image_path: str, label: str, confidence: str = "1.00") -> requests.Response:
        with open(image_path, "rb") as file:
            image_bytes = file.read()
        return self.send_image_bytes(image_bytes, os.path.basename(image_path), label, confidence)


