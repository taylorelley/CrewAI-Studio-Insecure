import streamlit as st
from streamlit import session_state as ss


class PageScheduler:
    def __init__(self):
        self.name = "Scheduling"

    def draw(self):
        st.subheader("Scheduling")
        st.caption("Create recurring runs and view upcoming schedules.")

        st.text_input("Cron expression", key="sched_cron", value="0 * * * *")
        st.selectbox("Target", ["Crew", "Flow"], key="sched_target")
        st.text_input("Target name", key="sched_target_name", value="Crew 1")
        st.checkbox("Send notification on completion", key="sched_notify", value=True)
        st.button("Add schedule", use_container_width=True)

        st.markdown("### Upcoming runs")
        st.table([
            {"target": "Crew 1", "cron": "0 * * * *", "next": "in 35 min"},
            {"target": "Flow 1", "cron": "*/5 * * * *", "next": "in 2 min"},
        ])
