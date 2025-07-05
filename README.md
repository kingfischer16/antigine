# Antigine: The Agentic Anti-Engine Game Development Tool

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Integration-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Antigine is a multi-agent AI system designed to act as an expert development partner for building games by writing only the code you need, without the bloat of traditional game engines.**

It is not a "game-from-prompt" generator; it is a system that accelerates development by automating the planning, architecture, and documentation phases, allowing a human developer to focus on creative ideas, implementation, and playtesting. This is intended to be an "engine-less" alternative to the major game engines, where you build your game from the ground up using a chosen language and framework, writing only the features and code needed to make your game work without all the bloat of modern "do everything" engines.

## Core Philosophy: The Agentic Anti-Engine

Antigine operates on an **agile, iterative philosophy** where the **codebase is the single source of truth**. The system evolves a living, playable game by integrating new features one at a time into the existing, functional codebase. The human's role is to be the Creative Director, providing new feature ideas, and the Lead Implementer, writing the final code based on the AI's expert guidance.

### Key Features
- **Stateful Orchestration:** Uses LangGraph to manage complex, multi-step workflows with review loops and human-in-the-loop interruptions.
- **Code-Aware Context:** Employs a RAG system and Tree-sitter parsing to understand the structure of the existing codebase, providing highly relevant context to its agents.
- **Framework-Specific Expertise:** Leverages a dedicated RAG system trained on framework documentation to provide accurate, idiomatic architectural advice and code.
- **Architectural Consistency:** Maintains an Architectural Decision Record (ADR) to ensure long-term design integrity and prevent architectural drift.
- **Automated Validation:** Includes an API Contract Validator to objectively verify that human implementations match the AI-generated specifications.

## System Architecture

Antigine is composed of three main layers: **Core Infrastructure**, **Specialist Agents**, and **System Artifacts**.

### 1. Core Infrastructure
- **Orchestrator:** The LangGraph state machine that directs the entire workflow.
- **`StateManager`:** The interface to the project's state, parsing the codebase and managing the ADR.
- **`ContextManager` (Codebase RAG):** Provides focused code context to agents.
- **`FrameworkDocRAG`:** Provides expert knowledge about the chosen framework.

### 2. Specialist Agents
- **`Project Scaffolder`:** Initializes a new game project with a clean, runnable structure.
- **`Technical Architect`:** Designs technical solutions for new features.
- **`Review Committee`:** A pair of agents (`Fidelity Analyst` & `Feasibility Analyst`) that validate the architect's plans.
- **`Implementation Planner`:** Translates approved plans into a human-executable Feature Implementation Package (FIP).
- **`Implementation Validator`:** Objectively verifies that the developer's code fulfills the FIP's API contract.

### 3. Core Artifacts
- **The Codebase:** The single source of truth.
- **Architectural Decision Record (ADR):** A directory of Markdown files tracking key architectural choices.
- **Composite Feature Implementation Package (FIP):** The final, structured recipe delivered to the human developer.

## Development Roadmap

The Antigine project will be developed component by component, following the defined learning projects.

- [ ] **Phase 1: Foundational Tools**
  - [ ] Implement `StateManager` with Tree-sitter parsing.
  - [ ] Build and test the `FrameworkDocRAG` system.
- [ ] **Phase 2: Core Agent Logic**
  - [ ] Develop the `Project Scaffolder` agent.
  - [ ] Implement the `Implementation Validator`'s core tool.
- [ ] **Phase 3: LangGraph Integration**
  - [ ] Build the main orchestration graph.
  - [ ] Integrate all agents as nodes within the graph.
- [ ] **Phase 4: Full System Testing**
  - [ ] End-to-end testing with a sample game project.

## Contributing

*TBD*

---
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
