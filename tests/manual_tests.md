# Manual Test Suite for Antigine CLI

This document contains manual tests for Antigine CLI functionality that cannot be easily automated. These tests should be run by developers to ensure the interactive components work correctly.

## Prerequisites

```bash
# Set up development environment
export PYTHONPATH="D:\GitProjects\antigine"  # or your actual path
cd "D:\GitProjects\antigine"
```

## Test Categories

- [CLI Help and Version](#cli-help-and-version)
- [Project Initialization](#project-initialization)
- [Project Status and Information](#project-status-and-information)
- [Configuration Management](#configuration-management)
- [Feature Management](#feature-management)
- [GDD Creator Agent](#gdd-creator-agent)
- [Feature Request Workflow](#feature-request-workflow)
- [Error Handling](#error-handling)
- [Cross-Platform Compatibility](#cross-platform-compatibility)

---

## CLI Help and Version

### Test 1.1: Main Help Display
**Description:** Verify main help message displays all available commands
**Command:**
```bash
python -c "from antigine.run import main; main(['--help'])"
```
**Expected Output:**
```
usage: antigine [-h] [--version] <command> ...

The Agentic Anti-Engine Game Development Tool

positional arguments:
  <command>   Available commands
    init      Initialize a new Antigine project
    status    Show project status and statistics
    feature   Feature management commands
    config    View and manage project configuration

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit

Examples:
  antigine init                     Initialize a new project
  antigine status                   Show project status
  antigine feature list             List all features
  antigine feature show <id>        Show feature details
```

### Test 1.2: Version Display
**Description:** Verify version information is displayed correctly
**Command:**
```bash
python -c "from antigine.run import main; main(['--version'])"
```
**Expected Output:**
```
antigine 0.1.0
```

### Test 1.3: Init Command Help
**Description:** Verify init command help shows new language argument
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--help'])"
```
**Expected Output:**
```
usage: antigine init [-h] [--name NAME] [--language LANGUAGE]
                     [--tech-stack TECH_STACK]

options:
  -h, --help            show this help message and exit
  --name NAME           Project name (interactive prompt if not provided)
  --language LANGUAGE   Programming language (e.g. 'Lua', 'Python', 'C++',
                        'C') - interactive prompt if not provided
  --tech-stack TECH_STACK
                        Game tech stack - single framework (e.g. 'Love2D') or
                        multiple libraries separated by '+' (e.g.
                        'SDL2+OpenGL+GLM')
```

### Test 1.4: Feature Subcommand Help
**Description:** Verify feature subcommand help works
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', '--help'])"
```
**Expected Output:**
```
usage: antigine feature [-h] <operation> ...

positional arguments:
  <operation>  Feature operations
    list       List features
    show       Show detailed feature information

options:
  -h, --help   show this help message and exit
```

---

## Project Initialization

### Test 2.1: Basic Project Initialization with All Args
**Description:** Initialize a new project with all parameters provided via command line
**Setup:**
```bash
mkdir "D:\TestProjects\AntigineManualTest1"
cd "D:\TestProjects\AntigineManualTest1"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'TestGame', '--language', 'Lua', '--tech-stack', 'Love2D'])"
```
**Expected Output:**
```
[INFO] Initializing Antigine project 'TestGame' in D:\TestProjects\AntigineManualTest1
[INFO] Tech Stack: Love2D
[INFO] Creating project folders...
[INFO] Configuring project...
[INFO] Initializing project ledger...
[OK] Successfully initialized Antigine project 'TestGame'!
[INFO] Next steps:
[INFO]   1. Run 'antigine status' to view project information
[INFO]   2. Create your first feature with 'antigine feature create'
```
**Verify:** Check that `.antigine` folder and `main.lua`, `conf.lua` files are created

### Test 2.2: C++ Project with Multiple Libraries
**Description:** Initialize a C++ project with complex tech stack
**Setup:**
```bash
mkdir "D:\TestProjects\AntigineManualTest2"
cd "D:\TestProjects\AntigineManualTest2"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'My3DGame', '--language', 'C++', '--tech-stack', 'SDL2+OpenGL+GLM+Assimp'])"
```
**Expected Output:**
```
[INFO] Initializing Antigine project 'My3DGame' in D:\TestProjects\AntigineManualTest2
[INFO] Tech Stack: SDL2+OpenGL+GLM+Assimp
[INFO] Creating project folders...
[INFO] Configuring project...
[INFO] Initializing project ledger...
[OK] Successfully initialized Antigine project 'My3DGame'!
[INFO] Next steps:
[INFO]   1. Run 'antigine status' to view project information
[INFO]   2. Create your first feature with 'antigine feature create'
```
**Verify:** Check that C++ project structure is created with `CMakeLists.txt`, `src/main.cpp`, and appropriate asset folders

### Test 2.3: Interactive Language and Tech Stack Selection
**Description:** Test the interactive prompts for language and tech stack selection with text input validation
**Setup:**
```bash
mkdir "D:\TestProjects\AntigineManualTest3"
cd "D:\TestProjects\AntigineManualTest3"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'InteractiveGame'])"
```
**Interactive Steps:**
1. When prompted for programming language, enter `2` (Python)
2. When prompted for tech stack, enter `Pygame`

**Expected Output:**
```
Please select a programming language for your project:
  1. Lua
  2. Python
  3. C++  
  4. C

Select programming language
Enter choice [1-4]: 2

Available libraries for Python:
  1. Pygame - Cross-platform set of Python modules for writing video games
  2. NumPy - Fundamental package for scientific computing with Python

You can specify:
  - A single library (e.g., 'Love2D', 'Pygame', 'SDL2')
  - Multiple libraries separated by '+' (e.g., 'SDL2+OpenGL+GLM')

Enter tech stack for Python: Pygame
✓ Recognized library: Pygame

[INFO] Initializing Antigine project 'InteractiveGame' in D:\TestProjects\AntigineManualTest3
[INFO] Tech Stack: Pygame
[INFO] Creating project folders...
[INFO] Configuring project...
[INFO] Initializing project ledger...
[OK] Successfully initialized Antigine project 'InteractiveGame'!
[INFO] Next steps:
[INFO]   1. Run 'antigine status' to view project information
[INFO]   2. Create your first feature with 'antigine feature create'
```
**Verify:** Check that Python project structure is created with `main.py`, `requirements.txt`

### Test 2.4: Multiple Library Tech Stack Selection
**Description:** Test selection of multiple libraries for complex tech stacks
**Setup:**
```bash
mkdir "D:\TestProjects\AntigineManualTest4"
cd "D:\TestProjects\AntigineManualTest4"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'ComplexStackTest'])"
```
**Interactive Steps:**
1. When prompted for programming language, enter `3` (C++)
2. When prompted for tech stack, enter `SDL2+OpenGL+GLM`

**Expected Output:**
```
Please select a programming language for your project:
  1. Lua
  2. Python
  3. C++
  4. C

Select programming language
Enter choice [1-4]: 3

Available libraries for C++:
  1. SDL2 - Cross-platform development library for low level access
  2. OpenGL - Graphics rendering API for 2D and 3D graphics
  3. GLM - Mathematics library for graphics programming
  4. Assimp - Asset import library for 3D model loading
  5. stb_image - Image loading/decoding library
  6. Bullet - Physics simulation engine
  7. Dear ImGui - Immediate mode GUI toolkit for debugging

You can specify:
  - A single library (e.g., 'Love2D', 'Pygame', 'SDL2')
  - Multiple libraries separated by '+' (e.g., 'SDL2+OpenGL+GLM')

Enter tech stack for C++: SDL2+OpenGL+GLM
✓ Recognized libraries: SDL2, OpenGL, and GLM

[INFO] Initializing Antigine project 'ComplexStackTest' in D:\TestProjects\AntigineManualTest4
[INFO] Tech Stack: SDL2+OpenGL+GLM
[INFO] Creating project folders...
[INFO] Configuring project...
[INFO] Initializing project ledger...
[OK] Successfully initialized Antigine project 'ComplexStackTest'!
[INFO] Next steps:
[INFO]   1. Run 'antigine status' to view project information
[INFO]   2. Create your first feature with 'antigine feature create'
```

### Test 2.5: Tech Stack Validation and Error Handling
**Description:** Test validation errors and suggestions for incorrect tech stack input
**Setup:**
```bash
mkdir "D:\TestProjects\AntigineManualTest5"
cd "D:\TestProjects\AntigineManualTest5"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'ValidationErrorTest'])"
```
**Interactive Steps:**
1. When prompted for programming language, enter `3` (C++)
2. When prompted for tech stack, enter `invalidlib+SDL2`
3. System should show error and suggestions
4. Enter `SDL2` when prompted again

**Expected Output:**
```
Please select a programming language for your project:
  1. Lua
  2. Python
  3. C++  
  4. C

Select programming language
Enter choice [1-4]: 3

Available libraries for C++:
  1. SDL2 - Cross-platform development library for low level access
  2. OpenGL - Graphics rendering API for 2D and 3D graphics
  3. GLM - Mathematics library for graphics programming
  4. Assimp - Asset import library for 3D model loading
  5. stb_image - Image loading/decoding library
  6. Bullet - Physics simulation engine
  7. Dear ImGui - Immediate mode GUI toolkit for debugging

You can specify:
  - A single library (e.g., 'Love2D', 'Pygame', 'SDL2')
  - Multiple libraries separated by '+' (e.g., 'SDL2+OpenGL+GLM')

Enter tech stack for C++: invalidlib+SDL2
✗ Unrecognized library: 'invalidlib'
Did you mean:
  - SDL2
  - stb_image
Please try again.

Enter tech stack for C++: SDL2
✓ Recognized library: SDL2

[INFO] Initializing Antigine project 'ValidationErrorTest' in D:\TestProjects\AntigineManualTest5
[INFO] Tech Stack: SDL2
[INFO] Creating project folders...
[INFO] Configuring project...
[INFO] Initializing project ledger...
[OK] Successfully initialized Antigine project 'ValidationErrorTest'!
```

### Test 2.6: Case Insensitive Tech Stack Input
**Description:** Test case insensitive matching for tech stack names
**Setup:**
```bash
mkdir "D:\TestProjects\AntigineManualTest6"
cd "D:\TestProjects\AntigineManualTest6"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'CaseInsensitiveTest'])"
```
**Interactive Steps:**
1. When prompted for programming language, enter `c` (matches both "C++" and "C")
2. System should show ambiguous match error  
3. Enter `1` to select first language (Lua)
4. Enter `love2d` (lowercase) for tech stack

**Expected Output:**
```
Please select a programming language for your project:
  1. Lua
  2. Python
  3. C++  
  4. C

Select programming language
Enter choice [1-4]: c
Ambiguous choice. Matches: C++, C

Select programming language
Enter choice [1-4]: 1

Available libraries for Lua:
  1. Love2D - 2D game framework for Lua with built-in physics, audio, and graphics

You can specify:
  - A single library (e.g., 'Love2D', 'Pygame', 'SDL2')
  - Multiple libraries separated by '+' (e.g., 'SDL2+OpenGL+GLM')

Enter tech stack for Lua: love2d
✓ Recognized library: Love2D

[INFO] Initializing Antigine project 'CaseInsensitiveTest' in D:\TestProjects\AntigineManualTest6
[INFO] Tech Stack: love2d
[INFO] Creating project folders...
[INFO] Configuring project...
[INFO] Initializing project ledger...
[OK] Successfully initialized Antigine project 'CaseInsensitiveTest'!
```

### Test 2.7: Project Already Exists Error
**Description:** Verify error when trying to init in existing project
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'AnotherGame'])"
```
**Expected Output:**
```
[ERROR] This directory is already an Antigine project.
[INFO] Use 'antigine status' to view project information.
```

---

## Project Status and Information

### Test 3.1: Status in Valid Project
**Description:** Display status for a properly initialized project
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['status'])"
```
**Expected Output:**
```
================
Project Status: TestGame
================
Total Features: 0

Tech Stack: Love2D
Project Directory: D:\TestProjects\AntigineManualTest1
```

### Test 3.2: Verbose Status
**Description:** Display detailed status information
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['status', '--verbose'])"
```
**Expected Output:**
```
================
Project Status: TestGame
================
Total Features: 0

Tech Stack: Love2D
Project Directory: D:\TestProjects\AntigineManualTest1

Configuration:
  project_name: TestGame
  project_initials: MP
  project_description: This is a sample project template.
  project_version: 0.0.0
  project_repository_url: https://github...
  project_language: Lua
  tech_stack: Love2D
  tech_stack_repository_url: https://github.com/love2d/love
  tech_stack_documentation_url: https://love2d.org/wiki/Main_Page
  tech_stack_api_reference_url: https://love2d.org/wiki/love
  tech_stack_examples_url: https://love2d.org/wiki/Category:Games
```

### Test 3.3: Status Outside Project
**Description:** Verify error when running status outside project
**Setup:**
```bash
mkdir "D:\TestProjects\EmptyFolder"
cd "D:\TestProjects\EmptyFolder"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['status'])"
```
**Expected Output:**
```
[INFO] Run 'antigine init' to initialize a new project.
[ERROR] This directory is not an Antigine project.
```

---

## Configuration Management

### Test 4.1: List All Configuration
**Description:** Display all project configuration values
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['config', '--list'])"
```
**Expected Output:**
```
================
Project Configuration
================
project_name: TestGame
project_initials: MP
project_description: This is a sample project template.
project_version: 0.0.0
project_repository_url: https://github...
project_language: Lua
tech_stack: Love2D
tech_stack_repository_url: https://github.com/love2d/love
tech_stack_documentation_url: https://love2d.org/wiki/Main_Page
tech_stack_api_reference_url: https://love2d.org/wiki/love
tech_stack_examples_url: https://love2d.org/wiki/Category:Games
```

### Test 4.2: Get Specific Configuration Value
**Description:** Retrieve a specific configuration key
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['config', '--get', 'project_name'])"
```
**Expected Output:**
```
TestGame
```

### Test 4.3: Set Configuration Value
**Description:** Update a configuration value
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['config', '--set', 'project_description', 'An awesome manual test game'])"
```
**Expected Output:**
```
[OK] Updated project_description: This is a sample project template. → An awesome manual test game
```

### Test 4.4: Get Non-existent Configuration Key
**Description:** Verify error for invalid configuration key
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['config', '--get', 'nonexistent_key'])"
```
**Expected Output:**
```
[ERROR] Configuration key not found: nonexistent_key
[INFO] Available keys: project_name, project_initials, project_description, project_version, project_repository_url, project_language, tech_stack, tech_stack_repository_url, tech_stack_documentation_url, tech_stack_api_reference_url, tech_stack_examples_url
```

---

## Feature Management

### Test 5.1: List Features (Empty Project)
**Description:** List features in a new project with no features
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', 'list'])"
```
**Expected Output:**
```
[INFO] No features found.
```

### Test 5.2: Show Non-existent Feature
**Description:** Attempt to show details for non-existent feature
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', 'show', 'TG-001'])"
```
**Expected Output:**
```
[ERROR] Feature not found: TG-001
```

### Test 5.3: Show Feature with Invalid ID Format
**Description:** Verify validation of feature ID format
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', 'show', 'invalid-id'])"
```
**Expected Output:**
```
[ERROR] Invalid feature ID format: invalid-id
[INFO] Feature IDs should be in format: XX-###
```

### Test 5.4: List Features with Status Filter
**Description:** Filter features by status (empty result)
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', 'list', '--status', 'requested'])"
```
**Expected Output:**
```
[INFO] No features found (status: requested).
```

---

## GDD Creator Agent

### Test 6.1: GDD Command Help Display
**Description:** Verify GDD command help shows all available subcommands
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', '--help'])"
```
**Expected Output:**
```
usage: antigine gdd [-h] <operation> ...

positional arguments:
  <operation>  GDD operations
    create     Start interactive GDD creation
    resume     Resume existing GDD session
    status     Show GDD creation progress
    export     Export current GDD document

options:
  -h, --help   show this help message and exit
```

### Test 6.2: Start New GDD Session (Atomic Flash Lite)
**Description:** Start a new interactive GDD creation session with atomic Flash Lite architecture
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'create'])"
```
**Interactive Steps:**
1. System should show GDD creation instructions
2. Flash Lite should generate focused questions for Core Vision section
3. Respond with basic game concept information
4. System should evaluate response and either ask follow-up questions or complete section

**Expected Output:**
```
🎮 Starting GDD creation with atomic Flash Lite approach...
✨ New GDD session created: [timestamp]

📋 GDD Creation Instructions:
• Answer the coach's questions to build your Game Design Document
• Type 'help' to see available commands
• Type 'status' to check your progress
• Type 'next' to see what's coming up
• Type 'preview' to see your current GDD
• Type 'section <number>' to jump to a specific section
• Type 'quit' to exit and save progress

📝 Started section 1: Core Vision

📋 Questions to help you develop this section:
   1. What is the core concept and main gameplay mechanic of your game?
   2. Who is your target audience and what age group are you designing for?
   3. What 3-5 design pillars will guide your development decisions?

💬 Interactive GDD Creation Mode
Type 'help' for commands, 'quit' to exit, 'status' for progress

👤 You: 
```

### Test 6.3: Response Evaluation and Follow-up Questions
**Description:** Test how the system evaluates responses and generates follow-up questions
**Setup:** Use directory from Test 2.1, continuing from Test 6.2
**Interactive Steps:**
1. Provide a brief, incomplete response to the initial questions
2. System should evaluate the response as incomplete
3. Flash Lite should generate follow-up questions
4. Provide a complete response
5. System should evaluate as complete and move to next section

**Expected Behavior:**
```
👤 You: My game is a platformer
🤖 Coach: 📝 Your response covers the basic game type, but we need more details about your target audience and design pillars to complete this section.

📋 Questions to help you develop this section:
   1. What specific age group or demographic are you targeting with this platformer?
   2. What unique mechanics or features will set your platformer apart from others?
   3. What are the core design principles that will guide your development decisions?

👤 You: I'm targeting teenagers aged 13-17 who enjoy challenging games. My platformer will have unique gravity-switching mechanics where players can flip between ceiling and floor. My design pillars are: accessibility first, meaningful challenge, and tight controls.

🤖 Coach: ✅ Section 1 completed! You've provided a clear game concept, defined your target audience, and established solid design pillars.

🎯 Next: Section 2. MDA Breakdown
   Mechanics, Dynamics, and Aesthetics with ruthless focus

Continue to next section? (y/n): 
```

### Test 6.4: Resume Existing GDD Session
**Description:** Resume a previously started GDD creation session
**Setup:** First run Test 6.2, then exit without completing
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'resume'])"
```
**Expected Output:**
```
Resuming existing GDD session...
Session found: [timestamp]

Current progress: 1/8 sections complete
Currently working on: Section 2 - Mechanics & Systems

Welcome back! Let's continue with the Mechanics & Systems section...
```

### Test 6.5: GDD Session Status
**Description:** Check current GDD creation progress and status
**Setup:** Use directory with active GDD session
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'status'])"
```
**Expected Output:**
```
=== GDD Session Status ===

