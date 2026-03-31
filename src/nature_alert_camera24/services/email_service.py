from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage

from nature_alert_camera24.config import settings


class EmailService:
    def __init__(self) -> None:
        self._address = settings.email_address
        self._password = settings.email_password
        self._smtp_server = settings.smtp_server
        self._smtp_port = settings.smtp_port

    def is_configured(self) -> bool:
        return bool(self._address and self._password)

    def send_detection_email(
        self,
        subject: str,
        body: dict[str, str] | str,
        recipient: str,
        image_bytes: bytes | None = None,
        image_filename: str = "detection.jpg",
    ) -> bool:
        if not self.is_configured():
            return False

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self._address
        msg["To"] = recipient

        if isinstance(body, dict):
            plain_body = json.dumps(body, indent=2)
            label = body.get("label", "unknown")
            confidence = body.get("confidence", "n/a")
            timestamp = body.get("timestamp", "n/a")
        else:
            plain_body = body
            label = "unknown"
            confidence = "n/a"
            timestamp = "n/a"

        msg.set_content(plain_body)

        html = f"""
        <html>
            <body>
                <h3>Detection report</h3>
                <ul>
                    <li><b>Label:</b> {label}</li>
                    <li><b>Confidence:</b> {confidence}</li>
                    <li><b>Timestamp:</b> {timestamp}</li>
                </ul>
            </body>
        </html>
        """
        msg.add_alternative(html, subtype="html")

        if image_bytes:
            msg.add_attachment(
                image_bytes,
                maintype="image",
                subtype="jpeg",
                filename=image_filename,
            )

        try:
            with smtplib.SMTP_SSL(self._smtp_server, self._smtp_port) as smtp:
                smtp.login(self._address, self._password)
                smtp.send_message(msg)
            return True
        except Exception:
            return False


