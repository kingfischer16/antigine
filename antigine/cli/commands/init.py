"""
init.py
#######

CLI command handler for project initialization. Delegates to ProjectSetupManager.
"""

import os
import sys
from argparse import Namespace
from typing import Optional

from ...managers.ProjectSetupManager import ProjectSetupManager
from ..utils.output import print_success, print_error, print_info
from ..utils.validation import prompt_for_input, detect_project_directory


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
            project_name = prompt_for_input(
                "Enter project name", 
                default=os.path.basename(project_dir)
            )
        
        # TODO: Tech stack selection will be implemented in Phase 2
        # For now, we'll use a placeholder
        tech_stack = args.tech_stack or "love2d"
        
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