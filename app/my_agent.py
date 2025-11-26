from crewai import Agent
import streamlit as st
from utils import rnd_id, fix_columns_width, format_llm_display
from streamlit import session_state as ss
from db_utils import save_agent, delete_agent, save_task
import db_utils
from llms import llm_providers_and_models, create_llm
from datetime import datetime

class MyAgent:
    NO_LLM_SENTINEL = "none:none"
    def __init__(self, id=None, role=None, backstory=None, goal=None, temperature=None, allow_delegation=False, verbose=False, cache= None, llm_provider_model=None, max_iter=None, created_at=None, tools=None, knowledge_source_ids=None):
        self.id = id or "A_" + rnd_id()
        self.role = role or "Senior Researcher"
        self.backstory = backstory or "Driven by curiosity, you're at the forefront of innovation, eager to explore and share knowledge that could change the world."
        self.goal = goal or "Uncover groundbreaking technologies in AI"
        self.temperature = temperature or 0.1
        self.allow_delegation = allow_delegation if allow_delegation is not None else False
        self.verbose = verbose if verbose is not None else True
        available_llms = llm_providers_and_models()
        if llm_provider_model is None:
            self.llm_provider_model = available_llms[0] if available_llms else self.NO_LLM_SENTINEL
        else:
            self.llm_provider_model = llm_provider_model
        self.created_at = created_at or datetime.now().isoformat()
        self.tools = tools or []
        self.max_iter = max_iter or 25
        self.cache = cache if cache is not None else True
        self.knowledge_source_ids = knowledge_source_ids or []
        self.edit_key = f'edit_{self.id}'
        if self.edit_key not in ss:
            ss[self.edit_key] = False

    @property
    def edit(self):
        return ss[self.edit_key]

    @edit.setter
    def edit(self, value):
        ss[self.edit_key] = value

    def get_crewai_agent(self) -> Agent:
        if not self.llm_provider_model or self.llm_provider_model == self.NO_LLM_SENTINEL:
            raise ValueError("No LLM provider/model configured. Please configure an LLM in your environment before creating agents.")

        llm = create_llm(self.llm_provider_model, temperature=self.temperature)
        tools = [tool.create_tool() for tool in self.tools]
        
        # Add knowledge sources if they exist
        knowledge_sources = []
        if 'knowledge_sources' in ss and self.knowledge_source_ids:
            valid_knowledge_source_ids = []
            
            for ks_id in self.knowledge_source_ids:
                ks = next((k for k in ss.knowledge_sources if k.id == ks_id), None)
                if ks:
                    try:
                        knowledge_sources.append(ks.get_crewai_knowledge_source())
                        valid_knowledge_source_ids.append(ks_id)
                    except Exception as e:
                        print(f"Error loading knowledge source {ks.id}: {str(e)}")
        if knowledge_sources:
            print(f"Loaded {len(knowledge_sources)} knowledge sources for agent {self.id}")
            print(knowledge_sources)
        return Agent(
            role=self.role,
            backstory=self.backstory,
            goal=self.goal,
            allow_delegation=self.allow_delegation,
            verbose=self.verbose,
            max_iter=self.max_iter,
            cache=self.cache,
            tools=tools,
            llm=llm,
            knowledge_sources=knowledge_sources if knowledge_sources else None
        )

    def delete(self):
        ss.agents = [agent for agent in ss.agents if agent.id != self.id]
        delete_agent(self.id)

    def request_delete_modal(self):
        """Flag this agent for deletion and trigger modal display."""
        ss['delete_agent_target_id'] = self.id

    def clear_delete_modal(self):
        if 'delete_agent_target_id' in ss:
            del ss['delete_agent_target_id']

    def analyze_dependencies(self):
        """Analyze dependencies for this agent."""
        conflicts = []

        # Check if used in crews
        used_in_crews = [c.name for c in ss.get('crews', []) if any(a.id == self.id for a in c.agents)]
        if used_in_crews:
            conflicts.append(f"Used in crews: {', '.join(used_in_crews)}")

        # Check if used in tasks
        used_in_tasks = [t.description[:40] for t in ss.get('tasks', []) if t.agent and t.agent.id == self.id]
        if used_in_tasks:
            conflicts.append(f"Assigned to {len(used_in_tasks)} task(s)")

        return conflicts

    def draw_delete_dialog(self):
        conflicts = self.analyze_dependencies()

        if not hasattr(st, 'dialog'):
            st.error("This Streamlit version does not support st.dialog – please upgrade Streamlit.")
            return

        @st.dialog(f"Delete agent: {self.role}")
        def _dlg():
            st.markdown("### Confirm deleting agent")

            if conflicts:
                st.warning("⚠️ This agent has dependencies:")
                for conflict in conflicts:
                    st.markdown(f"- {conflict}")
                st.markdown("Deleting this agent will:")
                st.markdown("- Remove it from all crews")
                st.markdown("- Unassign it from all tasks")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Cancel"):
                    self.clear_delete_modal()
                    st.rerun()
            with col_b:
                if st.button("Delete agent", type="primary"):
                    # Remove from crews
                    for crew in ss.get('crews', []):
                        if any(a.id == self.id for a in crew.agents):
                            crew.agents = [a for a in crew.agents if a.id != self.id]
                            db_utils.save_crew(crew)

                    # Unassign from tasks
                    for task in ss.get('tasks', []):
                        if task.agent and task.agent.id == self.id:
                            task.agent = None
                            save_task(task)

                    # Delete agent
                    self.delete()
                    self.clear_delete_modal()
                    st.rerun()

        _dlg()

    def duplicate(self):
        """Create a copy of this agent with a new ID"""
        new_agent = MyAgent(
            role=f"{self.role} (Copy)",
            backstory=self.backstory,
            goal=self.goal,
            temperature=self.temperature,
            allow_delegation=self.allow_delegation,
            verbose=self.verbose,
            cache=self.cache,
            llm_provider_model=self.llm_provider_model,
            max_iter=self.max_iter,
            tools=self.tools.copy(),
            knowledge_source_ids=self.knowledge_source_ids.copy()
        )
        ss.agents.append(new_agent)
        save_agent(new_agent)
        st.toast(f"✅ Agent '{new_agent.role}' duplicated successfully!", icon="✅")
        return new_agent

    def get_tool_display_name(self, tool):
        first_param_name = tool.get_parameter_names()[0] if tool.get_parameter_names() else None
        first_param_value = tool.parameters.get(first_param_name, '') if first_param_name else ''
        return f"{tool.name} ({first_param_value if first_param_value else tool.tool_id})"

    def is_valid(self, show_warning=False):
        for tool in self.tools:
            if not tool.is_valid(show_warning=show_warning):
                if show_warning:
                    st.warning(f"Tool {tool.name} is not valid")
                return False
        return True

    def validate_llm_provider_model(self):
        available_models = llm_providers_and_models()
        if available_models:
            if self.llm_provider_model not in available_models:
                self.llm_provider_model = available_models[0]
        else:
            self.llm_provider_model = self.NO_LLM_SENTINEL

    def draw(self, key=None):
        self.validate_llm_provider_model()
        if self.llm_provider_model and ": " in self.llm_provider_model:
            selected_model = format_llm_display(self.llm_provider_model)
        else:
            selected_model = "No LLM configured"

        expander_title = f"{self.role[:60]} - {selected_model}" if self.is_valid() else f"❗ {self.role[:20]} - {selected_model}"
        form_key = f'form_{self.id}_{key}' if key else f'form_{self.id}'        
        if self.edit:
            with st.expander(f"Agent: {self.role}", expanded=True):
                with st.form(key=form_key):
                    self.role = st.text_input("Role", value=self.role)
                    self.backstory = st.text_area("Backstory", value=self.backstory)
                    st.caption(f"Characters: {len(self.backstory)}")
                    self.goal = st.text_area("Goal", value=self.goal)
                    st.caption(f"Characters: {len(self.goal)}")
                    self.allow_delegation = st.checkbox("Allow delegation", value=self.allow_delegation)
                    self.verbose = st.checkbox("Verbose", value=self.verbose)
                    self.cache = st.checkbox("Cache", value=self.cache)
                    available_llms = llm_providers_and_models()
                    if available_llms:
                        selected_index = available_llms.index(self.llm_provider_model) if self.llm_provider_model in available_llms else 0
                        self.llm_provider_model = st.selectbox(
                            "LLM Provider and Model",
                            options=available_llms,
                            index=selected_index,
                        )
                    else:
                        st.warning("No LLM providers are configured. Please update your .env file.")
                        self.llm_provider_model = self.NO_LLM_SENTINEL
                    self.temperature = st.slider("Temperature", value=self.temperature, min_value=0.0, max_value=1.0)
                    self.max_iter = st.number_input("Max Iterations", value=self.max_iter, min_value=1, max_value=100)                    
                    enabled_tools = [tool for tool in ss.tools]
                    tools_key = f"{self.id}_tools_{key}" if key else f"{self.id}_tools"
                    selected_tools = st.multiselect(
                        "Select Tools",
                        [self.get_tool_display_name(tool) for tool in enabled_tools],
                        default=[self.get_tool_display_name(tool) for tool in self.tools],
                        key=tools_key
                    )                    
                    if 'knowledge_sources' in ss and len(ss.knowledge_sources) > 0:
                        knowledge_source_options = [ks.id for ks in ss.knowledge_sources]
                        knowledge_source_labels = {ks.id: ks.name for ks in ss.knowledge_sources}
                        
                        # Filter out any knowledge source IDs that no longer exist
                        valid_knowledge_sources = [ks_id for ks_id in self.knowledge_source_ids 
                                                if ks_id in knowledge_source_options]
                        
                        # If we filtered out any IDs, update the agent's knowledge sources
                        if len(valid_knowledge_sources) != len(self.knowledge_source_ids):
                            self.knowledge_source_ids = valid_knowledge_sources
                            save_agent(self)
                        
                        # Generate a unique key for the knowledge sources multiselect
                        ks_key = f"knowledge_sources_{self.id}_{key}" if key else f"knowledge_sources_{self.id}"
                        
                        # Now use the filtered list for the multiselect with the unique key
                        selected_knowledge_sources = st.multiselect(
                            "Knowledge Sources",
                            options=knowledge_source_options,
                            default=valid_knowledge_sources,
                            format_func=lambda x: knowledge_source_labels.get(x, "Unknown"),
                            key=ks_key
                        )
                        self.knowledge_source_ids = selected_knowledge_sources
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submitted = st.form_submit_button("Save", type="primary")
                    with col_cancel:
                        cancelled = st.form_submit_button("Cancel")
                    if submitted:
                        self.tools = [tool for tool in enabled_tools if self.get_tool_display_name(tool) in selected_tools]
                        self.set_editable(False)
                    elif cancelled:
                        self.set_editable(False)
        else:
            fix_columns_width()
            with st.expander(expander_title, expanded=False):
                st.markdown(f"**Role:** {self.role}")
                st.markdown(f"**Backstory:** {self.backstory}")
                st.markdown(f"**Goal:** {self.goal}")
                st.markdown(f"**Allow delegation:** {self.allow_delegation}")
                st.markdown(f"**Verbose:** {self.verbose}")
                st.markdown(f"**Cache:** {self.cache}")
                st.markdown(f"**LLM Provider and Model:** {self.llm_provider_model}")
                st.markdown(f"**Temperature:** {self.temperature}")
                st.markdown(f"**Max Iterations:** {self.max_iter}")
                st.markdown(f"**Tools:** {[self.get_tool_display_name(tool) for tool in self.tools]}")                
                # Display knowledge sources
                if self.knowledge_source_ids and 'knowledge_sources' in ss:
                    knowledge_sources = [ks for ks in ss.knowledge_sources if ks.id in self.knowledge_source_ids]
                    if knowledge_sources:
                        st.markdown("**Knowledge Sources:**")
                        for ks in knowledge_sources:
                            st.markdown(f"- {ks.name}")
                self.is_valid(show_warning=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    btn_key = f"edit_btn_{rnd_id()}"
                    st.button("Edit", on_click=self.set_editable, args=(True,), key=btn_key)
                with col2:
                    dup_key = f"dup_btn_{rnd_id()}"
                    st.button("Duplicate", on_click=self.duplicate, key=dup_key)
                with col3:
                    del_key = f"del_btn_{rnd_id()}"
                    st.button("Delete", on_click=self.request_delete_modal, key=del_key)

                # If this agent was selected for deletion, draw the modal here
                if ss.get('delete_agent_target_id') == self.id:
                    self.draw_delete_dialog()

    def set_editable(self, edit):
        self.edit = edit
        save_agent(self)
        if not edit:
            st.rerun()
