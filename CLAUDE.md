# CLAUDE.md - CrewAI Studio Development Guide

## Project Overview

**CrewAI Studio (Insecure Edition)** is a Streamlit-based web application that provides a no-code interface for creating, managing, and running AI agent crews using the CrewAI framework. This edition is specifically tailored for environments with TLS/SSL inspection or self-signed certificates, shipping with certificate verification disabled by default.

### Key Features
- Multi-platform support (Windows, Linux, MacOS)
- No-code interface for AI agent orchestration
- Multi-LLM provider support (OpenAI, Anthropic, Groq, Gemini, Ollama, Azure, AWS Bedrock, LM Studio, XAI/Grok)
- Knowledge source integration with RAG capabilities
- Custom and built-in CrewAI tools
- Crew execution history and results tracking
- Export crews as standalone Streamlit apps
- Threaded crew execution with background processing
- **TLS/SSL verification disabled by design** for corporate proxy environments

## Technology Stack

### Core Dependencies
- **Python**: 3.12+
- **UI Framework**: Streamlit
- **AI Framework**: CrewAI 0.165.1, CrewAI-Tools 0.65.0
- **LLM Integration**: LangChain ecosystem (0.3.x series)
  - langchain==0.3.25
  - langchain-community==0.3.24
  - langchain-openai==0.2.1
  - langchain-groq==0.2.0
  - langchain-anthropic>=0.3.0
- **Database**: SQLAlchemy with SQLite (default) or PostgreSQL support
- **Vector Store**: ChromaDB 0.5.23
- **Knowledge Management**: Embedchain 0.1.128
- **Search**: DuckDuckGo Search 8.0.2+

### Database Architecture
Uses a generic entity storage pattern with SQLAlchemy:
- Single `entities` table with columns: `id` (TEXT), `entity_type` (TEXT), `data` (TEXT/JSON)
- Supports both SQLite (local) and PostgreSQL (production)
- Configured via `DB_URL` environment variable

## Codebase Structure

```
CrewAI-Studio-Insecure/
├── app/                          # Main application directory
│   ├── app.py                    # Entry point - Streamlit app initialization
│   ├── db_utils.py               # Database operations (SQLAlchemy)
│   ├── llms.py                   # LLM provider management and creation
│   ├── ssl_override.py           # TLS/SSL verification disabling utilities
│   ├── utils.py                  # Helper functions (ID generation, UI utilities)
│   ├── console_capture.py        # Console output capture for UI display
│   ├── result.py                 # Result storage and retrieval
│   │
│   ├── my_agent.py               # MyAgent model class
│   ├── my_task.py                # MyTask model class
│   ├── my_crew.py                # MyCrew model class
│   ├── my_tools.py               # MyTool model and tool registry
│   ├── my_knowledge_source.py    # MyKnowledgeSource model
│   │
│   ├── pg_agents.py              # Agents page UI component
│   ├── pg_tasks.py               # Tasks page UI component
│   ├── pg_crews.py               # Crews page UI component
│   ├── pg_tools.py               # Tools page UI component
│   ├── pg_knowledge.py           # Knowledge sources page UI component
│   ├── pg_crew_run.py            # Crew execution page UI component
│   ├── pg_results.py             # Results history page UI component
│   ├── pg_export_crew.py         # Import/Export page UI component
│   │
│   └── tools/                    # Custom tool implementations
│       ├── CustomApiTool.py      # Generic API calling tool
│       ├── CustomCodeInterpreterTool.py
│       ├── CustomFileWriteTool.py
│       ├── ScrapeWebsiteToolEnhanced.py
│       ├── ScrapflyScrapeWebsiteTool.py
│       ├── CSVSearchToolEnhanced.py
│       └── DuckDuckGoSearchTool.py
│
├── img/                          # Images and assets
├── .streamlit/                   # Streamlit configuration
├── requirements.txt              # Python dependencies
├── .env_example                  # Example environment configuration
├── Dockerfile                    # Docker container definition
├── docker-compose.yaml           # Docker Compose configuration
├── install_conda.sh/bat          # Conda installation scripts
├── install_venv.sh/bat           # Virtual environment installation scripts
├── run_conda.sh/bat              # Conda run scripts
└── run_venv.sh/bat               # Virtual environment run scripts
```

