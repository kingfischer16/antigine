# Antigine: The Agentic Anti-Engine Game Development Tool

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Integration-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-orange)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Antigine is a multi-agent AI system designed to act as an expert development partner for building games by writing only the code you need, without the bloat of traditional game engines.**

It is not a "game-from-prompt" generator; it is a system that accelerates development by automating the planning, architecture, implementation, and documentation phases, allowing a human developer to focus on creative direction and playtesting. This is intended to be an "engine-less" alternative to the major game engines, where you build your game from the ground up using a chosen language and framework, writing only the features and code needed to make your game work without all the bloat of modern "do everything" engines.

## Core Philosophy: The Agentic "Anti-Engine"

Antigine (a portmanteau of "anti-engine") operates on an **agile, iterative philosophy** where the **codebase is the single source of truth**. The system evolves a living, playable game by integrating new features one at a time into the existing, functional codebase. The human's role is to be the Creative Director, providing new feature ideas and changes, while the agentic system handles the technical details.

### Key Features
- **Stateful Orchestration:** Uses LangGraph to manage complex, multi-step workflows with review loops and human-in-the-loop interruptions.
- **Code- and Framework-Aware Context:** Ensures relevant technical information is available at the planning and architecture steps.
- **Tiered Project Management:** A central GDD is used as a starter point, which is used to generate conceptual game "modules", which in turn are broken down into a series of feature requests that can be used to .
- **Automated Validation:** Integrated review loops with acceptance criteria for feature architecture and implementation plans.
- **Human-In-The-Loop:** Everytime a document is created, the human operator is requested to review and approve it before the system carries on with registrationa and the next generation steps.

## How it works

Antigine assists game designers at 3 critical phases of development:

### 1. Project Start
At project start, there is no code or documentation present. The user passes a Git repo folder location to Antigine and the system sets up the following:
- **`.antigine` folder -** The folder in the Git repo that contains all Antigine-specific artifacts, e.g. database, configuration files, etc.
- **`ledger.db` -** The database that contains the project management information, e.g. the feature requests, architectural design documents, implementation plans.
- **`project_config.json` -** The project-specific Antigine configuration file, detailing the language and framework.
- **Project Registration -** Centrally registers the project name and location to local app data.
- **Game Design Document -** If you don't already have one, Antigine will walk you through creating a minimalist GDD, suitable for fleshing-out modules in the next step.
- **Starter Code -** Given the GDD, chosen language and framework, Antigine sets up the basic folders and files, e.g. a `main.lua` file and some asset folders when using Lua and Love2D.

### 2. Planning
After the basic setup, Antigine helps breakdown the GDD into modules. These compose the high-level architecture of the game project, ensuring everything in the GDD, as well as all supporting systems needed to realize the game are captured. This results in a `modules.md` document added to the `.antigine` folder, and is referenced periodically to ensure the project is proceeding in the right direction.

The planning stage also encompasses the creation of feature requests. Each module is broken down into a series of small features that are each themselves small enough to be implemented quickly, but result in a working and playable game when finished. The features should be as small as possible so code functionality can be reviewed efficiently and so minimal changes are applied at one time. A series of many small incremental changes is easier to control and manage than massive sweeping code changes, and and bugs or unintended behavior that arises during the implementation can be more easily corrected.

Modules are large architectural concepts that give more detail to that which is described in the GDD. Feature requests are much smaller and can be created as needed. In fact, while the GDD and module documentation can be created at once at the beginning of the project, the individual feature requests can be created one at a time, or even as needed, based on the GDD, modules, and existing code to ensure the latest feature requests describe only necessary and valuable changes and don't duplicate existing functionality. Modules can describe a list of features to be requested, but do not contain any details for these features.

Feature requests are stored in the `ledger.db` database, given a status and metadata, and linked to their parent module and dependencies on other features. 

### 3. Implementation
Using the feature request created in the planning stage, we create a sequence of planning documents that progress us towards finally implementing the code. At each stage, after the document has been produced by the writer agent and approved by the reviewer agent, the human is given a chance to review the 
- **Choose a Feature Request -** Feature requests defined and stored in the ledger in the planning phase can be selected for development.
- **Technical Architectural Specification -** Feature architecture is planned in detail to fully capture the requested functionality. The architectural specification does not specify how the feature is to be implemented, rather it fully describes all aspects of the feature and how it connects to existing systems. This results in a technical architecture document corresponding 1-to-1 to the feature request. 
- **Technical Architecture Review -** The technical architecture document is reviewed to ensure it is feasible within the chosen programming language and framework for the game project, and that it adequately describes the functionality of the requested feature without going beyond what was requested. The approved techncial architecture document is added to the `ledger.db` database and linked to the feature request.
- **Implementation Planning -** Given the approved technical architecture another agent creates the feature implementation plan, which is the description of the actual implementation. Note that this is not yet the code implementation, though this document may contain code snippets. This agent references the actual codebase as well as language and framework and API documentation to create a detailed implementation plan for how to actually create and integrate the code to bring this feature to life. The intention of this document is to be passed to the last agent (the coding agent) which is expected to have the proficiency level of a junior developer.
- **Implementation Plan Review -** The implementation plan is reviewed against the feature request and the technical architecture to ensure that the requested feature is going to provide the requested functionality. This review agent also ensures that the implementation is minimalist and modular, and that it will integrate correctly with the existing codebase. The approved implementation plan is added to the `ledger.db` database and linked to the feature request.
- **Coder -** This agent takes the implementation plan, reviews the codebase, and forumlates the new code. This results in updates to existing files or the creation of new files, with the changes provided to the human operator before being written. This stage, in addition to actually writing code, will compile the code. The agent has access to build tools for the language and framework. Any compile errors that are encountered will be sent back to this agent and solved during the agent coding session. This agent also has access to internet search to solve issues, and to search framework and API documentation.
- **Code Review -** Finally, before the changes are commited to master branch, a code review agent reviews the code for syntax, best practices, convention consistency, as well as duplicate/unecessary/deprecated code that may be left over from a previous feature or refactor. A final human operator review is requested before the operator merges the pull request (handled completely by the operator).

## How to use Antigine
 1. Start the CLI
 2. Chose to either create a new project or select an existing project (as registered in the local app data folder) and add the git repo folder and GDD (or create one)
 3. If project is new, proceed with converting GDD to modules and feature requests. It is recommended to only plan a few feature requests (or preferably one at time) before implementing features so as to not have irrelevant feature requests in the queue. We work agile.
 4. Select a feature to develop and have the system proceed through the Implementation phase. Antigine will ask for human operator review after each review agent stage and request to proceed, or the operator can request changes if needed, or cancel the implementation completely. This stage ends in the actual code implementation.

## Contributing

*TBD*

---
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
