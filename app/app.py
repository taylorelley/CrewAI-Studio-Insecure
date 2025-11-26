import streamlit as st
from streamlit import session_state as ss
import db_utils
from pg_agents import PageAgents
from pg_tasks import PageTasks
from pg_crews import PageCrews
from pg_tools import PageTools
from pg_crew_run import PageCrewRun
from pg_export_crew import PageExportCrew
from pg_results import PageResults
from pg_knowledge import PageKnowledge
from dotenv import load_dotenv
from llms import load_secrets_from_env
import os
from ssl_override import disable_ssl_verification

# Ensure TLS/SSL verification is disabled before any network operations
disable_ssl_verification()

def pages():
    return {
        'Crews': PageCrews(),
        'Tools': PageTools(),
        'Agents': PageAgents(),
        'Tasks': PageTasks(),
        'Knowledge': PageKnowledge(),  # Add this line
        'Kickoff!': PageCrewRun(),
        'Results': PageResults(),
        'Import/export': PageExportCrew()
    }

def load_data():
    ss.agents = db_utils.load_agents()
    ss.tasks = db_utils.load_tasks()
    ss.crews = db_utils.load_crews()
    ss.tools = db_utils.load_tools()
    ss.enabled_tools = db_utils.load_tools_state()
    ss.knowledge_sources = db_utils.load_knowledge_sources()


def get_page_badges():
    """Generate badges for navigation showing item counts and validation status"""
    badges = {}

    # Count crews and validation status
    crews_count = len(ss.get('crews', []))
    invalid_crews = sum(1 for c in ss.get('crews', []) if not c.is_valid())
    badges['Crews'] = f"({crews_count})" + (" ⚠️" if invalid_crews > 0 else "")

    # Count tools
    tools_count = len(ss.get('tools', []))
    invalid_tools = sum(1 for t in ss.get('tools', []) if not t.is_valid())
    badges['Tools'] = f"({tools_count})" + (" ⚠️" if invalid_tools > 0 else "")

    # Count agents
    agents_count = len(ss.get('agents', []))
    invalid_agents = sum(1 for a in ss.get('agents', []) if not a.is_valid())
    badges['Agents'] = f"({agents_count})" + (" ⚠️" if invalid_agents > 0 else "")

    # Count tasks
    tasks_count = len(ss.get('tasks', []))
    invalid_tasks = sum(1 for t in ss.get('tasks', []) if not t.is_valid())
    badges['Tasks'] = f"({tasks_count})" + (" ⚠️" if invalid_tasks > 0 else "")

    # Count knowledge sources
    knowledge_count = len(ss.get('knowledge_sources', []))
    badges['Knowledge'] = f"({knowledge_count})"

    # Count results
    results_count = len(ss.get('results', []))
    badges['Results'] = f"({results_count})"

    # Kickoff status
    if ss.get('running', False):
        badges['Kickoff!'] = "🚀"
    else:
        badges['Kickoff!'] = ""

    badges['Import/export'] = ""

    return badges

def draw_sidebar():
    page_descriptions = {
        'Crews': 'Create and manage crew configurations',
        'Tools': 'Enable and configure tools for agents',
        'Agents': 'Define AI agents with roles and capabilities',
        'Tasks': 'Create tasks for agents to execute',
        'Knowledge': 'Manage knowledge sources for RAG',
        'Kickoff!': 'Execute crews and monitor progress',
        'Results': 'View and download crew execution results',
        'Import/export': 'Import/export crews and generate code'
    }

    with st.sidebar:
        st.image("img/crewai_logo.png")

        if 'page' not in ss:
            ss.page = 'Crews'

        # Get badges for each page
        badges = get_page_badges()

        # Create page labels with badges
        page_labels = [f"{page} {badges.get(page, '')}" for page in pages().keys()]

        selected_page = st.radio('Page', page_labels, index=list(pages().keys()).index(ss.page), label_visibility="collapsed")

        # Extract the actual page name (remove badge)
        selected_page_name = selected_page.split(' (')[0].split(' ⚠️')[0].split(' 🚀')[0].strip()

        # Show description for current page
        st.divider()
        if selected_page_name in page_descriptions:
            st.caption(f"ℹ️ {page_descriptions[selected_page_name]}")

        # Validation summary
        st.divider()
        validation_errors = []

        # Check crews
        for crew in ss.get('crews', []):
            if not crew.is_valid():
                validation_errors.append(f"❌ Crew: {crew.name}")

        # Check agents
        for agent in ss.get('agents', []):
            if not agent.is_valid():
                validation_errors.append(f"❌ Agent: {agent.role[:30]}")

        # Check tasks
        for task in ss.get('tasks', []):
            if not task.is_valid():
                validation_errors.append(f"❌ Task: {task.description[:30]}")

        # Check tools
        for tool in ss.get('tools', []):
            if not tool.is_valid():
                validation_errors.append(f"❌ Tool: {tool.name}")

        if validation_errors:
            with st.expander(f"⚠️ Validation Issues ({len(validation_errors)})", expanded=False):
                for error in validation_errors[:10]:  # Show max 10
                    st.caption(error)
                if len(validation_errors) > 10:
                    st.caption(f"... and {len(validation_errors) - 10} more")
        else:
            st.success("✅ All items valid")

        if selected_page_name != ss.page:
            ss.page = selected_page_name
            st.rerun()
            
def main():
    st.set_page_config(page_title="CrewAI Studio", page_icon="img/favicon.ico", layout="wide")
    load_secrets_from_env()
    if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
        try:
            import agentops
            agentops.init(api_key=os.getenv('AGENTOPS_API_KEY'),auto_start_session=False)    
        except ModuleNotFoundError as e:
            ss.agentops_failed = True
            print(f"Error initializing AgentOps: {str(e)}")            
        
    db_utils.initialize_db()
    load_data()
    draw_sidebar()
    PageCrewRun.maintain_session_state() #this will persist the session state for the crew run page so crew run can be run in a separate thread
    pages()[ss.page].draw()
    
if __name__ == '__main__':
    main()
