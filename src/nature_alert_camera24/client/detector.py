from __future__ import annotations

import threading
import time

import cv2
from ultralytics import YOLO

from nature_alert_camera24.config import settings
from nature_alert_camera24.client.uploader import UploaderClient


CLASS_NAMES = {
    0: "buffalo",
    1: "elephant",
    2: "rhino",
    3: "zebra",
    4: "giraffe",
    5: "lion",
    6: "hippo",
    7: "antelope",
    8: "person",
}


class LiveDetector:
    def __init__(self, uploader: UploaderClient | None = None) -> None:
        self._uploader = uploader or UploaderClient()
        self._custom_model = YOLO(settings.custom_model_path)
        self._fallback_model = YOLO(settings.fallback_model_path)

    def _send_async(self, image_data: bytes, label: str, confidence: str) -> None:
        thread = threading.Thread(
            target=self._uploader.send_image_bytes,
            args=(image_data, "detected_image.jpg", label, confidence),
            daemon=True,
        )
        thread.start()

    def run_camera_loop(self) -> None:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            raise RuntimeError("Could not open camera.")

        last_detection_time = 0.0

        while True:
            success, frame = camera.read()
            if not success:
                break

            frame_to_show = frame.copy()
            now = time.time()

            if now - last_detection_time >= settings.detection_interval_seconds:
                last_detection_time = now
                custom_results = self._custom_model(frame)
                fallback_results = self._fallback_model(frame)

                custom_boxes = custom_results[0].boxes if custom_results and custom_results[0].boxes else []
                fallback_boxes = fallback_results[0].boxes if fallback_results and fallback_results[0].boxes else []

                skip_frame = any(
                    self._fallback_model.model.names.get(int(box.cls[0]), "unknown").lower() == "teddy bear"
                    for box in fallback_boxes
                )

                if not skip_frame:
                    labels: list[str] = []
                    confidences: list[str] = []

                    for box in custom_boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])

                        if class_id == 8 and confidence < 0.8:
                            continue
                        if confidence < 0.6:
                            continue

                        label = CLASS_NAMES.get(class_id, "unknown")
                        labels.append(label)
                        confidences.append(f"{confidence:.2f}")

                        cv2.rectangle(frame_to_show, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            frame_to_show,
                            f"{label} ({confidence:.2f})",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2,
                        )

                    if labels:
                        ok, encoded = cv2.imencode(".jpg", frame_to_show)
                        if ok:
                            self._send_async(
                                image_data=encoded.tobytes(),
                                label=",".join(labels),
                                confidence=",".join(confidences),
                            )

            cv2.imshow("NatureAlertCamera24 Detection", frame_to_show)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        camera.release()
        cv2.destroyAllWindows()


