import streamlit as st
from streamlit import session_state as ss


class PageTesting:
    def __init__(self):
        self.name = "Testing & Debugging"

    def draw(self):
        st.subheader("Testing & Debugging")
        st.write("Step through crews or flows with optional mocked outputs.")

        control_cols = st.columns(4)
        control_cols[0].toggle("Enable dry run", key="test_dry_run", value=True)
        control_cols[1].toggle("Mock LLM responses", key="test_mock_llm")
        control_cols[2].slider("Max retries", 0, 5, 2, key="test_retries")
        control_cols[3].selectbox("Target", ["Crew", "Flow", "Task"], key="test_target")

        st.text_area("Mock payload", key="test_mock_payload", value="Simulated output for debugging")
        action_cols = st.columns(2)
        action_cols[0].button("Run single task", use_container_width=True, type="primary")
        action_cols[1].button("Run full crew", use_container_width=True)

        tabs = st.tabs(["Execution timeline", "Error matrix", "Live inspector"])
        with tabs[0]:
            history = ss.get('debug_history', [
                {"step": "Task A", "status": "success", "latency": "1.2s"},
                {"step": "Task B", "status": "paused", "latency": "--", "note": "Awaiting human approval"},
            ])
            st.dataframe(history, use_container_width=True)
            st.progress(0.45, text="Timeline coverage")
        with tabs[1]:
            st.markdown("Map of retry strategies across error categories")
            st.json({"llm": "retry with backoff", "tool": "fallback to cache", "network": "retry with jitter"})
        with tabs[2]:
            st.markdown("Real-time inspector")
            st.metric("Active span", "1.4s")
            st.metric("Tokens mocked", "420")
            st.graphviz_chart("""
                digraph {
                    rankdir=LR;
                    start -> task_a [label="ok"]
                    task_a -> human_gate [label="awaiting"]
                    human_gate -> task_b [label="approved"]
                }
            """, use_container_width=True)
