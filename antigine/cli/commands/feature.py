"""
feature.py
##########

CLI command handler for feature management. Delegates to ProjectLedgerManager.
"""

import os
from argparse import Namespace

from ...managers.ProjectLedgerManager import ProjectLedgerManager
from ..utils.output import (
    print_success, print_error, print_info, print_table, 
    print_feature_summary
)
from ..utils.validation import detect_project_directory, validate_feature_id


def handle_feature(args: Namespace) -> int:
    """
    Handles the 'antigine feature' command by delegating to ProjectLedgerManager.
    
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
        
        # Initialize ledger manager
        try:
            ledger_manager = ProjectLedgerManager(project_dir)
        except Exception as e:
            print_error(f"Failed to initialize project ledger: {e}")
            return 1
        
        # Handle subcommands
        if args.feature_command == "list":
            return handle_feature_list(ledger_manager, args)
        elif args.feature_command == "show":
            return handle_feature_show(ledger_manager, args)
        else:
            print_error(f"Unknown feature command: {args.feature_command}")
            return 1
            
    except KeyboardInterrupt:
        print_error("Operation cancelled by user.")
        return 130
        
    except Exception as e:
        print_error(f"Feature command failed: {e}")
        return 1


def handle_feature_list(ledger_manager: ProjectLedgerManager, args: Namespace) -> int:
    """
    Handle 'antigine feature list' command.
    
    Args:
        ledger_manager: ProjectLedgerManager instance
        args: Parsed command-line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    try:
        # Get features based on filters
        if args.status:
            features = ledger_manager.get_features_by_status(args.status)
            filter_text = f" (status: {args.status})"
        elif args.type:
            # For type filtering, we need to get all features and filter
            # This is a limitation of the current ProjectLedgerManager API
            stats = ledger_manager.get_feature_statistics()
            all_statuses = stats.get('by_status', {}).keys()
            features = []
            for status in all_statuses:
                status_features = ledger_manager.get_features_by_status(status)
                features.extend([f for f in status_features if f.get('type') == args.type])
            filter_text = f" (type: {args.type})"
        else:
            # Get all features by getting features from all statuses
            stats = ledger_manager.get_feature_statistics()
            all_statuses = stats.get('by_status', {}).keys()
            features = []
            for status in all_statuses:
                features.extend(ledger_manager.get_features_by_status(status))
            filter_text = ""
        
        if not features:
            print_info(f"No features found{filter_text}.")
            return 0
        
        # Prepare table data
        headers = ["ID", "Title", "Type", "Status", "Created"]
        rows = []
        
        for feature in features:
            # Truncate long titles for table display
            title = feature.get('title', '')
            if len(title) > 30:
                title = title[:27] + "..."
            
            rows.append([
                feature.get('feature_id', 'N/A'),
                title,
                feature.get('type', 'N/A'),
                feature.get('status', 'N/A'),
                feature.get('date_created', 'N/A')[:10]  # Show only date part
            ])
        
        # Display results
        print_info(f"Found {len(features)} feature(s){filter_text}")
        print_table(headers, rows)
        
        return 0
        
    except Exception as e:
        print_error(f"Failed to list features: {e}")
        return 1


def handle_feature_show(ledger_manager: ProjectLedgerManager, args: Namespace) -> int:
    """
    Handle 'antigine feature show <id>' command.
    
    Args:
        ledger_manager: ProjectLedgerManager instance
        args: Parsed command-line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    try:
        feature_id = args.feature_id
        
        # Validate feature ID format
        if not validate_feature_id(feature_id):
            print_error(f"Invalid feature ID format: {feature_id}")
            print_info("Feature IDs should be in format: XX-###")
            return 1
        
        # Get feature details
        feature = ledger_manager.get_feature_by_id(feature_id)
        
        if not feature:
            print_error(f"Feature not found: {feature_id}")
            return 1
        
        # Display feature details
        print_feature_summary(feature)
        
        return 0
        
    except Exception as e:
        print_error(f"Failed to show feature: {e}")
        return 1