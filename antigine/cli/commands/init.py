"""
init.py
#######

CLI command handler for project initialization. Delegates to ProjectSetupManager.
"""

import os
from argparse import Namespace

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
        return str(args.language)

    # Available languages based on tech stack database
    available_languages = ["Lua", "Python", "C++", "C"]

    print_info("Please select a programming language for your project:")
    for i, lang in enumerate(available_languages, 1):
        print_info(f"  {i}. {lang}")

    language = prompt_for_choice(
        "Select programming language", choices=available_languages, default=None  # type: ignore
    )

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
        return str(args.tech_stack)

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

    tech_stack = _get_validated_tech_stack(language, available_libraries)

    return tech_stack


def _get_validated_tech_stack(language: str, available_libraries: dict) -> str:
    """
    Get and validate tech stack input from user with enhanced feedback.

    Args:
        language: Selected programming language
        available_libraries: Dictionary of available libraries for the language

    Returns:
        str: Validated tech stack string
    """
    while True:
        tech_stack = prompt_for_input(
            f"Enter tech stack for {language}",
            required=True
        )

        # Parse and validate the tech stack
        validation_result = _validate_tech_stack_input(tech_stack, available_libraries)

        if validation_result["valid"]:
            # Show what was recognized
            recognized_libs = validation_result["recognized_libraries"]
            if len(recognized_libs) > 1:
                lib_list = ", ".join(recognized_libs[:-1]) + f", and {recognized_libs[-1]}"
                print_success(f"✓ Recognized libraries: {lib_list}")
            else:
                print_success(f"✓ Recognized library: {recognized_libs[0]}")

            # Show any warnings
            if validation_result["warnings"]:
                for warning in validation_result["warnings"]:
                    print_info(f"ℹ {warning}")

            return tech_stack
        else:
            # Show validation errors
            for error in validation_result["errors"]:
                print_error(f"✗ {error}")

            # Show suggestions if available
            if validation_result["suggestions"]:
                print_info("Did you mean:")
                for suggestion in validation_result["suggestions"]:
                    print_info(f"  - {suggestion}")

            print_info("Please try again.")


def _validate_tech_stack_input(tech_stack: str, available_libraries: dict) -> dict:
    """
    Validate tech stack input and provide detailed feedback.

    Args:
        tech_stack: User input tech stack string
        available_libraries: Available libraries for the language

    Returns:
        dict: Validation result with status, errors, warnings, suggestions
    """
    # Parse components
    components = [comp.strip() for comp in tech_stack.split('+') if comp.strip()]

    if not components:
        return {
            "valid": False,
            "errors": ["Tech stack cannot be empty"],
            "warnings": [],
            "suggestions": [],
            "recognized_libraries": []
        }

    recognized_libraries = []
    unrecognized_components = []
    suggestions = []
    warnings = []

    # Validate each component
    for component in components:
        # Try exact match (case insensitive)
        exact_match = None
        for lib_name in available_libraries.keys():
            if lib_name.lower() == component.lower():
                exact_match = lib_name
                break

        if exact_match:
            recognized_libraries.append(exact_match)
        else:
            unrecognized_components.append(component)
            # Try to find close matches for suggestions
            close_matches = _find_close_matches(component, list(available_libraries.keys()))
            suggestions.extend(close_matches)

    # Check for potential issues
    if len(recognized_libraries) > 5:
        warnings.append(f"You've selected {len(recognized_libraries)} libraries - this might be overly complex")

    # Determine if valid
    is_valid = len(unrecognized_components) == 0

    errors = []
    if unrecognized_components:
        if len(unrecognized_components) == 1:
            errors.append(f"Unrecognized library: '{unrecognized_components[0]}'")
        else:
            comp_list = "', '".join(unrecognized_components)
            errors.append(f"Unrecognized libraries: '{comp_list}'")

    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "suggestions": list(set(suggestions)),  # Remove duplicates
        "recognized_libraries": recognized_libraries
    }


def _find_close_matches(input_text: str, available_options: list, max_suggestions: int = 3) -> list:
    """
    Find close matches for typos or partial inputs.

    Args:
        input_text: User input text
        available_options: List of valid options
        max_suggestions: Maximum number of suggestions to return

    Returns:
        list: List of suggested corrections
    """
    input_lower = input_text.lower()
    suggestions = []

    # Look for partial matches (substring matching)
    for option in available_options:
        option_lower = option.lower()
        if input_lower in option_lower or option_lower in input_lower:
            suggestions.append(option)

    # If no partial matches, look for options that start with the same letter
    if not suggestions:
        for option in available_options:
            if option.lower().startswith(input_lower[0]):
                suggestions.append(option)

    return suggestions[:max_suggestions]
