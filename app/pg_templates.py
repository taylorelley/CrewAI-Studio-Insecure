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

        categories = sorted(set(t["category"] for t in TEMPLATES))
        active_category = st.radio("Category", options=["All"] + categories, index=0, horizontal=True)

        filtered = [t for t in TEMPLATES if active_category in ("All", t["category"])]
        rows = [filtered[i:i+3] for i in range(0, len(filtered), 3)]
        for row in rows:
            cols = st.columns(len(row))
            for col, template in zip(cols, row):
                with col:
                    st.markdown(
                        f"""
                        <div style='padding:14px;border-radius:14px;border:1px solid #e0e0e0;background:linear-gradient(145deg,#f8fafc,#ffffff);'>
                            <h4 style='margin-bottom:6px'>{template['name']}</h4>
                            <small style='color:#6b7280'>{template['category']}</small>
                            <p style='margin-top:10px;color:#111827'>{template['description']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.button("Import", key=f"import_{template['name']}", use_container_width=True)

        st.markdown("### Custom template upload")
        uploaded = st.file_uploader("Upload template package", type=["json", "yaml", "zip"])
        if uploaded:
            ss['uploaded_template_name'] = uploaded.name
            st.success(f"Staged {uploaded.name} for import")
            st.markdown(f"Preview: **{uploaded.name}** will be parsed and added to the gallery.")

