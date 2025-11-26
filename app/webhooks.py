import streamlit as st


class PageWebhooks:
    def __init__(self):
        self.name = "Webhooks"

    def draw(self):
        st.subheader("Webhooks")
        st.caption("Configure inbound triggers for crews and flows.")

        st.text_input("Endpoint", value="https://example.com/webhooks/crew", help="Expose via reverse proxy in production")
        st.text_area("Sample payload", value="{""crew_id"": ""C_123"", ""inputs"": {""query"": ""hello""}}")
        st.checkbox("Require secret", value=True)
        st.button("Save webhook", use_container_width=True)

        st.markdown("### Recent deliveries")
        st.table([
            {"status": "200", "latency": "450ms", "note": "Crew triggered"},
            {"status": "401", "latency": "--", "note": "Missing secret"},
        ])