Session ID: [session-id]
Style: coach | Model: standard
Tech Stack: Love2D/Lua
Started: [timestamp]

Progress: 3/8 sections complete

Section Status:
✓ 1. Core Concept (Complete)
✓ 2. Mechanics & Systems (Complete) 
✓ 3. Art & Audio (Complete)
→ 4. Technical Architecture (In Progress)
  5. Level Design & Content (Pending)
  6. User Interface & Experience (Pending)
  7. Development & Production (Pending)
  8. Testing & Quality Assurance (Pending)

Content completeness: 60% (ready for initial export)
```

### Test 6.6: Export GDD Preview
**Description:** Export current GDD document as markdown preview
**Setup:** Use directory with partially complete GDD session
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'export', '--preview'])"
```
**Expected Output:**
```
Exporting GDD preview...

Preview saved to: docs/gdd_preview.md

Content includes:
- 3 completed sections
- 1 section in progress
- 4 sections pending (outlined)

Use --final to generate complete GDD when all sections are done.
```

### Test 6.7: Final GDD Export
**Description:** Export final complete GDD document
**Setup:** Use directory with completed GDD session
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'export', '--final'])"
```
**Expected Output:**
```
Generating final GDD document...

✅ All 8 sections complete
✅ Content validation passed
✅ GDD document generated

