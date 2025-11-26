import streamlit as st


class PageWebhooks:
    def __init__(self):
        self.name = "Webhooks"

    def draw(self):
        st.subheader("Webhooks")
        st.caption("Configure inbound triggers for crews and flows.")

        col_form, col_monitor = st.columns([1.2, 1])
        with col_form:
            with st.container(border=True):
                st.markdown("#### Endpoint builder")
                st.text_input("Endpoint", value="https://example.com/webhooks/crew", help="Expose via reverse proxy in production")
                st.text_area("Sample payload", value="{""crew_id"": ""C_123"", ""inputs"": {""query"": ""hello""}}")
                st.checkbox("Require secret", value=True)
                st.selectbox("Target", ["Crew", "Flow"], key="webhook_target")
                st.button("Save webhook", use_container_width=True, type="primary")

        with col_monitor:
            st.markdown("#### Delivery monitor")
            st.metric("24h calls", 18)
            st.metric("Median latency", "410ms")
            st.progress(0.8, text="Uptime")
            st.code("curl -X POST https://example.com/webhooks/crew -H 'x-secret: ****' -d '{...}'")

        st.markdown("### Recent deliveries")
        st.data_editor([
            {"status": "200", "latency": "450ms", "note": "Crew triggered"},
            {"status": "401", "latency": "--", "note": "Missing secret"},
        ], hide_index=True, use_container_width=True)
