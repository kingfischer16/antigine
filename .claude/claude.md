# Claude.md: AI Guide for Antigine

This file is the primary guide for our AI assistant, Claude Code. It contains essential project information, commands, and rules to ensure effective and safe collaboration. Please review it before making changes.

## 1. Project Overview

- **Project:** Antigine
- **Description:** Antigine is a multi-agent AI system designed to act as an expert development partner for building games by writing only the code you need, without the bloat of traditional game engines. Antigine will initially be a CLI application, possibly later being given a web app front end. Antigine mirrors some aspects of Claude Code but with specific application towards video game development. The system is language and framework agnostic, allowing users to develop games in any programming language and framework combination.
- **Technology Stack:** Python (project language), LangGraph (multi-agent framework), various LLM APIs (OpenAI, Google, etc.)
- **Architecture:** 
```
antigine/
├── .claude/            # Claude project documentation
├── core/               # Core system components (models, prompts)
├── managers/           # High-level system managers
├── notebooks/          # Development and testing notebooks (human use only) 
├── documents/          # Documentation and specifications for the development of the Antigine system
├── templates/          # Templates for table data, schemas, config files
├── tests/              # unit tests for non-API calling functions
└── scripts/            # Utility scripts
```

## 2. Key Commands

Use these commands to work with the repository:

- **Install Dependencies:** `pip install -r requirements.txt && pip install -r requirements-dev.txt`
- **Run Tests:** `python -m unittest discover tests`
- **Run Type Checking:** `mypy .`
- **Run Linting:** `flake8 .`
- **Build Project:** `python -m build` (requires `pyproject.toml` setup - request help if needed)

## 3. Workflow & Style Guide

**Development Workflow:**
1. Create a new feature branch for each feature/functionality
2. Keep feature branches small but complete
3. Plan and review changes thoroughly before implementation (Rule #1)
4. Develop the feature following the multi-agent architecture pattern
5. Add comprehensive unit tests for non-API calling functions
6. Run type checking (`mypy`) and linting (`flake8`) before committing
7. Conduct manual CLI testing to emulate user experience
8. Request human review before implementation (Rule #2)
9. Create pull request after thorough testing
10. Merge after final approval

**Code Style:**
- Follow PEP 8 guidelines for Python code
- Use type hints throughout the codebase, creating custom types as needed
- Include proper docstrings for all functions, classes, and modules
- Add file headers describing contents, intended use, and function

## 4. Project Context & Understanding

**Essential Reading:** Before working on Antigine, always review:
- `README.md` for current project summary
- Files in `documents/` folder for detailed architecture and specifications
- `requirements.txt` and `requirements-dev.txt` for current dependencies (these change frequently)
- Existing code in `core/` and `managers/` for architecture patterns

**Key Project Principles:**
- **Language & Framework Agnosticism:** Antigine assists in developing games in ANY programming language and framework combination
- **Multi-Agent Architecture:** Uses LangGraph with central orchestrators managing state and conditional edges
- **Documentation Generation:** Use Sphinx for automatic project documentation

## 5. Immutable Rules (NON-NEGOTIABLE)

These rules must be followed at all times. Violation of these rules is a critical error.

1. **ALWAYS thoroughly plan and review changes or additions to code before implementation**
2. **ALWAYS ask for a human review before implementing code changes**
3. **NEVER modify or run files in the notebooks/ folder**
4. **ALWAYS refer to Python and LangGraph best practices when creating or changing code**
5. **ALWAYS suggest tests for new functions when tests do not require an API call to an LLM**
6. **NEVER store API keys or sensitive information in any repository folder (public or private)**
7. **ALWAYS implement loop limit counters for all review/iteration loops (default: 3 iterations maximum)**
8. **ALWAYS check requirements.txt and requirements-dev.txt for current dependencies before making assumptions**
9. **ALWAYS use type hints and follow PEP 8 guidelines when writing Python code**
10. **ALWAYS include proper docstrings and file headers for new code**
11. **ALWAYS implement rate limiting mechanisms for API calls to prevent excessive usage**
12. **ALWAYS ensure multi-agent graphs have a central orchestrator managing state and conditional edges**

## 6. Security & API Guidelines

- **API Keys:** Stored as local environment variables, referenced by LLM API calls following best practices
- **Rate Limiting:** Implement appropriate rate limiting for API calls to prevent abuse
- **Environment Variables:** All sensitive configuration uses environment variables with `.env` files (never committed to repo)
- **Multi-Agent Coordination:** Each graph has a central orchestrator managing state, conditional edges, and human operator approval processes
- **Loop Management:** All loops require limit counters (default: 3 iterations) to prevent infinite cycles

---

**Note:** This file provides development guidelines. For complete project understanding, refer to the main README.md and documentation in the `documents/` folder.