Final GDD saved to: docs/gdd.md
Backup created: docs/gdd_backup_[timestamp].md

Your Game Design Document is complete!
```

### Test 6.8: Interactive Commands Testing
**Description:** Test various interactive commands during GDD creation session
**Setup:** Use directory from Test 2.3
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'create'])"
```
**Interactive Steps:**
1. Test 'help' command
2. Test 'status' command  
3. Test 'next' command
4. Test 'preview' command
5. Test 'section 3' command to jump to a specific section

**Expected Behavior:**
```
👤 You: help
📖 Available Commands:
• help          - Show this help message
• status        - Show current progress and section status
• next          - Preview the next section
• preview       - Show current GDD document preview
• section <num> - Jump to a specific section (e.g., 'section 3')
• quit          - Exit and save progress

👤 You: status
📊 Progress Summary:
Current Section: Core Vision (1/8)
Completed: 0 sections (0.0%)

👤 You: section 3
📝 Started section 3: Core Gameplay Loop
[Questions for section 3 would appear here]
```

### Test 6.9: Tech Stack Integration Validation
**Description:** Verify tech stack-specific guidance is provided in Flash Lite questions
**Setup:** Use directory with different tech stacks from previous tests
**Commands:**
```bash
# Test Love2D guidance
cd AntigineManualTest1
python -c "from antigine.run import main; main(['gdd', 'create'])"

# Test SDL2 guidance  
cd AntigineManualTest2
python -c "from antigine.run import main; main(['gdd', 'create'])"

# Test Pygame guidance
cd AntigineManualTest3  
python -c "from antigine.run import main; main(['gdd', 'create'])"
```
**Expected Behavior:**
- Love2D questions should reference Love2D-specific considerations (sprites, physics, audio systems)
- SDL2 questions should mention C++ development patterns, OpenGL rendering capabilities, memory management
- Pygame questions should discuss Python game development, cross-platform deployment, pygame module usage