## Core Architecture Patterns

### 1. Model Classes (my_*.py)
All model classes follow a consistent pattern:

**Entity ID Prefixes:**
- Agents: `A_` prefix
- Tasks: `T_` prefix
- Crews: `C_` prefix
- Tools: Generated via `tool_id`
- Knowledge Sources: Custom UUID

**Common Patterns:**
```python
class MyAgent:
    def __init__(self, id=None, ...):
        self.id = id or "A_" + rnd_id()
        self.edit_key = f'edit_{self.id}'
        # Store edit state in Streamlit session state

    def get_crewai_agent(self) -> Agent:
        # Convert to CrewAI framework object

    def draw(self, key=None):
        # Render Streamlit UI with edit/view modes

    def delete(self):
        # Remove from session state and database
```

### 2. Page Components (pg_*.py)
Page classes inherit from a common pattern and implement:
- `__init__()`: Initialize page state
- `draw()`: Render the page UI
- Event handlers for user interactions

### 3. Database Operations (db_utils.py)
Generic entity storage with type-specific loaders:
- `save_entity(entity_type, entity_id, data)`: Upsert JSON data
- `load_entities(entity_type)`: Retrieve all entities of a type
- `delete_entity(entity_type, entity_id)`: Remove entity
- Type-specific helpers: `save_agent()`, `load_agents()`, `save_crew()`, etc.

### 4. LLM Provider Management (llms.py)
Dynamic LLM provider detection and creation:
- `load_secrets_from_env()`: Load API keys into session state
- `llm_providers_and_models()`: Return available providers based on configured API keys
- `create_llm(provider_model, temperature)`: Factory for LLM instances
- Format: `"provider: model"` (e.g., `"openai: gpt-4"`, `"anthropic: claude-3-5-sonnet-20241022"`)

### 5. SSL/TLS Override (ssl_override.py)
**CRITICAL**: This is called early in `app.py` before any network operations:
```python
disable_ssl_verification()
```
Sets environment variables and patches `ssl` and `requests` modules to disable certificate verification globally.

## Key Conventions and Patterns

### Session State Management
Streamlit session state (`st.session_state` or `ss`) is heavily used:
- Entity collections: `ss.agents`, `ss.tasks`, `ss.crews`, `ss.tools`, `ss.knowledge_sources`
- UI state: `ss.page`, `ss.enabled_tools`
- Edit mode tracking: `ss[f'edit_{entity_id}']`
- Environment variables: `ss.env_vars`

### Edit/View Mode Pattern
All entities support toggling between view and edit modes:
1. View mode: Expandable display with Edit/Delete buttons
2. Edit mode: Form-based editing with Save button
3. State persisted in session state with `edit_key`
4. Changes saved to database on form submit
5. UI rerun triggered after save

### Tool Architecture
Tools are registered in `TOOL_CLASSES` dictionary in `my_tools.py`:
- Key: Tool identifier string
- Value: Tuple of (ToolClass, is_builtin_flag)
- Custom tools in `app/tools/` directory
- CrewAI built-in tools imported dynamically

**Tool Creation Pattern:**
```python
class MyTool:
    def __init__(self, name, tool_class, parameters):
        self.tool_id = rnd_id()
        self.name = name
        self.tool_class = tool_class
        self.parameters = parameters  # Dict of tool-specific params

    def create_tool(self):
        # Instantiate the actual tool class with parameters
        return self.tool_class(**self.parameters)
```

### Knowledge Source Integration
Knowledge sources provide RAG capabilities:
- Support for various source types (text, PDF, web, etc.)
- ChromaDB for vector storage
- Can be attached to agents or crews
- Loaded via Embedchain

### Dependency and Validation
Complex validation with dependency tracking:
- `is_valid(show_warning=False)`: Validation method on all entities
- Crews validate that all agents/tasks are valid
- Tasks validate that their agent is valid
- Cascade delete handling with conflict detection (see `MyCrew.analyze_dependencies()` in app/my_crew.py:356)

### Async Task Execution
Tasks support async execution with context sharing:
- `async_execution` flag on tasks
- `context_from_async_tasks_ids` and `context_from_sync_tasks_ids` for dependency context
- Recursive task creation resolves dependencies in `MyCrew.get_crewai_crew()`

