import streamlit as st
from streamlit import session_state as ss
import db_utils
from my_flow import MyFlow


class PageFlows:
    def __init__(self):
        self.name = "Flows"

    def _ensure_canvas_state(self, flow: MyFlow):
        nodes_key = f"flow_nodes_{flow.id}"
        edges_key = f"flow_edges_{flow.id}"
        harness_key = f"flow_harness_{flow.id}"
        if nodes_key not in ss:
            ss[nodes_key] = flow.nodes.copy()
        if edges_key not in ss:
            ss[edges_key] = flow.edges.copy()
        if harness_key not in ss:
            ss[harness_key] = flow.test_harness.copy()
        return nodes_key, edges_key, harness_key

    def _create_flow(self):
        flow = MyFlow(name=f"Flow {len(ss.get('flows', [])) + 1}")
        ss.flows.append(flow)
        db_utils.save_flow(flow)
        st.toast("Flow created", icon="✨")

    def _delete_flow(self, flow_id: str):
        ss.flows = [f for f in ss.get('flows', []) if f.id != flow_id]
        db_utils.delete_flow(flow_id)
        st.toast("Flow removed", icon="🗑️")

    def _save_flow(self, flow: MyFlow, nodes_key: str, edges_key: str, harness_key: str):
        flow.nodes = ss.get(nodes_key, [])
        flow.edges = ss.get(edges_key, [])
        flow.test_harness = ss.get(harness_key, flow.test_harness)
        db_utils.save_flow(flow)
        st.toast("Flow saved", icon="💾")

    def draw(self):
        st.subheader("Flow studio")
        st.caption("Plan, branch, and debug orchestrations with human gates inspired by n8n and suna.")

        if 'flows' not in ss:
            ss.flows = db_utils.load_flows()

        top_metrics = st.columns(4)
        top_metrics[0].metric("Flows", len(ss.flows))
        top_metrics[1].metric("Human gates", sum(1 for f in ss.flows for n in f.nodes if n.get("type") == "approval"))
        top_metrics[2].metric("Conditional edges", sum(1 for f in ss.flows for e in f.edges if e.get("condition") not in [None, "", "always"]))
        top_metrics[3].metric("Pending drafts", len([f for f in ss.flows if not f.state_preview]))

        st.markdown("---")
        action_cols = st.columns([1, 2, 2])
        action_cols[0].button("➕ New flow", on_click=self._create_flow, type="primary", use_container_width=True)
        if ss.flows:
            selected = action_cols[1].selectbox(
                "Select flow",
                options=ss.flows,
                format_func=lambda f: f"{f.name} ({f.version})",
                key="flow_selector",
            )
        else:
            selected = None
        if selected:
            action_cols[2].button(
                "🗑️ Delete selected",
                use_container_width=True,
                on_click=self._delete_flow,
                args=(selected.id,),
            )

        if not selected and ss.flows:
            selected = ss.flows[0]

        if selected:
            nodes_key, edges_key, harness_key = self._ensure_canvas_state(selected)
            tabs = st.tabs(["Canvas", "Debug & test", "State & docs"])

            with tabs[0]:
                st.markdown("#### Interactive canvas")
                st.caption("Edit nodes and edges inline, then preview the DAG. Use lanes to mimic swimlanes and approvals for human-in-the-loop moments.")
                lane_colors = {"entry": "#cddafd", "analysis": "#ffd6a5", "review": "#ffadad", "exit": "#caffbf"}
                col_canvas, col_preview = st.columns([1.2, 1])
                with col_canvas:
                    edited_nodes = st.data_editor(
                        ss[nodes_key],
                        key=f"nodes_editor_{selected.id}",
                        num_rows="dynamic",
                        hide_index=True,
                        column_config={
                            "id": st.column_config.TextColumn("Node id", required=True),
                            "label": st.column_config.TextColumn("Label", required=True),
                            "type": st.column_config.SelectboxColumn("Type", options=["event", "task", "approval", "tool"], required=True),
                            "lane": st.column_config.SelectboxColumn("Lane", options=list(lane_colors.keys()), required=True),
                        },
                        use_container_width=True,
                    )
                    ss[nodes_key] = edited_nodes

                    edited_edges = st.data_editor(
                        ss[edges_key],
                        key=f"edges_editor_{selected.id}",
                        num_rows="dynamic",
                        hide_index=True,
                        column_config={
                            "source": st.column_config.TextColumn("From", required=True),
                            "target": st.column_config.TextColumn("To", required=True),
                            "condition": st.column_config.TextColumn("Condition", required=False, help="e.g. approved, score>0.7"),
                        },
                        use_container_width=True,
                    )
                    ss[edges_key] = edited_edges

                    st.button(
                        "💾 Save layout",
                        key=f"save_flow_{selected.id}",
                        on_click=self._save_flow,
                        args=(selected, nodes_key, edges_key, harness_key),
                        use_container_width=True,
                    )

                with col_preview:
                    st.markdown("##### Diagram preview")
                    st.graphviz_chart(selected.as_graphviz(ss[nodes_key], ss[edges_key]), use_container_width=True)
                    st.markdown("##### Swimlanes")
                    lane_cols = st.columns(len(lane_colors))
                    for idx, (lane, color) in enumerate(lane_colors.items()):
                        lane_cols[idx].markdown(
                            f"<div style='padding:8px;border-radius:8px;background:{color}'><strong>{lane}</strong><br>{', '.join([n['label'] for n in ss[nodes_key] if n.get('lane')==lane]) or '—'}</div>",
                            unsafe_allow_html=True,
                        )

            with tabs[1]:
                st.markdown("#### Flow debugger")
                st.caption("Step through tasks, pause for approvals, or inject mock responses to test branches.")
                harness = ss[harness_key]
                col_a, col_b, col_c = st.columns(3)
                harness["dry_run"] = col_a.toggle("Dry run", value=harness.get("dry_run", True), key=f"dry_{selected.id}")
                harness["step"] = col_b.toggle("Step-through", value=harness.get("step", True), key=f"step_{selected.id}")
                harness["max_retries"] = col_c.slider("Retries", 0, 5, value=int(harness.get("max_retries", 2)), key=f"retry_{selected.id}")
                harness["mock"] = st.text_area("Mock LLM/tool payload", value=harness.get("mock", "Synthetic output"), key=f"mock_{selected.id}")
                ss[harness_key] = harness
                st.progress(35, text="Planned path scored")
                timeline = [
                    {"node": "start", "status": "done", "duration": "0.2s"},
                    {"node": "task_a", "status": "running", "duration": "1.1s"},
                    {"node": "human_gate", "status": "waiting", "duration": "--"},
                ]
                st.dataframe(timeline, use_container_width=True)
                st.button(
                    "▶️ Simulate test run",
                    use_container_width=True,
                    on_click=self._save_flow,
                    args=(selected, nodes_key, edges_key, harness_key),
                    key=f"run_test_{selected.id}",
                )

            with tabs[2]:
                st.markdown("#### Documentation & state")
                meta_cols = st.columns(2)
                with meta_cols[0]:
                    selected.draw()
                    st.text_input("Version", key=f"flow_version_{selected.id}", value=selected.version,
                                  on_change=lambda fid=selected.id: self._update_version(fid))
                with meta_cols[1]:
                    st.json({"entry": selected.entry_event, "nodes": len(ss[nodes_key]), "edges": len(ss[edges_key]), "harness": harness})
                    st.markdown("***Live state snapshot***")
                    st.code("Conditional routing, parallel branches, and approvals are captured above. Export to PNG via the diagram widget.")

    def _update_version(self, flow_id: str):
        version_val = st.session_state.get(f"flow_version_{flow_id}")
        for flow in ss.get('flows', []):
            if flow.id == flow_id:
                flow.version = version_val
                db_utils.save_flow(flow)
                break
