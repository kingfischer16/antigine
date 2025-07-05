# Core Artifacts
Data collections and deliverables that form the input, output, or intermediate data packages in Antigine.

| Artifact | Description | Location |
| -------- | ----------- | -------- |
| Project Codebase | The codebase of the game project being developed. | GitHub repository for the game project, `source` folder. |
| Feature Ledger | A directory structure that contains files for each feature: `request.md` (the feature request from the user or ProductionManager), `fip.md` (the final, approved FIP), `adr.md` (architectural design record, a concise summary of the architectural impact, generated after implementation validation). Each feature will also have an entry in the `ledger.json` master file. | A top level folder `.antigine/ledger/` in the game project repository, one folder per feature. | 
| Engine Documentation | The source of documentation for the game engine being used, e.g. the Ursina Engine. | The game engine website. |
| Engine API Reference | The source of documentation for the game engine API, e.g. the Ursina Engine API reference. | The game engine website. |
| Engine Codebase | The source code for the game engine being used, e.g. the Ursina Engine. | Either the game engine GitHub repo or the local directory where the game engine is installed. |
