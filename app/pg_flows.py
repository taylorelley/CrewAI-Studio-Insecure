import streamlit as st
from streamlit import session_state as ss
import db_utils
from my_flow import MyFlow


class PageFlows:
    def __init__(self):
        self.name = "Flows"

    def _create_flow(self):
        flow = MyFlow(name=f"Flow {len(ss.get('flows', [])) + 1}")
        ss.flows.append(flow)
        db_utils.save_flow(flow)
        st.toast("Flow created", icon="✨")

    def _delete_flow(self, flow_id: str):
        ss.flows = [f for f in ss.get('flows', []) if f.id != flow_id]
        db_utils.delete_flow(flow_id)
        st.toast("Flow removed", icon="🗑️")

    def draw(self):
        st.subheader("Flows")
        if 'flows' not in ss:
            ss.flows = db_utils.load_flows()

        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("""Design event-driven orchestration with conditional routing,\
             human-in-the-loop gates, and task DAGs. This lightweight builder mirrors CrewAI's Flow patterns\
             while keeping definitions editable from the UI.""")
            st.button("New flow", on_click=self._create_flow, type="primary")
            for flow in ss.flows:
                with st.expander(f"{flow.name} ({flow.version})", expanded=False):
                    flow.draw()
                    st.text_input("Version", key=f"flow_version_{flow.id}", value=flow.version,
                                  on_change=lambda fid=flow.id: self._update_version(fid))
                    st.code("Conditional routing, parallel branches, and stateful nodes can be linked via the visual builder.")
                    st.button("Delete", key=f"del_{flow.id}", on_click=self._delete_flow, args=(flow.id,), use_container_width=True)

        with col2:
            st.markdown("### Visual builder")
            st.caption("Use this quick sketch pad to outline nodes and dependencies. A full ReactFlow canvas can be integrated later without breaking definitions.")
            nodes = st.text_area("Nodes (comma separated)", value="start, task_a, task_b, end", key="flow_nodes")
            edges = st.text_area("Edges (source>target per line)", value="start>task_a\nstart>task_b\ntask_a>end\ntask_b>end", key="flow_edges")
            graph_lines = ["digraph Flow {"]
            for node in [n.strip() for n in nodes.split(',') if n.strip()]:
                graph_lines.append(f'  "{node}";')
            for raw_edge in edges.splitlines():
                if '>' in raw_edge:
                    src, dst = raw_edge.split('>', 1)
                    graph_lines.append(f'  "{src.strip()}" -> "{dst.strip()}";')
            graph_lines.append("}")
            st.graphviz_chart("\n".join(graph_lines), use_container_width=True)

            st.markdown("### Flow test harness")
            st.checkbox("Dry run (no LLM)", key="flow_dry_run")
            st.checkbox("Step-through execution", key="flow_step")
            st.text_input("Mock response", key="flow_mock_response", value="Synthetic LLM output")
            st.button("Run test", use_container_width=True)

    def _update_version(self, flow_id: str):
        version_val = st.session_state.get(f"flow_version_{flow_id}")
        for flow in ss.get('flows', []):
            if flow.id == flow_id:
                flow.version = version_val
                db_utils.save_flow(flow)
                break
