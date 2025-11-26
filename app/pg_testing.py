import streamlit as st
from streamlit import session_state as ss


class PageTesting:
    def __init__(self):
        self.name = "Testing & Debugging"

    def draw(self):
        st.subheader("Testing & Debugging")
        st.write("Step through crews or flows with optional mocked outputs.")

        st.checkbox("Enable dry run", key="test_dry_run", value=True)
        st.checkbox("Mock LLM responses", key="test_mock_llm")
        st.text_area("Mock payload", key="test_mock_payload", value="Simulated output for debugging")
        st.slider("Max retries", 0, 5, 2, key="test_retries")
        st.button("Run single task", use_container_width=True)
        st.button("Run full crew", use_container_width=True)

        st.markdown("### Execution timeline")
        history = ss.get('debug_history', [
            {"step": "Task A", "status": "success", "latency": "1.2s"},
            {"step": "Task B", "status": "paused", "latency": "--", "note": "Awaiting human approval"},
        ])
        st.table(history)

        st.markdown("### Retry and error categories")
        st.json({"llm": "retry with backoff", "tool": "fallback to cache", "network": "retry with jitter"})
