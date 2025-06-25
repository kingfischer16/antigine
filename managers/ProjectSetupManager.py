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

        # Creates the .afie folder in the game project folder.
        # This folder is used to store project-specific data.
        afie_folder = os.path.join(self.game_project_folder, ".afie")
        os.makedirs(afie_folder, exist_ok=True)

        # Copy the 'template_project.json' file from the afie templates folder in this module to
        # the .afie folder in the game_project_folder, and rename it to 'project.json'.
        template_project_path = os.path.join(os.path.dirname(__file__), "templates", "template_project.json")
        if not os.path.isfile(template_project_path):
            raise FileNotFoundError(f"Template project file does not exist: {template_project_path}")
        project_file_path = os.path.join(afie_folder, "project.json")
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
        afie_folder = os.path.join(self.game_project_folder, ".afie")
        project_file_path = os.path.join(afie_folder, "project.json")

        if not os.path.isfile(project_file_path):
            raise FileNotFoundError(f"Project file does not exist: {project_file_path}")

        with open(project_file_path, "r", encoding="utf-8") as f:
            project_data = json.load(f)

        project_data[field] = data

        with open(project_file_path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4)
        
    def create_empty_ledger(self) -> None:
        """
        Creates an empty ledger folder and file for the project.
        """
        afie_folder = os.path.join(self.game_project_folder, ".afie")
        if not os.path.isdir(afie_folder):
            raise FileNotFoundError(f"Expected directory does not exist: {afie_folder}")

        ledger_folder = os.path.join(afie_folder, "ledger")
        os.makedirs(ledger_folder, exist_ok=True)

        ledger_file_path = os.path.join(ledger_folder, "ledger.json")
        with open(ledger_file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)