## Development Workflows

### Local Development Setup

**Option 1: Virtual Environment**
```bash
# Linux/MacOS
./install_venv.sh
./run_venv.sh

# Windows
./install_venv.bat
./run_venv.bat
```

**Option 2: Conda**
```bash
# Linux/MacOS
./install_conda.sh
./run_conda.sh

# Windows
./install_conda.bat
./run_conda.bat
```

**Option 3: Docker**
```bash
cp .env_example .env
# Edit .env with your API keys
docker-compose up --build
```

### Environment Configuration
Create a `.env` file based on `.env_example`:

**Required for basic functionality:**
```env
OPENAI_API_KEY="your-key"  # Often needed for embeddings even with other LLMs
```

**Optional LLM providers (configure at least one):**
```env
ANTHROPIC_API_KEY="your-key"
GROQ_API_KEY="your-key"
GEMINI_API_KEY="your-key"
OLLAMA_HOST="http://localhost:11434"
OLLAMA_MODELS="ollama/llama3.2,ollama/llama3.1"
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AWS_ACCESS_KEY_ID="your-key"
AWS_SECRET_ACCESS_KEY="your-secret"
XAI_API_KEY="your-key"
LMSTUDIO_API_BASE="http://localhost:1234/v1"
```

**Database (optional):**
```env
DB_URL="postgresql://user:password@host:5432/dbname"
# Defaults to sqlite:///crewai.db if not set
```

**Tools (optional):**
```env
SERPER_API_KEY="your-key"  # For search tools
SCRAPFLY_API_KEY="your-key"  # For enhanced scraping
```

### Running the Application
The app starts on `http://localhost:8501` by default.

**Development mode** (auto-reload on file changes):
```bash
streamlit run app/app.py
```

### Database Management
- Default: SQLite database `crewai.db` in project root
- PostgreSQL: Set `DB_URL` environment variable
- Schema auto-created on first run via `db_utils.initialize_db()`
- **Troubleshooting**: Delete `crewai.db` to reset (loses all data)

## AI Assistant Guidelines

### When Making Changes

1. **Understand the Entity Lifecycle:**
   - Creation: User fills form → Model instance created → Saved to database → Added to session state
   - Update: Edit button → Form displayed → Save → Database update → Session state refresh → UI rerun
   - Delete: Delete button → Remove from session state → Database delete → UI rerun

2. **Session State is Critical:**
   - Always check if data exists in `ss` before accessing
   - Use `ss.get('key', default)` for safe access
   - Remember that session state persists across reruns but not across browser sessions

3. **Database Consistency:**
   - Always save to database after modifying entities
   - Use the entity-specific save functions: `save_agent(agent)`, `save_task(task)`, etc.
   - These handle JSON serialization automatically

4. **LLM Provider Handling:**
   - Check `llm_providers_and_models()` for available providers before showing UI
   - Validate that saved `llm_provider_model` still exists in available providers
   - Format is always `"provider: model"`
   - Handle the case when no providers are configured (`NO_LLM_SENTINEL`)

5. **Tool Integration:**
   - Tools must be registered in `TOOL_CLASSES` in `my_tools.py`
   - Custom tools go in `app/tools/` directory
   - Must extend `crewai.tools.BaseTool`
   - Use Pydantic v1 models for `args_schema` (CrewAI requirement)

6. **Knowledge Sources:**
   - Validate knowledge source IDs before use
   - Handle missing knowledge sources gracefully
   - Filter out invalid IDs and update entity if needed

7. **Form Keys Must Be Unique:**
   - Use `rnd_id()` for button keys to avoid conflicts
   - Use entity ID in form keys: `f'form_{self.id}'`
   - Pass `key` parameter when drawing multiple instances of same entity

8. **UI Rerun Triggers:**
   - Call `st.rerun()` after state changes that affect multiple components
   - Don't rerun unnecessarily (performance impact)
   - Use `on_change` callbacks for form elements when possible

### Common Tasks

**Adding a new LLM provider:**
1. Add environment variable loading in `llms.py:load_secrets_from_env()`
2. Add check in `llms.py:llm_providers_and_models()` to detect if configured
3. Create `create_<provider>_llm()` function
4. Update `create_llm()` to route to new provider
5. Update `.env_example` with new keys
6. Update README.md with provider information

