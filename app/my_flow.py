import streamlit as st
from dataclasses import dataclass, field
from datetime import datetime
from utils import rnd_id


@dataclass
class MyFlow:
    """Lightweight placeholder for a CrewAI Flow definition.

    The real CrewAI SDK exposes richer primitives for event-driven flows.
    This object focuses on storing a small amount of metadata so the UI can
    present and persist drafts until a full runtime wiring is added.
    """

    id: str = field(default_factory=lambda: f"F_{rnd_id()}")
    name: str = "Flow"
    description: str = ""
    version: str = "v1"
    entry_event: str = "manual"
    state_preview: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def is_valid(self) -> bool:
        return bool(self.name)

    def draw(self):
        st.text_input("Name", key=f"flow_name_{self.id}", value=self.name, on_change=self._update_name)
        st.text_area("Description", key=f"flow_desc_{self.id}", value=self.description, on_change=self._update_description)
        st.selectbox(
            "Entry trigger",
            options=["manual", "webhook", "schedule", "event"],
            key=f"flow_entry_{self.id}",
            index=["manual", "webhook", "schedule", "event"].index(self.entry_event)
            if self.entry_event in ["manual", "webhook", "schedule", "event"]
            else 0,
            on_change=self._update_entry,
        )
        with st.expander("State preview", expanded=False):
            st.json(self.state_preview or {"note": "State inspection will appear after runs."})

    def _update_name(self):
        self.name = st.session_state.get(f"flow_name_{self.id}", self.name)

    def _update_description(self):
        self.description = st.session_state.get(f"flow_desc_{self.id}", self.description)

    def _update_entry(self):
        self.entry_event = st.session_state.get(f"flow_entry_{self.id}", self.entry_event)
