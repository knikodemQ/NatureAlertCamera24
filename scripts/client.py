from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nature_alert_camera24.client.uploader import UploaderClient  # noqa: E402


def send_static_samples() -> None:
    client = UploaderClient()
    samples = [
        (ROOT_DIR / "zubr.jpg", "bison", "1.00"),
        (ROOT_DIR / "zubry.jpg", "bisons", "1.00"),
    ]
    for image_path, label, confidence in samples:
        response = client.send_image_file(image_path=str(image_path), label=label, confidence=confidence)
        print(response.text)
        time.sleep(2)


def send_camera_snapshot() -> None:
    client = UploaderClient()
    camera = cv2.VideoCapture(0)
    ok, frame = camera.read()
    camera.release()

    if not ok:
        print("Camera frame not available.")
        return

    ok, encoded = cv2.imencode(".jpg", frame)
    if not ok:
        print("Could not encode camera frame.")
        return

    response = client.send_image_bytes(
        image_bytes=encoded.tobytes(),
        filename="camera.jpg",
        label="camera_object",
        confidence="1.00",
    )
    print(response.text)


if __name__ == "__main__":
    mode = input("Choose mode (static/camera): ").strip().lower()
    if mode == "static":
        send_static_samples()
    elif mode == "camera":
        send_camera_snapshot()
    else:
        print("Unknown mode. Use 'static' or 'camera'.")


