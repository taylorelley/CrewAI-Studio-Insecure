import streamlit as st


class PageCompare:
    def __init__(self):
        self.name = "Compare"

    def draw(self):
        st.subheader("Crew / Flow comparison")
        st.caption("Run A/B experiments and inspect differences.")

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Variant A", value="Crew 1")
            st.text_area("Notes", value="Manager LLM = gpt-4o")
        with col2:
            st.text_input("Variant B", value="Crew 2")
            st.text_area("Notes", value="Manager LLM = claude")

        st.button("Start comparison run", use_container_width=True)
        st.markdown("### Outcomes")
        st.table([
            {"metric": "Success rate", "A": "90%", "B": "82%"},
            {"metric": "Avg tokens", "A": 1200, "B": 900},
        ])
