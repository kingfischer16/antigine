"""
ProjectSetupManager.py
######################

This module provides functions and classes dedicated to setting up a new project, including creating the necessary directory structure and initializing the ledger.
"""

# Imports
import os
import json

class ProjectSetupManager:
    """
    ProjectSetupManager is responsible for setting up a new game project by creating the necessary folder structure
    and initializing the project files.
    """

    def __init__(self, game_project_folder: str):
        """
        Initializes the ProjectSetupManager with the path to the game project folder.

        game_project_folder (str): The path to the game project folder.
        """
        self.game_project_folder = game_project_folder

    def create_project_folders(self) -> None:
        """
        Creates the necessary folder structure for a new game project.
        """
        if not os.path.isdir(self.game_project_folder):
            raise FileNotFoundError(f"Expected directory does not exist: {self.game_project_folder}")

        # Creates the .antigine folder in the game project folder.
        # This folder is used to store project-specific data.
        antigine_folder = os.path.join(self.game_project_folder, ".antigine")
        os.makedirs(antigine_folder, exist_ok=True)
        # Create the rest of the folders
        folders_to_create = [
            "assets",
            "assets/images",
            "assets/sounds",
            "assets/meshes",
            "assets/textures",
            "levels",
            "scripts",
            "data",
            "logs",
            "source"
        ]
        for folder in folders_to_create:
            folder_path = os.path.join(self.game_project_folder, folder)
            os.makedirs(folder_path, exist_ok=True)

        # Copy the 'template_project.json' file from the antigine templates folder in this module to
        # the .antigine folder in the game_project_folder, and rename it to 'project.json'.
        # Navigate up from managers/ to the project root to find templates/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        template_project_path = os.path.join(project_root, "templates", "template_project.json")
        if not os.path.isfile(template_project_path):
            raise FileNotFoundError(f"Template project file does not exist: {template_project_path}")
        project_file_path = os.path.join(antigine_folder, "project.json")
        with open(template_project_path, "r", encoding="utf-8") as template_file:
            project_data = json.load(template_file)
        with open(project_file_path, "w", encoding="utf-8") as project_file:
            json.dump(project_data, project_file, indent=4)

    def edit_project_file(self, field: str, data: str) -> None:
        """
        Edits a field in the project.json file.

        field (str): The field to edit in the project.json file.
        data (str): The data to set for the field.
        """
        antigine_folder = os.path.join(self.game_project_folder, ".antigine")
        project_file_path = os.path.join(antigine_folder, "project.json")

        if not os.path.isfile(project_file_path):
            raise FileNotFoundError(f"Project file does not exist: {project_file_path}")

        with open(project_file_path, "r", encoding="utf-8") as f:
            project_data = json.load(f)

        project_data[field] = data

        with open(project_file_path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4)
        
    def create_empty_ledger(self) -> None:
        """
        Creates an empty SQLite ledger database for the project.
        """
        from ..core.database import initialize_database
        
        antigine_folder = os.path.join(self.game_project_folder, ".antigine")
        if not os.path.isdir(antigine_folder):
            raise FileNotFoundError(f"Expected directory does not exist: {antigine_folder}")

        # Create SQLite database with proper schema
        ledger_db_path = os.path.join(antigine_folder, "ledger.db")
        initialize_database(ledger_db_path)
