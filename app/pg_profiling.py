import streamlit as st


class PageProfiling:
    def __init__(self):
        self.name = "Profiling"

    def draw(self):
        st.subheader("Profiling")
        st.caption("Inspect latency, token usage, and tool calls.")

        st.metric("Average task latency", "1.8s")
        st.metric("Tokens per task", "450")
        st.metric("Tool calls", "3")

        st.markdown("### Bottleneck hints")
        st.write("Visualize where tasks spend time and how often retries occur.")
        st.progress(60, text="Task B waiting for approval")

