"""
init.py
#######

CLI command handler for project initialization. Delegates to ProjectSetupManager.
"""

import os
from argparse import Namespace
from typing import cast

from ...managers.ProjectSetupManager import ProjectSetupManager
from ..utils.output import print_success, print_error, print_info
from ..utils.validation import prompt_for_input, prompt_for_choice, detect_project_directory
from ...core.tech_stacks import resolve_tech_stack_name, tech_stack_manager


def handle_init(args: Namespace) -> int:
    """
    Handles the 'antigine init' command by delegating to ProjectSetupManager.

    Args:
        args: Parsed command-line arguments

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    try:
        # Determine project directory (current working directory)
        project_dir = os.getcwd()

        # Check if already an Antigine project
        if detect_project_directory(project_dir):
            print_error("This directory is already an Antigine project.")
            print_info("Use 'antigine status' to view project information.")
            return 1

        # Get project name
        project_name = args.name
        if not project_name:
            project_name = prompt_for_input("Enter project name", default=os.path.basename(project_dir))

        # Get programming language - required for project setup
        language = _get_programming_language(args)

        # Get tech stack - required for project setup
        tech_stack = _get_tech_stack(args, language)

        # Resolve any aliases or case issues in the tech stack name
        tech_stack = resolve_tech_stack_name(tech_stack)

        print_info(f"Initializing Antigine project '{project_name}' in {project_dir}")
        print_info(f"Tech Stack: {tech_stack}")

        # Create project setup manager and initialize
        setup_manager = ProjectSetupManager(project_dir)

        # Create project structure
        print_info("Creating project folders...")
        setup_manager.create_project_folders()

        # Update project configuration
        print_info("Configuring project...")
        setup_manager.edit_project_file("project_name", project_name)
        setup_manager.edit_project_file("tech_stack", tech_stack)

        # Initialize ledger database
        print_info("Initializing project ledger...")
        setup_manager.create_empty_ledger()

        print_success(f"Successfully initialized Antigine project '{project_name}'!")
        print_info("Next steps:")
        print_info("  1. Run 'antigine status' to view project information")
        print_info("  2. Create your first feature with 'antigine feature create'")

        return 0

    except FileNotFoundError as e:
        print_error(f"Directory error: {e}")
        return 1

    except PermissionError as e:
        print_error(f"Permission error: {e}")
        print_info("Make sure you have write permissions to this directory.")
        return 1

    except Exception as e:
        print_error(f"Failed to initialize project: {e}")
        return 1


def _get_programming_language(args: Namespace) -> str:
    """
    Get programming language from args or prompt user for selection.

    Args:
        args: Parsed command-line arguments

    Returns:
        str: Selected programming language
    """
    # Check if language was provided via command line
    if hasattr(args, "language") and args.language:
        return args.language

    # Available languages based on tech stack database
    available_languages = ["Lua", "Python", "C++", "C"]

    print_info("Please select a programming language for your project:")
    for i, lang in enumerate(available_languages, 1):
        print_info(f"  {i}. {lang}")

    language = prompt_for_choice("Select programming language", choices=available_languages, default=None)  # type: ignore

    return language


def _get_tech_stack(args: Namespace, language: str) -> str:
    """
    Get tech stack from args or prompt user for selection.

    Args:
        args: Parsed command-line arguments
        language: Selected programming language

    Returns:
        str: Selected tech stack
    """
    # Check if tech_stack was provided via command line
    if hasattr(args, "tech_stack") and args.tech_stack:
        return args.tech_stack

    # Get available libraries for the selected language
    available_libraries = tech_stack_manager.get_available_libraries(language)

    print_info(f"Available libraries for {language}:")
    lib_names = list(available_libraries.keys())
    for i, lib_name in enumerate(lib_names, 1):
        lib_info = available_libraries[lib_name]
        print_info(f"  {i}. {lib_name} - {lib_info.description}")

    print_info("")
    print_info("You can specify:")
    print_info("  - A single library (e.g., 'Love2D', 'Pygame', 'SDL2')")
    print_info("  - Multiple libraries separated by '+' (e.g., 'SDL2+OpenGL+GLM')")

    tech_stack = prompt_for_input(f"Enter tech stack for {language}", default=None)  # type: ignore

    if not tech_stack:
        print_error("Tech stack is required. Please specify at least one library.")
        raise ValueError("Tech stack input is required")

    return tech_stack
