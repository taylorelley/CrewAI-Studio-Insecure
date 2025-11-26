import streamlit as st
from streamlit import session_state as ss


TEMPLATES = [
    {"name": "Research crew", "description": "Analyst + researcher + reviewer", "category": "Research"},
    {"name": "Content studio", "description": "Plan, draft, edit, and polish content", "category": "Content"},
    {"name": "Analysis flow", "description": "Branching flow with approvals", "category": "Flows"},
]


class PageTemplates:
    def __init__(self):
        self.name = "Templates"

    def draw(self):
        st.subheader("Template gallery")
        st.caption("Clone ready-made crews and flows to jump-start experiments.")

        for template in TEMPLATES:
            with st.expander(f"{template['name']} ({template['category']})", expanded=False):
                st.write(template['description'])
                st.button("Import", key=f"import_{template['name']}", use_container_width=True)

        st.markdown("### Custom template upload")
        uploaded = st.file_uploader("Upload template package", type=["json", "yaml", "zip"])
        if uploaded:
            ss['uploaded_template_name'] = uploaded.name
            st.success(f"Staged {uploaded.name} for import")

