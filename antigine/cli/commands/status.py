"""
status.py
#########

CLI command handler for project status display. Delegates to ProjectLedgerManager.
"""

import os
import json
from argparse import Namespace

from ...managers.ProjectLedgerManager import ProjectLedgerManager
from ..utils.output import print_error, print_info, print_project_status
from ..utils.validation import detect_project_directory


def handle_status(args: Namespace) -> int:
    """
    Handles the 'antigine status' command by delegating to ProjectLedgerManager.

    Args:
        args: Parsed command-line arguments

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    try:
        # Check if we're in an Antigine project
        project_dir = os.getcwd()
        if not detect_project_directory(project_dir):
            print_error("This directory is not an Antigine project.")
            print_info("Run 'antigine init' to initialize a new project.")
            return 1

        # Load project configuration
        config_path = os.path.join(project_dir, ".antigine", "project.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                project_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print_error(f"Failed to load project configuration: {e}")
            return 1

        project_name = project_config.get("project_name", "Unknown Project")
        tech_stack = project_config.get("tech_stack", "Unknown")

        # Get project statistics
        try:
            ledger_manager = ProjectLedgerManager(project_dir)
            stats = ledger_manager.get_feature_statistics()
        except Exception as e:
            print_error(f"Failed to load project ledger: {e}")
            return 1

        # Display project status
        print_project_status(stats, project_name)

        # Show tech stack information
        print(f"\nTech Stack: {tech_stack}")
        print(f"Project Directory: {project_dir}")

        # Show verbose information if requested
        if args.verbose:
            print("\nConfiguration:")
            for key, value in project_config.items():
                print(f"  {key}: {value}")

            # Show recent features if any exist
            if stats.get("total_features", 0) > 0:
                print("\nRecent Features:")
                try:
                    # Get recent features (limit to 5)
                    recent_features = []
                    for status in ["requested", "planned", "in_progress", "implemented"]:
                        features = ledger_manager.get_features_by_status(status)
                        recent_features.extend(features[:5])
                        if len(recent_features) >= 5:
                            break

                    for feature in recent_features[:5]:
                        print(f"  {feature['feature_id']}: {feature['title']} ({feature['status']})")

                except Exception as e:
                    print_info(f"Could not load recent features: {e}")

        return 0

    except KeyboardInterrupt:
        print_error("Operation cancelled by user.")
        return 130

    except Exception as e:
        print_error(f"Failed to get project status: {e}")
        return 1
