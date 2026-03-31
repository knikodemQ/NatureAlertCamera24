from __future__ import annotations

import base64
from collections import Counter
from io import BytesIO

import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image

from nature_alert_camera24.db import SessionLocal, init_db
from nature_alert_camera24.models import Detection
from nature_alert_camera24.services.auth_service import AuthService
from nature_alert_camera24.services.detection_service import DetectionService


init_db()


def _init_session_state() -> None:
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("detection_detail", None)
    st.session_state.setdefault("current_page", 1)


def _render_detection_card(detection: Detection, key_suffix: str) -> None:
    image_b64 = base64.b64encode(detection.image_data).decode()
    st.markdown(
        f"""
        <div style="border:1px solid #d6d6d6;border-radius:10px;padding:10px;margin-bottom:10px;">
            <img src="data:image/jpeg;base64,{image_b64}" style="width:100%;border-radius:6px;" />
            <p><b>{detection.label}</b><br>{detection.timestamp}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("View details", key=f"details_{key_suffix}"):
        st.session_state["detection_detail"] = detection.id
        st.rerun()


def _show_login() -> None:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign in"):
        with SessionLocal() as db:
            auth_service = AuthService(db)
            success, value = auth_service.login(username, password)
        if success:
            st.session_state["user_id"] = value
            st.rerun()
        else:
            st.error(str(value))


def _show_register() -> None:
    st.subheader("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign up"):
        with SessionLocal() as db:
            auth_service = AuthService(db)
            success, message = auth_service.register(username, email, password)
        if success:
            st.success(message)
        else:
            st.error(message)


def _show_detection_details(detection_id: int) -> None:
    with SessionLocal() as db:
        detection = db.query(Detection).filter(Detection.id == detection_id).first()

    if not detection:
        st.error("Detection not found.")
        return

    st.subheader("Detection details")
    image = Image.open(BytesIO(detection.image_data))
    st.image(image, caption=f"{detection.label} - {detection.timestamp}", use_container_width=True)
    st.write(f"Label: {detection.label}")
    st.write(f"Confidence: {detection.confidence}")

    if st.button("Back"):
        st.session_state["detection_detail"] = None
        st.rerun()

    st.markdown("---")
    st.subheader("Send details by email")
    recipient = st.text_input("Recipient email")

    if st.button("Send email"):
        if not recipient.strip():
            st.error("Recipient email is required.")
            return
        with SessionLocal() as db:
            service = DetectionService(db)
            sent = service.notify_detection(detection, recipient=recipient)
        if sent:
            st.success("Email sent.")
        else:
            st.warning("Email is not configured. Set SMTP values in .env.")


def _show_statistics(detections: list[Detection]) -> None:
    if not detections:
        st.info("No detections available.")
        return

    labels: list[str] = []
    dated_labels: list[tuple[str, str]] = []

    for detection in detections:
        detection_labels = [label.strip() for label in detection.label.split(",") if label.strip()]
        labels.extend(detection_labels)
        dated_labels.extend((label, detection.timestamp.date().isoformat()) for label in detection_labels)

    counts = Counter(labels)
    df_counts = pd.DataFrame(counts.items(), columns=["Label", "Count"]).sort_values("Count", ascending=False)

    st.altair_chart(
        alt.Chart(df_counts).mark_bar().encode(
            x=alt.X("Label", sort="-y"),
            y="Count",
            tooltip=["Label", "Count"],
        ),
        use_container_width=True,
    )

    df_time = pd.DataFrame(dated_labels, columns=["Label", "Date"])
    df_time = df_time.groupby(["Date", "Label"]).size().reset_index(name="Count")
    st.altair_chart(
        alt.Chart(df_time).mark_line(point=True).encode(
            x="Date:T",
            y="Count:Q",
            color="Label:N",
            tooltip=["Date", "Label", "Count"],
        ),
        use_container_width=True,
    )


def _show_dashboard() -> None:
    with SessionLocal() as db:
        service = DetectionService(db)
        latest = service.latest_detection()
        detections = service.list_recent(limit=40)

    tabs = st.tabs(["Latest", "All", "Statistics"])

    with tabs[0]:
        if latest:
            _render_detection_card(latest, "latest")
        else:
            st.info("No detections yet.")

    with tabs[1]:
        labels = sorted({label.strip() for d in detections for label in d.label.split(",") if label.strip()})
        selected_label = st.selectbox("Filter by label", options=["All"] + labels)

        filtered = detections
        if selected_label != "All":
            filtered = [d for d in detections if selected_label in [x.strip() for x in d.label.split(",")]]

        per_page = 8
        total_pages = max(1, (len(filtered) + per_page - 1) // per_page)
        current_page = min(st.session_state["current_page"], total_pages)
        st.session_state["current_page"] = current_page

        start = (current_page - 1) * per_page
        end = start + per_page
        for idx, detection in enumerate(filtered[start:end], start=1):
            _render_detection_card(detection, f"{current_page}_{idx}")

        col_prev, col_info, col_next = st.columns([1, 3, 1])
        with col_prev:
            if st.button("Previous") and current_page > 1:
                st.session_state["current_page"] -= 1
                st.rerun()
        with col_info:
            st.write(f"Page {current_page}/{total_pages}")
        with col_next:
            if st.button("Next") and current_page < total_pages:
                st.session_state["current_page"] += 1
                st.rerun()

    with tabs[2]:
        _show_statistics(detections)


def main() -> None:
    _init_session_state()
    st.title("NatureAlertCamera24")

    if st.session_state["user_id"]:
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        if st.session_state["detection_detail"]:
            _show_detection_details(st.session_state["detection_detail"])
        else:
            _show_dashboard()
        return

    selected = st.sidebar.radio("Menu", ["Login", "Register"])
    if selected == "Login":
        _show_login()
    else:
        _show_register()


if __name__ == "__main__":
    main()


