import streamlit as st


class PageLLMComparison:
    def __init__(self):
        self.name = "LLM Comparison"

    def draw(self):
        st.subheader("LLM provider comparison")
        st.caption("Benchmark different providers for the same crew or flow.")

        providers = ["OpenAI", "Anthropic", "Groq", "Local"]
        st.multiselect("Providers", providers, default=providers[:2])
        st.checkbox("Enable failover", key="llm_failover", value=True)
        st.button("Run benchmark", use_container_width=True)

        st.markdown("### Sample results")
        st.table([
            {"provider": "OpenAI", "latency": "2.1s", "cost": "$0.04", "score": "8/10"},
            {"provider": "Anthropic", "latency": "2.5s", "cost": "$0.05", "score": "8.5/10"},
        ])
