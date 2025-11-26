import streamlit as st
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
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
    nodes: List[Dict] = field(
        default_factory=lambda: [
            {"id": "start", "label": "Start", "type": "event", "lane": "entry"},
            {"id": "task_a", "label": "Task A", "type": "task", "lane": "analysis"},
            {"id": "human_gate", "label": "Human check", "type": "approval", "lane": "review"},
            {"id": "end", "label": "End", "type": "event", "lane": "exit"},
        ]
    )
    edges: List[Dict] = field(
        default_factory=lambda: [
            {"source": "start", "target": "task_a", "condition": "always"},
            {"source": "task_a", "target": "human_gate", "condition": "needs_approval"},
            {"source": "human_gate", "target": "end", "condition": "approved"},
        ]
    )
    test_harness: Dict = field(default_factory=lambda: {"dry_run": True, "step": True, "mock": ""})
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

    def as_graphviz(self, nodes: List[Dict] = None, edges: List[Dict] = None) -> str:
        nodes = nodes or self.nodes
        edges = edges or self.edges
        graph_lines = ["digraph Flow {"]
        graph_lines.append('  rankdir="LR";')
        for node in nodes:
            label = node.get("label", node.get("id"))
            n_type = node.get("type", "task")
            shape = "box" if n_type in ["task", "approval"] else "ellipse"
            color = "#7f5af0" if n_type == "task" else "#f25f4c" if n_type == "approval" else "#94d2bd"
            graph_lines.append(f'  "{node.get("id")}" [label="{label}" shape={shape} style=filled fillcolor="{color}"];')
        for edge in edges:
            src = edge.get("source")
            dst = edge.get("target")
            label = edge.get("condition", "")
            graph_lines.append(f'  "{src}" -> "{dst}" [label="{label}"];')
        graph_lines.append("}")
        return "\n".join(graph_lines)

    def _update_name(self):
        self.name = st.session_state.get(f"flow_name_{self.id}", self.name)

    def _update_description(self):
        self.description = st.session_state.get(f"flow_desc_{self.id}", self.description)

    def _update_entry(self):
        self.entry_event = st.session_state.get(f"flow_entry_{self.id}", self.entry_event)
