# Antigine: The Agentic Anti-Engine Game Development Tool

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Integration-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Antigine is a multi-agent AI system designed to act as an expert development partner for building games by writing only the code you need, without the bloat of traditional game engines.**

It is not a "game-from-prompt" generator; it is a system that accelerates development by automating the planning, architecture, implementation, and documentation phases, allowing a human developer to focus on creative direction and playtesting. This is intended to be an "engine-less" alternative to the major game engines, where you build your game from the ground up using a chosen language and framework, writing only the features and code needed to make your game work without all the bloat of modern "do everything" engines.

## Core Philosophy: The Agentic "Anti-Engine"

Antigine (a portmanteau of "anti-engine") operates on an **agile, iterative philosophy** guided by two complementary principles:

1. **The codebase is the technical source of truth** - What actually runs and plays is what matters
2. **"Follow the fun"** - Playtesting and player feedback drive evolution, not rigid documentation

The system evolves a living, playable game by integrating new features one at a time into the existing, functional codebase. The human's role is to be the Creative Director, providing new feature ideas and changes based on what makes the game more engaging, while the agentic system handles the technical details.

### Key Features
- **Multi-Agent Architecture:** Nine specialized AI agents handle different aspects of development, from GDD creation to code review.
- **Stateful Orchestration:** Uses LangGraph to manage complex workflows with mandatory human review at each stage.
- **Framework Agnostic:** Initially supports Lua/Love2D with architecture designed for future language expansion.
- **Creative Scaffolding:** GDD → Modules → Feature Requests provide initial creative direction, but evolve based on playtesting.
- **Living Codebase:** Each feature integration maintains a functional, playable game state.
- **Playtest-Driven Development:** Features and design evolve based on what's actually fun to play, not rigid planning documents.

## System Architecture

Antigine employs nine specialized AI agents orchestrated through LangChain and LangGraph:

**Planning Phase:**
- **GDD Creator:** Interactive chat agent that creates minimalist Game Design Documents using best practices and probing questions
- **Module Planner:** Breaks down the GDD into high-level architectural modules with feature lists
- **Feature Request Writer:** Creates detailed, implementable feature requests from modules and GDD context

**Implementation Phase:**
- **Technical Architecture Writer:** Designs comprehensive technical specifications for features
- **Technical Architecture Reviewer:** Validates architectural feasibility and scope
- **Implementation Plan Writer:** Creates detailed implementation plans referencing codebase and framework documentation
- **Implementation Plan Reviewer:** Ensures implementation plans are minimal, modular, and integrate correctly
- **Coder:** Writes and updates code, compiles, and resolves build errors with internet access for documentation
- **Code Reviewer:** Final review for syntax, best practices, and code quality

All agents operate with **mandatory human review** at each stage, allowing operators to approve, request changes, or cancel before proceeding.

## How it works

Antigine assists game designers at 3 critical phases of development:

### 1. Project Start
At project start, there is no code or documentation present. The user passes a Git repo folder location to Antigine and the system sets up the following:
- **`.antigine` folder -** The folder in the Git repo that contains all Antigine-specific artifacts, e.g. database, configuration files, etc.
- **`ledger.db` -** SQLite database containing feature metadata (ID, name, description, status, dates, parent module), approved documents (feature requests, technical architecture, implementation plans), and feature relationship mappings (dependencies, supersessions).
- **`project_config.json` -** Project configuration specifying language (Lua) and framework (Love2D).
- **Project Registration -** Registers project in local app data for future access.
- **Game Design Document -** Interactive GDD creation process using the GDD Creator agent if none exists.
- **Starter Code -** Framework-appropriate project structure (e.g., `main.lua`, asset folders for Love2D).

### 2. Planning
The Module Planner agent converts the GDD into architectural modules documented in `modules.md`. Each module represents a major game system with associated feature lists.

**Important**: The GDD and modules serve as **creative scaffolding** - they help clarify initial vision but are living documents that evolve based on playtesting feedback. They guide early development but don't constrain later iterations.

The Feature Request Writer agent then creates detailed, implementable feature requests from these modules. Features are designed to be:
- **Small and incremental** for easy review and integration
- **Independently functional** to maintain playable game state
- **Created on-demand** to avoid irrelevant or duplicate work
- **Adaptable** - can be modified or replaced based on gameplay discoveries

Feature requests are stored in `ledger.db` with full metadata and linked to their parent modules and dependencies.

### 3. Implementation
The implementation phase processes individual feature requests through a structured pipeline with mandatory human review at each stage:

1. **Feature Selection** - Choose a feature request from the ledger
2. **Technical Architecture** - Writer creates comprehensive technical specification; Reviewer validates feasibility and scope
3. **Implementation Planning** - Writer creates detailed implementation plan with code snippets; Reviewer ensures modularity and integration compatibility  
4. **Code Writing** - Coder implements the feature, compiles code, and resolves any build errors
5. **Code Review** - Final review for syntax, best practices, and code quality

Each approved document is stored in `ledger.db` and linked to the feature request. The human operator reviews and approves all outputs before progression to the next stage.

## How to use Antigine
1. **Start the CLI** and choose to create a new project or select an existing one
2. **Project Setup**: Provide Git repo folder location and create/import GDD as initial creative foundation
3. **Planning**: Convert GDD to modules, then create feature requests as needed (recommended: one at a time for agile development)
4. **Implementation**: Select a feature and proceed through the 5-stage implementation pipeline, with mandatory human review after each stage
5. **Playtest & Iterate**: Test your game frequently - let player feedback and fun factor guide which features to build next, modify, or abandon

**Remember**: Your GDD and modules are starting points, not contracts. Follow the fun and let your game evolve naturally through the development process.

## Contributing

*TBD*

---
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