**Adding a custom tool:**
1. Create tool class in `app/tools/YourTool.py` extending `BaseTool`
2. Define Pydantic v1 `args_schema` for parameters
3. Implement `_run()` method
4. Register in `my_tools.py:TOOL_CLASSES`: `"YourTool": (YourToolClass, False)`
5. Tool will appear in UI automatically

**Adding a new page:**
1. Create `app/pg_yourpage.py` with class `PageYourPage`
2. Implement `draw(self)` method
3. Import in `app/app.py`
4. Add to `pages()` dictionary: `'Your Page': PageYourPage()`
5. Page appears in sidebar automatically

**Modifying database schema:**
- The schema is generic and flexible (JSON data column)
- To add fields to an entity: Add to model `__init__()`, update save/load in `db_utils.py`
- Breaking changes: Users must delete `crewai.db` (document in PR/release notes)

### Security Considerations

**TLS/SSL Verification Disabled:**
- This is intentional for the "Insecure" edition
- `ssl_override.py:disable_ssl_verification()` is called on app startup
- Do NOT remove or "fix" this - it's the primary feature
- If creating a "secure" fork, create separate branch/repo

**API Key Storage:**
- Keys stored in `.env` file (not committed)
- Loaded into session state on app start
- Never log or expose keys in UI
- Use `st.text_input(type="password")` for key inputs in UI

**SQL Injection:**
- Using SQLAlchemy with parameterized queries (safe)
- Never concatenate user input into SQL strings

**Code Execution Risks:**
- Custom tools can execute arbitrary code
- Code interpreter tool executes user Python code
- This is expected functionality - document risks in UI

### Testing and Validation

**No automated tests exist** in this repository. When making changes:

1. **Manual testing checklist:**
   - Create, edit, delete entities (agents, tasks, crews, tools)
   - Run a crew with various configurations
   - Test with multiple LLM providers
   - Verify knowledge source integration
   - Test import/export functionality
   - Check cascade deletes don't break other entities

2. **Browser console:**
   - Watch for JavaScript errors
   - Streamlit may show warnings about session state

3. **Python console:**
   - Run with `streamlit run app/app.py`
   - Watch for Python exceptions in terminal
   - CrewAI framework may show verbose output

### Debugging Tips

**Streamlit reruns frequently** - use caching where appropriate:
```python
@st.cache_data
def expensive_operation():
    ...
```

**Session state inspection:**
```python
st.write(ss)  # Dump entire session state
st.write(ss.agents)  # Check specific key
```

**Database inspection:**
```bash
sqlite3 crewai.db
sqlite> SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type;
sqlite> SELECT * FROM entities WHERE entity_type='agent';
```

**LLM provider issues:**
- Check environment variables are loaded: `st.write(ss.env_vars)`
- Verify API keys are valid (test with curl/postman)
- Check `llm_providers_and_models()` output
- Look for SSL errors (should not happen with ssl_override)

**Common errors:**
- `KeyError` on session state: Use `.get()` with default value
- `AttributeError` on entity: Check entity is fully initialized
- LLM fails: Verify API key, check rate limits, ensure model name is correct
- Database locked: Close other connections to SQLite file

### Code Style and Conventions

**Python style:**
- No strict linting enforced
- Generally follows PEP 8
- Imports: Standard library → Third party → Local modules
- Use type hints where helpful but not required

**Naming conventions:**
- Classes: PascalCase (`MyAgent`, `PageCrews`)
- Functions/methods: snake_case (`save_entity`, `get_crewai_agent`)
- Constants: UPPER_SNAKE_CASE (`TOOL_CLASSES`, `DB_URL`)
- Private methods: prefix with `_` (`_run`, `_get_env_var`)

**Streamlit UI:**
- Use `st.form()` for complex inputs with submit button
- Use `on_change` callbacks for immediate updates
- Expanders for collapsible sections
- Columns for side-by-side layout
- Containers with `border=True` for grouped elements

**Error handling:**
- Show user-friendly messages with `st.warning()` or `st.error()`
- Log detailed errors to console with `print()` or `st.exception()`
- Gracefully degrade when optional features unavailable

