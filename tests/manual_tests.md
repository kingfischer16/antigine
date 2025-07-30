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
**Description:** Test the interactive prompts for language and tech stack selection
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

### Test 2.4: Required Tech Stack Validation
**Description:** Test that tech stack input is required and cannot be empty
**Setup:**
```bash
mkdir "D:\TestProjects\AntigineManualTest4"
cd "D:\TestProjects\AntigineManualTest4"
```
**Command:**
```bash
python -c "from antigine.run import main; main(['init', '--name', 'ValidationTest'])"
```
**Interactive Steps:**
1. When prompted for programming language, enter `1` (Lua)
2. When prompted for tech stack, press Enter (empty input)
3. Should show error and re-prompt
4. Enter `Love2D` when prompted again

**Expected Output:**
```
Please select a programming language for your project:
  1. Lua
  2. Python
  3. C++
  4. C

Select programming language
Enter choice [1-4]: 1

Available libraries for Lua:
  1. Love2D - 2D game framework for Lua with built-in physics, audio, and graphics

You can specify:
  - A single library (e.g., 'Love2D', 'Pygame', 'SDL2')
  - Multiple libraries separated by '+' (e.g., 'SDL2+OpenGL+GLM')

Enter tech stack for Lua: 
[ERROR] Tech stack is required. Please specify at least one library.
Error: Tech stack input is required
```

### Test 2.5: Project Already Exists Error
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

### Test 6.2: Start New GDD Session (Coach Style)
**Description:** Start a new interactive GDD creation session with coach style
**Setup:** Use directory from Test 2.1
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'create', '--style', 'coach', '--model', 'standard'])"
```
**Interactive Steps:**
1. Agent should introduce itself and explain the process
2. Agent should ask questions about the first section (Core Concept)
3. Respond with basic game concept information
4. Type "done" when ready to move to next section

**Expected Output:**
```
Starting new GDD creation session...
Style: coach | Model: standard | Tech Stack: Love2D/Lua

=== GDD Creator Agent ===
Welcome! I'm here to guide you through creating a comprehensive Game Design Document for your Love2D project.

We'll work through 8 key sections together:
1. Core Concept (Current)
2. Mechanics & Systems
3. Art & Audio
4. Technical Architecture
5. Level Design & Content
6. User Interface & Experience
7. Development & Production
8. Testing & Quality Assurance

Let's start with your core concept. What's the main idea behind your game?
```

### Test 6.3: Start New GDD Session (Assembler Style)
**Description:** Start a new interactive GDD creation session with assembler style
**Setup:** Use directory from Test 2.2
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'create', '--style', 'assembler', '--model', 'lite'])"
```
**Expected Output:**
```
Starting new GDD creation session...
Style: assembler | Model: lite | Tech Stack: SDL2+OpenGL+GLM+Assimp/C++

=== GDD Creator Agent ===
GDD creation initialized. We need to efficiently collect information for 8 sections.

Section 1/8: Core Concept
Required info: Game title, genre, core mechanics, target audience
Enter your game's basic concept:
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

### Test 6.8: Model Tier Selection
**Description:** Test different model complexity tiers
**Setup:** Use directory from Test 2.3
**Command:**
```bash
python -c "from antigine.run import main; main(['gdd', 'create', '--model', 'pro', '--style', 'coach'])"
```
**Expected Output:**
```
Starting new GDD creation session...
Style: coach | Model: pro | Tech Stack: Pygame/Python

=== GDD Creator Agent (Pro Model) ===
Welcome to the advanced GDD creation experience! I'll provide detailed guidance and sophisticated analysis throughout our journey.

I'll ask probing questions, suggest industry best practices, and help you create a professional-grade Game Design Document...
```

### Test 6.9: Tech Stack Integration Validation
**Description:** Verify tech stack-specific guidance is provided
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
- Love2D session should mention Love2D-specific concepts, functions, libraries
- SDL2 session should reference C++ patterns, OpenGL rendering, asset management
- Pygame session should discuss Python game development, pygame modules, cross-platform considerations

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