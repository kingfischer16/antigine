"""
config.py
#########

CLI command handler for configuration management. Delegates to core configuration functions.
"""

import os
import json
from argparse import Namespace

from ..utils.output import print_success, print_error, print_info, print_header
from ..utils.validation import detect_project_directory


def handle_config(args: Namespace) -> int:
    """
    Handles the 'antigine config' command by working with project configuration.
    
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
        
        config_path = os.path.join(project_dir, ".antigine", "project.json")
        
        # Load current configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print_error(f"Failed to load project configuration: {e}")
            return 1
        
        # Handle subcommands
        if args.list:
            return handle_config_list(config)
        elif args.get:
            return handle_config_get(config, args.get)
        elif args.set:
            return handle_config_set(config_path, config, args.set[0], args.set[1])
        else:
            # Default to list if no specific action
            return handle_config_list(config)
            
    except KeyboardInterrupt:
        print_error("Operation cancelled by user.")
        return 130
        
    except Exception as e:
        print_error(f"Configuration command failed: {e}")
        return 1


def handle_config_list(config: dict) -> int:
    """
    Display all configuration values.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        int: Exit code (0 for success)
    """
    print_header("Project Configuration")
    
    for key, value in config.items():
        # Format complex values nicely
        if isinstance(value, (list, dict)):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)
        
        print(f"{key}: {value_str}")
    
    return 0


def handle_config_get(config: dict, key: str) -> int:
    """
    Get a specific configuration value.
    
    Args:
        config: Configuration dictionary
        key: Configuration key to retrieve
        
    Returns:
        int: Exit code (0 for success, 1 if key not found)
    """
    if key in config:
        value = config[key]
        if isinstance(value, (list, dict)):
            print(json.dumps(value, indent=2))
        else:
            print(value)
        return 0
    else:
        print_error(f"Configuration key not found: {key}")
        print_info(f"Available keys: {', '.join(config.keys())}")
        return 1


def handle_config_set(config_path: str, config: dict, key: str, value: str) -> int:
    """
    Set a configuration value.
    
    Args:
        config_path: Path to configuration file
        config: Current configuration dictionary
        key: Configuration key to set
        value: New value to set
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Parse value as JSON if possible, otherwise keep as string
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        
        # Update configuration
        old_value = config.get(key)
        config[key] = parsed_value
        
        # Save updated configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        # Confirm the change
        if old_value is not None:
            print_success(f"Updated {key}: {old_value} → {parsed_value}")
        else:
            print_success(f"Set {key}: {parsed_value}")
        
        return 0
        
    except Exception as e:
        print_error(f"Failed to set configuration: {e}")
        return 1