**Note:** The Flash Lite model should incorporate tech stack context into all question generation, ensuring questions are relevant to the specific technology being used.

### Test 6.10: Error Handling - No Project Context
**Description:** Verify error when running GDD commands outside Antigine project
**Setup:**
```bash
mkdir "D:\TestProjects\NonAntigineFolder"
cd "D:\TestProjects\NonAntigineFolder"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'create'])"
```
**Expected Output:**
```
Error: Not in an Antigine project directory. Run 'antigine init' first.
```

### Test 6.11: Session Persistence and Recovery
**Description:** Test session state persistence across CLI restarts
**Setup:** Use directory from Test 2.1
**Interactive Steps:**
1. Start GDD session and complete first section
2. Exit CLI (Ctrl+C or normal termination)
3. Restart and resume session
4. Verify all previous conversation history is available

**Commands:**
```bash
# Step 1: Start session
python -c "from antigine.run import main; main(['gdd', 'create'])"
# [Interact and then exit]

# Step 3: Resume
python -c "from antigine.run import main; main(['gdd', 'resume'])"
```
**Expected Behavior:**
- Session resumes exactly where it left off
- Previous conversation context is maintained
- Current section progress is preserved

### Test 6.12: Content Validation and Warnings
**Description:** Test content completeness validation and warnings
**Setup:** Use directory with minimal responses in GDD session
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'status', '--validate'])"
```
**Expected Output:**
```
=== GDD Session Status ===
[... status info ...]

