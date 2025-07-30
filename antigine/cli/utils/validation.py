"""
validation.py
#############

CLI input validation and interactive prompt utilities.
"""

import os
import re
import sys
from typing import List, Optional, Callable


def detect_project_directory(path: str) -> bool:
    """
    Check if a directory is already an Antigine project.

    Args:
        path: Directory path to check

    Returns:
        bool: True if directory contains .antigine folder
    """
    antigine_folder = os.path.join(path, ".antigine")
    return os.path.isdir(antigine_folder)


def get_project_root() -> Optional[str]:
    """
    Find the root directory of the current Antigine project by searching upward.

    Returns:
        Optional[str]: Path to project root if found, None otherwise
    """
    current_path = os.getcwd()
    
    # Check current directory and parent directories
    while current_path != os.path.dirname(current_path):  # Stop at filesystem root
        if detect_project_directory(current_path):
            return current_path
        current_path = os.path.dirname(current_path)
    
    # Check the root directory itself
    if detect_project_directory(current_path):
        return current_path
    
    return None


def validate_project_name(name: str) -> bool:
    """
    Validate project name format.

    Args:
        name: Project name to validate

    Returns:
        bool: True if name is valid
    """
    if not name or len(name.strip()) == 0:
        return False

    if len(name) > 50:
        return False

    # Allow alphanumeric, spaces, hyphens, underscores
    pattern = r"^[a-zA-Z0-9\s\-_]+$"
    return bool(re.match(pattern, name))


def validate_feature_id(feature_id: str) -> bool:
    """
    Validate feature ID format (e.g., "UP-001").

    Args:
        feature_id: Feature ID to validate

    Returns:
        bool: True if format is valid
    """
    pattern = r"^[A-Z]{1,4}-\d{3}$"
    return bool(re.match(pattern, feature_id))


def prompt_for_input(
    prompt_text: str,
    default: Optional[str] = None,
    required: bool = True,
    validator: Optional[Callable[[str], bool]] = None,
) -> str:
    """
    Prompt user for input with optional default and validation.

    Args:
        prompt_text: Text to display to user
        default: Default value if user enters nothing
        required: Whether input is required
        validator: Optional validation function

    Returns:
        str: User input (validated if validator provided)

    Raises:
        KeyboardInterrupt: If user cancels with Ctrl+C
    """
    default_text = f" [{default}]" if default else ""
    required_text = " (required)" if required and not default else ""

    while True:
        try:
            user_input = input(f"{prompt_text}{default_text}{required_text}: ").strip()

            # Use default if no input provided
            if not user_input and default:
                user_input = default

            # Check if input is required
            if required and not user_input:
                print("This field is required. Please enter a value.")
                continue

            # Validate input if validator provided
            if validator and user_input:
                if not validator(user_input):
                    print("Invalid input. Please try again.")
                    continue

            return user_input

        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            raise KeyboardInterrupt


def prompt_for_choice(prompt_text: str, choices: List[str], default: Optional[str] = None) -> str:
    """
    Prompt user to select from a list of choices.

    Args:
        prompt_text: Text to display to user
        choices: List of valid choices
        default: Default choice if user enters nothing

    Returns:
        str: Selected choice

    Raises:
        KeyboardInterrupt: If user cancels with Ctrl+C
    """
    if default and default not in choices:
        raise ValueError(f"Default '{default}' not in choices: {choices}")

    print(f"\n{prompt_text}")
    for i, choice in enumerate(choices, 1):
        default_marker = " (default)" if choice == default else ""
        print(f"  {i}. {choice}{default_marker}")

    while True:
        try:
            user_input = input(f"\nEnter choice [1-{len(choices)}]: ").strip()

            # Use default if no input provided
            if not user_input and default:
                return default

            # Try to parse as number
            try:
                choice_num = int(user_input)
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}.")
                    continue
            except ValueError:
                # Try to match input as choice name
                user_input_lower = user_input.lower()
                matches = [choice for choice in choices if choice.lower().startswith(user_input_lower)]

                if len(matches) == 1:
                    return matches[0]
                elif len(matches) > 1:
                    print(f"Ambiguous choice. Matches: {', '.join(matches)}")
                    continue
                else:
                    print(f"Invalid choice. Please select from: {', '.join(choices)}")
                    continue

        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            raise KeyboardInterrupt


def confirm_action(prompt_text: str, default: bool = False) -> bool:
    """
    Prompt user for yes/no confirmation.

    Args:
        prompt_text: Text to display to user
        default: Default value if user enters nothing

    Returns:
        bool: True if user confirms, False otherwise

    Raises:
        KeyboardInterrupt: If user cancels with Ctrl+C
    """
    default_text = "[Y/n]" if default else "[y/N]"

    while True:
        try:
            user_input = input(f"{prompt_text} {default_text}: ").strip().lower()

            if not user_input:
                return default

            if user_input in ("y", "yes", "true", "1"):
                return True
            elif user_input in ("n", "no", "false", "0"):
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
                continue

        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            raise KeyboardInterrupt
