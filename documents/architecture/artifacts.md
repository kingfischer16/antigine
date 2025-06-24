# Core Artifacts
Data collections and deliverables that form the input, output, or intermediate data packages in AFIE.

| Artifact | Description | Location |
| -------- | ----------- | -------- |
| Project Codebase | The codebase of the game project being developed. | GitHub repository for the game project, `source` folder. |
| Feature Request | A request developed by the human user and a qualified chat agent (e.g. "production manager") that is the input for the technical architect to being work developing the FIP. Complete with details and acceptance criteria. | Github repository for the game project, `feature_requests` folder, one feature request per file. |
| Feature Implementation Package (FIP) | The main output of the AFIE system, a GitHub Copilot-optimized markdown recipe, complete with engine, API, and codebase context, delivered to the human operator. | GitHub repository for the game project, `fip` folder. |
| Architectural Decision Record (ADR) | A summary of the feature that has been implemented. Does not contain complete details or context, unless the implementation deviated in a way from the FIP. Links to the FIP and feature request for traceability. Note: the "feature requests" and ADR could be combined into a single directory with notes and status (e.g. "requested", "implemented"), this is worth considering. | GitHub repository for the game project, `adr` folder. |
| Engine Documentation | The source of documentation for the game engine being used, e.g. the Ursina Engine. | The game engine website. |
| Engine API Reference | The source of documentation for the game engine API, e.g. the Ursina Engine API reference. | The game engine website. |
| Engine Codebase | The source code for the game engine being used, e.g. the Ursina Engine. | Either the game engine GitHub repo or the local directory where the game engine is installed. |