⚠️  Content Validation Warnings:
- Section 1 (Core Concept): Low detail level detected
- Section 3 (Art & Audio): Missing key information about audio design
- Technical Architecture: No performance considerations mentioned

Recommendations:
- Expand core concept with more specific mechanics
- Add detailed audio design requirements
- Include performance targets and optimization strategy
```

---

## Feature Request Workflow

### Test 9.1: Basic Feature Request Creation
**Description:** Test the complete feature request workflow with LLM validation and semantic search
**Setup:** Use directory from Test 2.1 (Love2D project)
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', 'new'])"
```
**Interactive Steps:**
1. Enter feature title: "Player Movement System"
2. Enter feature description: "Implement WASD movement controls for the player character with smooth acceleration and deceleration. Player should move at 200 pixels per second and respond instantly to input changes."
3. Select feature type: 1 (new_feature)
4. Wait for LLM validation and semantic search
5. Review validation results
6. Choose to proceed with feature creation

**Expected Output:**
```
Enter feature title: Player Movement System
Enter feature description (press Enter twice to finish):
Implement WASD movement controls for the player character with smooth acceleration and deceleration. Player should move at 200 pixels per second and respond instantly to input changes.

Select feature type:
  1. new_feature - Add new functionality
  2. bug_fix - Fix existing bug
  3. refactor - Improve code structure
  4. enhancement - Improve existing feature
Enter choice (1-4): 1

Processing feature request...

Feature Request Validation Results:
  Confidence Score: 0.85

[OK] Feature request created successfully!
Feature ID: TG-001
Title: Player Movement System
Type: new_feature
Status: requested

Next steps:
  - View details: antigine feature show TG-001
  - List all features: antigine feature list
```