### Git and Version Control

**Branches:**
- Development happens on feature branches prefixed with `claude/`
- Push to: `claude/claude-md-mifbhif5sezvuqz8-017vQ95xtaFaAfCMfvU4XKZN` (current session)

**Commits:**
- Write clear, descriptive commit messages
- Reference issue numbers if applicable
- Keep commits focused on single logical change

**Important files not to commit:**
- `.env` (contains secrets)
- `crewai.db` (user data)
- `venv/` or `miniconda/` (installation directories)
- `__pycache__/` directories
- `.pyc` files

### Performance Considerations

**Database:**
- SQLite is single-threaded - consider PostgreSQL for multi-user deployments
- JSON serialization on every save - keep entity data reasonably sized

**Streamlit:**
- Entire script reruns on every interaction
- Use `@st.cache_data` for expensive operations
- Minimize database queries in loops
- Avoid loading large data into session state

**LLM Calls:**
- Can be slow (seconds to minutes)
- Crew runs in background thread (via `pg_crew_run.py`)
- Results saved to database for later viewing

## Project-Specific Context

### Why "Insecure"?
This is a fork/variant specifically for corporate environments where:
- SSL/TLS inspection proxies intercept HTTPS traffic
- Self-signed certificates are common
- Standard Python applications fail with certificate errors

The solution: Globally disable certificate verification. This is **intentional** and documented.

### CrewAI Integration
This app is a UI wrapper around the CrewAI framework:
- CrewAI handles agent orchestration, task execution, and LLM interactions
- This app provides: UI, persistence, multi-crew management, tool configuration
- CrewAI version pinned to avoid breaking changes: `crewai==0.165.1`

### LangChain Dependency Management
Carefully pinned versions to avoid resolver conflicts:
- All LangChain packages share `langchain-core<0.4` range
- Provider SDKs compatible with this core version
- CrewAI-Tools pinned to avoid `pypdf` conflicts with Embedchain

### Known Limitations
- No multi-user support (session state is per-browser)
- No authentication/authorization
- SQLite doesn't support true concurrent writes
- No undo/redo functionality
- No automated backups (users must export crews)

## Useful Reference Points

**Entry point:** `app/app.py:main()` (line 53)
**Session state initialization:** `app/app.py:load_data()` (line 32)
**Database initialization:** `app/db_utils.py:initialize_db()` (line 39)
**SSL override:** `app/ssl_override.py:disable_ssl_verification()` (line 19)
**LLM provider detection:** `app/llms.py:llm_providers_and_models()` (implementation in full file)
**Agent creation:** `app/my_agent.py:get_crewai_agent()` (line 41)
**Crew execution:** `app/pg_crew_run.py` (full file)
**Tool registry:** `app/my_tools.py:TOOL_CLASSES` (in file)
**Cascade delete logic:** `app/my_crew.py:analyze_dependencies()` (line 356)

## Quick Start for AI Assistants

When asked to work on this codebase:

1. **Understand the request:** What entity (agent/task/crew/tool) or feature is involved?
2. **Locate relevant files:** Use patterns above (my_*.py for models, pg_*.py for UI)
3. **Check dependencies:** How does this change affect other entities?
4. **Update model:** Modify `my_*.py` class and `__init__()` parameters
5. **Update database:** Modify save/load functions in `db_utils.py`
6. **Update UI:** Modify corresponding `pg_*.py` draw methods
7. **Test manually:** Create → Edit → Save → Delete → Verify cascade behavior
8. **Commit with clear message:** Describe what changed and why

When uncertain:
- Read the source file (they're well-structured and commented)
- Check how similar features are implemented
- Test incrementally
- Ask user for clarification on ambiguous requirements

## Additional Resources

- **CrewAI Documentation:** https://docs.crewai.com/
- **Streamlit Documentation:** https://docs.streamlit.io/
- **LangChain Documentation:** https://python.langchain.com/
- **Original CrewAI Studio:** https://github.com/strnad/CrewAI-Studio

---

**Last Updated:** 2025-11-26
**Repository:** https://github.com/taylorelley/CrewAI-Studio-Insecure
**Branch:** claude/claude-md-mifbhif5sezvuqz8-017vQ95xtaFaAfCMfvU4XKZN
