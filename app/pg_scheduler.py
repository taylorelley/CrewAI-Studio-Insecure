import streamlit as st
from streamlit import session_state as ss


class PageScheduler:
    def __init__(self):
        self.name = "Scheduling"

    def draw(self):
        st.subheader("Scheduling")
        st.caption("Create recurring runs and view upcoming schedules.")

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            with st.container(border=True):
                st.markdown("#### New schedule")
                st.text_input("Cron expression", key="sched_cron", value="0 * * * *")
                st.selectbox("Target", ["Crew", "Flow"], key="sched_target")
                st.text_input("Target name", key="sched_target_name", value="Crew 1")
                st.checkbox("Send notification on completion", key="sched_notify", value=True)
                st.slider("Concurrency", 1, 10, 3, key="sched_concurrency")
                st.button("Add schedule", use_container_width=True, type="primary")

        with col_right:
            st.markdown("#### Health & load")
            st.metric("Upcoming", 6, "+2 vs yesterday")
            st.metric("Queued", 1)
            st.progress(0.6, text="Window fill")

        st.markdown("### Upcoming runs")
        schedules = [
            {"target": "Crew 1", "cron": "0 * * * *", "next": "in 35 min", "channel": "slack"},
            {"target": "Flow 1", "cron": "*/5 * * * *", "next": "in 2 min", "channel": "email"},
        ]
        st.data_editor(schedules, hide_index=True, use_container_width=True)