### Test 9.2: Feature Request with Validation Issues
**Description:** Test LLM validation when feature request is incomplete
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', 'new'])"
```
**Interactive Steps:**
1. Enter feature title: "Add sound"
2. Enter feature description: "Need sounds in the game"
3. Select feature type: 1 (new_feature)
4. System should detect validation issues and show suggestions

**Expected Output:**
```
Enter feature title: Add sound
Enter feature description (press Enter twice to finish):
Need sounds in the game

Select feature type:
  1. new_feature - Add new functionality
  2. bug_fix - Fix existing bug
  3. refactor - Improve code structure
  4. enhancement - Improve existing feature
Enter choice (1-4): 1

Processing feature request...

[ERROR] Feature creation failed: Validation failed - insufficient detail

Validation issues identified:
  - Description is too vague and lacks specific requirements
  - Missing information about what types of sounds are needed
  - No success criteria or implementation details provided

Suggestions for improvement:
  - Specify what types of sounds (background music, sound effects, UI sounds)
  - Define when and how sounds should be triggered
  - Include audio format and quality requirements
```

### Test 9.3: Duplicate Feature Detection
**Description:** Test semantic search detection of similar features
**Setup:** Use directory from Test 9.1 (should have Player Movement System feature)
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', 'new'])"
```
**Interactive Steps:**
1. Enter feature title: "Character Movement Controls"
2. Enter feature description: "Create movement system for the player using keyboard input. The character should move smoothly across the screen with WASD keys."
3. Select feature type: 1 (new_feature)
4. System should detect similarity with existing feature
5. Choose option 3 to show detailed comparison
6. Choose option 2 to cancel and revise

