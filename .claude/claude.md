# Antigine: Agentic Anti-Engine Game Development Tool

## Project Overview

**Antigine** is a multi-agent AI system designed to accelerate game development by automating planning, architecture, implementation, and documentation phases. It operates on an "anti-engine" philosophy, building games from the ground up using minimal, purpose-built code without traditional game engine bloat.

**Core Philosophy:** The codebase is the single source of truth. Each feature integration maintains a functional, playable game state through incremental development.

## Development Context for Claude Code

This project requires understanding of:
- **Multi-agent orchestration** using LangChain/LangGraph
- **Pydantic state management** for workflow coordination
- **Prompt engineering** for specialized AI agents
- **Love2D/Lua** as the target game development framework
- **SQLite database** integration for project metadata

**Current Working Directory:** All development happens in the repository root with organized subdirectories.

## Current Status & Development Phase

- **Phase:** Early development - core implementation pipeline tested
- **Working Components:** 4 of 9 agents (Technical Architecture Writer/Reviewer, Implementation Plan Writer/Reviewer)
- **Framework:** Initially targeting Lua/Love2D with architecture for future expansion
- **Current Testing:** Complex feature requests to stress-test agent capabilities
- **Active Development:** `notebooks/testing_core_loop_architecture.ipynb` contains the working implementation

## Project Structure

```
antigine/
├── .claude/                    # Claude project documentation
├── .antigine/                  # Generated project artifacts (not in repo)
├── core/                       # Core system components
│   ├── chains.py              # LangChain chain definitions
│   ├── models.py              # Data models and state classes
│   └── prompts.py             # Agent prompts and templates
├── managers/                   # High-level system managers
│   ├── ProjectLedgerManager.py # Database and feature management
│   └── ProjectSetupManager.py  # Project initialization
├── notebooks/                  # Development and testing notebooks
│   ├── testing_core_loop_architecture.ipynb # 🎯 CURRENT WORKING IMPLEMENTATION
│   └── test_chains.ipynb      # Chain testing
├── documents/                  # Documentation and specifications
│   ├── architecture/          # Technical architecture docs
│   │   └── agent_specifications.md # Detailed agent specs
│   └── design/                # Design documents and prompts
├── templates/                  # JSON templates and examples
└── scripts/                   # Utility scripts
```

## System Architecture

### Multi-Agent Design (9 Agents Total)

**Planning Phase (3 agents):** 🚧 TODO
1. **GDD Creator** - Interactive chat for Game Design Document creation
2. **Module Planner** - Converts GDD into architectural modules  
3. **Feature Request Writer** - Creates implementable feature requests

**Implementation Phase (6 agents):**
4. **Technical Architecture Writer** - Designs technical specifications ✅ WORKING
5. **Technical Architecture Reviewer** - Validates feasibility and scope ✅ WORKING
6. **Implementation Plan Writer** - Creates detailed implementation plans ✅ WORKING
7. **Implementation Plan Reviewer** - Ensures modularity and integration ✅ WORKING
8. **Coder** - Implements features and resolves build errors 🚧 NEXT PRIORITY
9. **Code Reviewer** - Final code quality review 🚧 TODO

### Key Technical Components

**State Management:**
- `WorkflowState` (Pydantic models) in `core/models.py`
- Review classes with structured scoring (1-5 scale, ≥4 for approval)
- LangGraph integration for stateful workflows

**Database Design:**
- `ledger.db` (SQLite) for feature metadata and relationships
- `.antigine/` folder for generated markdown files
- Project registration in local app data

**Agent Orchestration:**
- Located in `notebooks/testing_core_loop_architecture.ipynb`
- StateGraph with conditional review loops
- Maximum 3 revision cycles before human escalation

## Development Guidelines & Patterns

### Code Style
- **Pydantic Models** for all state management and structured data
- **LangGraph** for orchestration and stateful workflows  
- **Type Hints** throughout for better IDE support
- **Modular Design** with clear agent separation

### Agent Development Pattern
1. Define agent in `core/prompts.py` with specific role and output format
2. Create node function in workflow with error handling
3. Add review loop logic with scoring criteria
4. Test in isolation before integrating into main workflow
5. Validate with complex feature requests

### Prompt Engineering Best Practices
- **Framework-Specific Context** - All prompts include Love2D/Lua context
- **Structured Output Requirements** with JSON schemas where applicable
- **Review Criteria** explicitly defined with 1-5 scoring rubrics
- **Error Handling** for malformed responses and edge cases
- **Context Integration** - Previous drafts and feedback in revision cycles

## Current Priorities & Next Steps

### 🎯 IMMEDIATE (Current Sprint)
1. **Complete Coder Agent** - Implement the code generation agent in the workflow
2. **Add Code Reviewer Agent** - Final validation step for generated code
3. **Fix Implementation Plan Review Loop** - Currently disabled for debugging
4. **Test Small Feature Implementation** - Validate incremental development philosophy

### 📋 SHORT TERM
1. **Planning Phase Agents** - GDD Creator, Module Planner, Feature Request Writer
2. **Database Integration** - Complete `ProjectLedgerManager.py` implementation
3. **CLI Interface** - User interaction and project management tools

### 🔮 MEDIUM TERM
1. **Love2D Build Integration** - Compilation and error handling
2. **Version Control Integration** - Git workflow automation
3. **Evaluation System** - Automated testing and quality metrics

## Key Files for Development

### 🔥 Critical Files (Most Important)
- `notebooks/testing_core_loop_architecture.ipynb` - **Main working implementation**
- `core/models.py` - **State classes and workflow data structures**
- `core/prompts.py` - **All agent prompt templates**
- `documents/architecture/agent_specifications.md` - **Complete agent specifications**

### 📚 Reference Files
- `core/chains.py` - LangChain chain definitions
- `managers/ProjectLedgerManager.py` - Database operations
- `templates/` - JSON templates and configuration examples

## Integration & Dependencies

### External Dependencies
- **LangChain/LangGraph** - Agent orchestration (`pip install langgraph`)
- **Google Gemini** - Currently using `gemini-2.5-flash-lite-preview-06-17`
- **SQLite** - Local database (built into Python)
- **Pydantic** - Data validation and settings management
- **Love2D/Lua** - Target framework for game development

### Environment Setup
```bash
pip install langgraph pydantic sqlite3 google-generativeai
# Love2D installation varies by platform
```

## Success Metrics & Quality Gates

### Quality Standards
- All reviewer agents require scores ≥4 for approval
- Maximum 3 revision cycles before human escalation  
- Generated code must be syntactically valid Lua/Love2D
- Features must integrate without breaking existing functionality
- Maintain incremental, playable game state throughout development

### Development Velocity Targets
- Agent implementation: 1-2 days per agent
- Complex feature requests: Complete in <30 minutes
- Full pipeline validation: <1 hour

## Common Development Tasks

### Adding a New Agent
1. Define prompt template in `core/prompts.py`
2. Create Pydantic model for agent output in `core/models.py`
3. Implement node function with error handling
4. Add to workflow graph in main notebook
5. Test with sample inputs

### Testing Agent Changes
1. Use `notebooks/test_chains.ipynb` for isolated testing
2. Test with complex feature requests (inventory systems, dialogue)
3. Validate review loop logic and scoring
4. Ensure structured output compliance

### Debugging Workflow Issues
1. Check StateGraph node connections
2. Validate Pydantic model schemas
3. Review LangChain prompt templates
4. Test agent responses in isolation
5. Check database state consistency

This project represents a sophisticated AI orchestration system requiring careful state management, prompt engineering, and iterative development practices. The multi-agent architecture demands understanding of both AI prompt design and software engineering principles.
