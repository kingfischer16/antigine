# Antigine Repository Structure

```
antigine/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
├── .devcontainer
│   └── devcontainer.json   
│
├── antigine/                       # Main package
│   ├── __init__.py
│   ├── main.py                     # Entry point / CLI
│   └── config.py                   # Configuration management
│
├── core/                           # Core infrastructure (keep your existing)
│   ├── __init__.py
│   ├── chains.py                   # LangChain chains
│   ├── prompts.py                  # Prompt templates
│   ├── models.py                   # LLM model configurations
│   ├── state.py                    # LangGraph state definitions
│   └── orchestrator.py             # Main LangGraph orchestrator
│
├── managers/                       # State and context managers (expand your existing)
│   ├── __init__.py
│   ├── state_manager.py            # StateManager class
│   ├── context_manager.py          # Codebase RAG (ContextManager)
│   ├── adr_manager.py              # ADR management
│   └── project_manager.py          # Project setup/scaffolding helpers
│
├── agents/                         # All specialist agents
│   ├── __init__.py
│   ├── base_agent.py               # Base agent class/interface
│   ├── project_scaffolder.py       # Project Scaffolder agent
│   ├── technical_architect.py      # Technical Architect agent
│   ├── implementation_planner.py   # Implementation Planner agent
│   ├── implementation_validator.py # Implementation Validator agent
│   └── review_committee/           # Review Committee agents
│       ├── __init__.py
│       ├── fidelity_analyst.py
│       └── feasibility_analyst.py
│
├── tools/                          # All tools (RAG and custom)
│   ├── __init__.py
│   ├── base_tool.py                # Base tool class/interface
│   ├── rag/                        # RAG-related tools
│   │   ├── __init__.py
│   │   ├── engine_context_rag.py   # Composite EngineContextRAG
│   │   ├── engine_docs_rag.py      # EngineDocumentationRAG
│   │   ├── engine_api_rag.py       # EngineAPIReferenceRAG
│   │   ├── engine_code_rag.py      # EngineCodebaseRAG
│   │   └── retriever_utils.py      # Shared RAG utilities
│   ├── validation/                 # Validation tools
│   │   ├── __init__.py
│   │   ├── contract_checker.py     # Tree-sitter contract validation
│   │   └── code_analyzer.py        # Code analysis utilities
│   └── scaffolding/                # Project scaffolding tools
│       ├── __init__.py
│       ├── project_generator.py    # Project structure generation
│       └── template_engine.py      # Template processing
│
├── templates/                      # Prompt templates and code templates
│   ├── prompts/                    # Agent prompt templates
│   │   ├── __init__.py
│   │   ├── architect_prompts.py
│   │   ├── planner_prompts.py
│   │   ├── validator_prompts.py
│   │   └── review_prompts.py
│   └── code/                       # Code generation templates
│       ├── ursina_project/         # Ursina project templates
│       │   ├── main.py.jinja2
│       │   ├── config.py.jinja2
│       │   └── ...
│       └── fip/                    # FIP templates
│           └── fip_template.md.jinja2
│
├── schemas/                        # Data models and schemas
│   ├── __init__.py
│   ├── state_schemas.py            # LangGraph state schemas
│   ├── fip_schemas.py              # FIP structure schemas
│   ├── adr_schemas.py              # ADR structure schemas
│   └── validation_schemas.py       # Validation result schemas
│
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── file_utils.py               # File operations
│   ├── git_utils.py                # Git operations
│   ├── parsing_utils.py            # Tree-sitter parsing utilities
│   ├── vector_store_utils.py       # Vector store operations
│   └── logging_utils.py            # Logging configuration
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration
│   ├── test_agents/
│   │   ├── test_architect.py
│   │   ├── test_planner.py
│   │   └── ...
│   ├── test_tools/
│   │   ├── test_rag_tools.py
│   │   ├── test_validation_tools.py
│   │   └── ...
│   ├── test_managers/
│   │   ├── test_state_manager.py
│   │   └── ...
│   └── fixtures/                   # Test data
│       ├── sample_codebase/
│       └── sample_adrs/
│
├── scripts/                        # Utility scripts
│   ├── setup_vector_stores.py      # Initialize vector stores
│   ├── update_engine_docs.py       # Update Ursina documentation
│   └── dev_server.py               # Development server/CLI
│
└── docs/                           # Documentation
    ├── architecture.md
    ├── agents.md
    ├── tools.md
    ├── api_reference.md
    └── development_guide.md
```

## Key Design Principles

### 1. **Separation of Concerns**
- **agents/**: Pure agent logic, focused on their specific roles
- **tools/**: Reusable tools that agents can use
- **managers/**: Infrastructure for state and context management
- **core/**: Orchestration and core LangChain/LangGraph components

### 2. **Scalability**
- Each agent gets its own file
- Tools are categorized by function (RAG, validation, scaffolding)
- Templates are separated from logic
- Clear separation between prompts and code templates

### 3. **Testability**
- Comprehensive test structure mirroring main code
- Fixtures for test data
- Clear separation of concerns makes unit testing easier

### 4. **Maintainability**
- Related functionality grouped together
- Base classes for common patterns
- Utils for shared functionality
- Schemas for data validation

### 5. **Development Workflow**
- Scripts for common development tasks
- Clear documentation structure
- Examples and fixtures for development

## Migration Path

Since you already have `core/` and `managers/`, you can:

1. **Keep your existing structure** - it fits well into this design
2. **Gradually expand** - add `agents/` and `tools/` as you build them
3. **Refactor incrementally** - move things to more specific locations as the codebase grows

## File Naming Conventions

- **Snake_case** for Python files and directories
- **Descriptive names** that clearly indicate purpose
- **Consistent suffixes**: `_agent.py`, `_tool.py`, `_manager.py`, `_utils.py`
- **Group related files** in subdirectories when there are 3+ related files