**Expected Output:**
```
Enter feature title: Character Movement Controls
Enter feature description (press Enter twice to finish):
Create movement system for the player using keyboard input. The character should move smoothly across the screen with WASD keys.

Select feature type:
  1. new_feature - Add new functionality
  2. bug_fix - Fix existing bug
  3. refactor - Improve code structure
  4. enhancement - Improve existing feature
Enter choice (1-4): 1

Processing feature request...

Feature Request Validation Results:
  Confidence Score: 0.82

Found 1 potentially related features:

1. Player Movement System (ID: TG-001)
   Relationship: duplicate
   Confidence: 0.92
   Description: Implement WASD movement controls for the player character with smooth acceleration...
   ⚠️  HIGH CONFIDENCE DUPLICATE

Options:
  1. Proceed with feature creation
  2. Cancel and revise feature
  3. Show detailed comparison
Enter choice (1-3): 3

==================================================
DETAILED FEATURE COMPARISONS
==================================================

YOUR FEATURE:
Title: Character Movement Controls
Type: new_feature
Description: Create movement system for the player using keyboard input. The character should move smoothly across the screen with WASD keys.

----------------------------------------
SIMILAR FEATURE #1:
ID: TG-001
Title: Player Movement System
Relationship: duplicate
Confidence: 0.92
Description: Implement WASD movement controls for the player character with smooth acceleration and deceleration. Player should move at 200 pixels per second and respond instantly to input changes.
==================================================
Press Enter to return to options...

Options:
  1. Proceed with feature creation
  2. Cancel and revise feature
  3. Show detailed comparison
Enter choice (1-3): 2
[INFO] Feature creation cancelled. Please revise and try again.
```

---

## Error Handling

### Test 7.1: Invalid Command
**Description:** Verify error handling for unknown commands
**Setup:** Any directory
**Command:**
```bash
python -c "from antigine.run import main; main(['invalid_command'])"
```
**Expected Output:**
```
Unknown command: invalid_command
usage: antigine [-h] [--version] <command> ...
[... help output continues ...]
```

