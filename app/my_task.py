from crewai import Task
import streamlit as st
from utils import rnd_id, fix_columns_width
from streamlit import session_state as ss
from db_utils import save_task, delete_task
import db_utils
from datetime import datetime

class MyTask:
    def __init__(self, id=None, description=None, expected_output=None, agent=None, async_execution=None, created_at=None, context_from_async_tasks_ids=None, context_from_sync_tasks_ids=None, **kwargs):
        self.id = id or "T_" + rnd_id()
        self.description = description or "Identify the next big trend in AI. Focus on identifying pros and cons and the overall narrative."
        self.expected_output = expected_output or "A comprehensive 3 paragraphs long report on the latest AI trends."
        self.agent = agent or ss.agents[0] if ss.agents else None
        self.async_execution = async_execution or False
        self.context_from_async_tasks_ids = context_from_async_tasks_ids or None
        self.context_from_sync_tasks_ids = context_from_sync_tasks_ids or None
        self.created_at = created_at or datetime.now().isoformat()
        self.edit_key = f'edit_{self.id}'
        if self.edit_key not in ss:
            ss[self.edit_key] = False

    @property
    def edit(self):
        return ss[self.edit_key]

    @edit.setter
    def edit(self, value):
        ss[self.edit_key] = value

    def get_crewai_task(self, context_from_async_tasks=None, context_from_sync_tasks=None) -> Task:
        context = []
        if context_from_async_tasks:
            context.extend(context_from_async_tasks)
        if context_from_sync_tasks:
            context.extend(context_from_sync_tasks)
        
        if context:
            return Task(description=self.description, expected_output=self.expected_output, async_execution=self.async_execution, agent=self.agent.get_crewai_agent(), context=context)
        else:
            return Task(description=self.description, expected_output=self.expected_output, async_execution=self.async_execution, agent=self.agent.get_crewai_agent())

    def delete(self):
        ss.tasks = [task for task in ss.tasks if task.id != self.id]
        delete_task(self.id)

    def request_delete_modal(self):
        """Flag this task for deletion and trigger modal display."""
        ss['delete_task_target_id'] = self.id

    def clear_delete_modal(self):
        if 'delete_task_target_id' in ss:
            del ss['delete_task_target_id']

    def analyze_dependencies(self):
        """Analyze dependencies for this task."""
        conflicts = []

        # Check if used in crews
        used_in_crews = [c.name for c in ss.get('crews', []) if any(t.id == self.id for t in c.tasks)]
        if used_in_crews:
            conflicts.append(f"Used in crews: {', '.join(used_in_crews)}")

        # Check if used as context in other tasks
        used_as_context = []
        for task in ss.get('tasks', []):
            if task.id != self.id:
                if self.id in (task.context_from_async_tasks_ids or []) or self.id in (task.context_from_sync_tasks_ids or []):
                    used_as_context.append(task.description[:40])

        if used_as_context:
            conflicts.append(f"Referenced as context in {len(used_as_context)} task(s)")

        return conflicts

    def draw_delete_dialog(self):
        conflicts = self.analyze_dependencies()

        if not hasattr(st, 'dialog'):
            st.error("This Streamlit version does not support st.dialog – please upgrade Streamlit.")
            return

        @st.dialog(f"Delete task: {self.description[:50]}")
        def _dlg():
            st.markdown("### Confirm deleting task")

            if conflicts:
                st.warning("⚠️ This task has dependencies:")
                for conflict in conflicts:
                    st.markdown(f"- {conflict}")
                st.markdown("Deleting this task will:")
                st.markdown("- Remove it from all crews")
                st.markdown("- Remove it as context from other tasks")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Cancel"):
                    self.clear_delete_modal()
                    st.rerun()
            with col_b:
                if st.button("Delete task", type="primary"):
                    # Remove from crews
                    for crew in ss.get('crews', []):
                        if any(t.id == self.id for t in crew.tasks):
                            crew.tasks = [t for t in crew.tasks if t.id != self.id]
                            db_utils.save_crew(crew)

                    # Remove from context references
                    for task in ss.get('tasks', []):
                        if task.id != self.id:
                            if task.context_from_async_tasks_ids and self.id in task.context_from_async_tasks_ids:
                                task.context_from_async_tasks_ids.remove(self.id)
                                save_task(task)
                            if task.context_from_sync_tasks_ids and self.id in task.context_from_sync_tasks_ids:
                                task.context_from_sync_tasks_ids.remove(self.id)
                                save_task(task)

                    # Delete task
                    self.delete()
                    self.clear_delete_modal()
                    st.rerun()

        _dlg()

    def duplicate(self):
        """Create a copy of this task with a new ID"""
        new_task = MyTask(
            description=f"{self.description} (Copy)",
            expected_output=self.expected_output,
            agent=self.agent,
            async_execution=self.async_execution,
            context_from_async_tasks_ids=self.context_from_async_tasks_ids.copy() if self.context_from_async_tasks_ids else None,
            context_from_sync_tasks_ids=self.context_from_sync_tasks_ids.copy() if self.context_from_sync_tasks_ids else None
        )
        ss.tasks.append(new_task)
        save_task(new_task)
        st.toast(f"✅ Task duplicated successfully!", icon="✅")
        return new_task

    def is_valid(self, show_warning=False):
        if not self.agent:
            if show_warning:
                st.warning(f"Task {self.description} has no agent")
            return False
        if not self.agent.is_valid(show_warning):
            return False
        return True

    def draw(self, key=None):
        agent_options = [agent.role for agent in ss.agents]
        expander_title = f"({self.agent.role if self.agent else 'unassigned'}) - {self.description}" if self.is_valid() else f"❗ ({self.agent.role if self.agent else 'unassigned'}) - {self.description}"
        if self.edit:
            with st.expander(expander_title, expanded=True):
                with st.form(key=f'form_{self.id}' if key is None else key):
                    self.description = st.text_area("Description", value=self.description)
                    st.caption(f"Characters: {len(self.description)}")
                    self.expected_output = st.text_area("Expected output", value=self.expected_output)
                    st.caption(f"Characters: {len(self.expected_output)}")
                    self.agent = st.selectbox("Agent", options=ss.agents, format_func=lambda x: x.role, index=0 if self.agent is None else agent_options.index(self.agent.role))
                    self.async_execution = st.checkbox("Async execution", value=self.async_execution)
                    self.context_from_async_tasks_ids = st.multiselect("Context from async tasks", options=[task.id for task in ss.tasks if task.async_execution], default=self.context_from_async_tasks_ids, format_func=lambda x: [task.description[:120] for task in ss.tasks if task.id == x][0])
                    self.context_from_sync_tasks_ids = st.multiselect("Context from sync tasks", options=[task.id for task in ss.tasks if not task.async_execution], default=self.context_from_sync_tasks_ids, format_func=lambda x: [task.description[:120] for task in ss.tasks if task.id == x][0])
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submitted = st.form_submit_button("Save", type="primary")
                    with col_cancel:
                        cancelled = st.form_submit_button("Cancel")
                    if submitted:
                        self.set_editable(False)
                    elif cancelled:
                        self.set_editable(False)
        else:
            fix_columns_width()
            with st.expander(expander_title):
                st.markdown(f"**Description:** {self.description}")
                st.markdown(f"**Expected output:** {self.expected_output}")
                st.markdown(f"**Agent:** {self.agent.role if self.agent else 'None'}")
                st.markdown(f"**Async execution:** {self.async_execution}")
                st.markdown(f"**Context from async tasks:** {', '.join([task.description[:120] for task in ss.tasks if task.id in self.context_from_async_tasks_ids]) if self.context_from_async_tasks_ids else 'None'}")
                st.markdown(f"**Context from sync tasks:** {', '.join([task.description[:120] for task in ss.tasks if task.id in self.context_from_sync_tasks_ids]) if self.context_from_sync_tasks_ids else 'None'}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("Edit", on_click=self.set_editable, args=(True,), key=rnd_id())
                with col2:
                    st.button("Duplicate", on_click=self.duplicate, key=rnd_id())
                with col3:
                    st.button("Delete", on_click=self.request_delete_modal, key=rnd_id())
                self.is_valid(show_warning=True)

                # If this task was selected for deletion, draw the modal here
                if ss.get('delete_task_target_id') == self.id:
                    self.draw_delete_dialog()

    def set_editable(self, edit):
        self.edit = edit
        save_task(self)
        if not edit:
            st.rerun()