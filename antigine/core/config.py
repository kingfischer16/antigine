"""
config.py
#########

This module provides utility functions for accessing project configuration.
It reads configuration from the project.json file in the .antigine folder.

This module cannot import from other modules in this package to avoid circular dependencies.
"""

# Imports
import os
import json
from typing import Dict, Any, cast


def get_project_config(project_folder: str) -> Dict[str, Any]:
    """
    Loads and returns the project configuration from the project.json file.

    Args:
        project_folder (str): The path to the game project folder.

    Returns:
        Dict[str, Any]: The project configuration data.

    Raises:
        FileNotFoundError: If the project.json file doesn't exist.
        json.JSONDecodeError: If the project.json file is malformed.
    """
    project_file_path = os.path.join(project_folder, ".antigine", "project.json")

    if not os.path.isfile(project_file_path):
        raise FileNotFoundError(f"Project configuration file does not exist: {project_file_path}")

    with open(project_file_path, "r", encoding="utf-8") as f:
        return cast(Dict[str, Any], json.load(f))


def get_framework_info(project_folder: str) -> tuple[str, str]:
    """
    Gets the framework and language information from project configuration.

    Args:
        project_folder (str): The path to the game project folder.

    Returns:
        tuple[str, str]: A tuple of (engine_name, project_language).
    """
    config = get_project_config(project_folder)
    engine_name = config.get("engine_name", "Unknown Engine")
    project_language = config.get("project_language", "Unknown Language")
    return engine_name, project_language