### Test 7.2: Missing Required Arguments
**Description:** Verify error when required arguments are missing
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['feature', 'show'])"
```
**Expected Output:**
```
usage: antigine feature show [-h] feature_id
antigine feature show: error: the following arguments are required: feature_id
```

### Test 7.3: Permission Error Simulation
**Description:** Test behavior with permission issues (manual setup required)
**Setup:**
```bash
mkdir "D:\TestProjects\ReadOnlyTest"
# Manually set folder to read-only in Windows properties
cd "D:\TestProjects\ReadOnlyTest"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'PermissionTest'])"
```
**Expected Output:**
```
[ERROR] Permission error: [specific error message]
[INFO] Make sure you have write permissions to this directory.
```

---

## Cross-Platform Compatibility

### Test 8.1: Long Path Support (Windows)
**Description:** Test with long directory paths on Windows
**Setup:**
```bash
mkdir "D:\TestProjects\Very\Long\Directory\Path\That\Exceeds\Normal\Limits\For\Testing\Purposes\AntigineTest"
cd "D:\TestProjects\Very\Long\Directory\Path\That\Exceeds\Normal\Limits\For\Testing\Purposes\AntigineTest"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'LongPathTest'])"
```
**Expected Output:**
```
[INFO] Initializing Antigine project 'LongPathTest' in [long path]
[INFO] Tech Stack: love2d
[INFO] Creating project folders...
[INFO] Configuring project...
[INFO] Initializing project ledger...
[OK] Successfully initialized Antigine project 'LongPathTest'!
```

### Test 8.2: Unicode Characters in Project Names
**Description:** Test project names with unicode characters
**Setup:**
```bash
mkdir "D:\TestProjects\UnicodeTest"
cd "D:\TestProjects\UnicodeTest"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'Spēlē-游戏-Игра'])"
```
**Expected Output:**
```
[INFO] Initializing Antigine project 'Spēlē-游戏-Игра' in D:\TestProjects\UnicodeTest
[... normal initialization output ...]
[OK] Successfully initialized Antigine project 'Spēlē-游戏-Игра'!
```

### Test 8.3: Spaces in Directory Paths
**Description:** Test handling of directory paths with spaces
**Setup:**
```bash
mkdir "D:\Test Projects\Antigine Space Test"
cd "D:\Test Projects\Antigine Space Test"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'SpaceTest'])"
```
**Expected Output:**
```
[INFO] Initializing Antigine project 'SpaceTest' in D:\Test Projects\Antigine Space Test
[... normal initialization output ...]
[OK] Successfully initialized Antigine project 'SpaceTest'!
```

---

## Cleanup

After running manual tests, clean up test directories:

```bash
# Remove test directories (be careful with paths!)
rmdir /s "D:\TestProjects\AntigineManualTest1"
rmdir /s "D:\TestProjects\AntigineManualTest2"
rmdir /s "D:\TestProjects\AntigineManualTest3"
rmdir /s "D:\TestProjects\AntigineManualTest4"
rmdir /s "D:\TestProjects\AntigineManualTest5"
rmdir /s "D:\TestProjects\AntigineManualTest6"
rmdir /s "D:\TestProjects\EmptyFolder"
rmdir /s "D:\TestProjects\ReadOnlyTest"
rmdir /s "D:\TestProjects\Very"
rmdir /s "D:\TestProjects\UnicodeTest"
rmdir /s "D:\TestProjects\NonAntigineFolder"
rmdir /s "D:\Test Projects"
```

---

## Notes for Testers

1. **Environment Setup:** Ensure `PYTHONPATH` includes the Antigine project root
2. **Platform Differences:** Some tests may behave differently on different operating systems
3. **File System:** Some tests create files and directories - ensure you have write permissions
4. **Unicode Support:** Console encoding may affect unicode tests on some systems
5. **Cleanup:** Always clean up test directories after testing to avoid conflicts

## Test Execution Checklist

- [ ] All CLI Help and Version tests pass
- [ ] Project Initialization works for different tech stacks
- [ ] Status display shows correct information
- [ ] Configuration management works correctly
- [ ] Feature management handles empty states properly
- [ ] GDD Creator Agent functionality works end-to-end
- [ ] GDD session persistence and recovery works
- [ ] Tech stack integration provides relevant guidance
- [ ] Error handling provides helpful messages
- [ ] Cross-platform compatibility verified

## Reporting Issues

When reporting issues found during manual testing:

1. **Test Name:** Which specific test failed
2. **Environment:** Operating system, Python version, console used
3. **Actual Output:** Copy the exact output received
4. **Expected vs Actual:** Highlight differences from expected output
5. **Reproduction Steps:** Any additional steps needed to reproduce the issue