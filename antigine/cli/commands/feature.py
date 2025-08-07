"""
feature.py
##########

CLI command handler for feature management. Delegates to ProjectLedgerManager.
"""

import os
from argparse import Namespace

from ...managers.ProjectLedgerManager import ProjectLedgerManager
from ..utils.output import print_error, print_info, print_table, print_feature_summary, print_success, print_warning
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
        if args.feature_command == "new":
            return handle_feature_new(ledger_manager, args, project_dir)
        elif args.feature_command == "list":
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
            all_statuses = stats.get("by_status", {}).keys()
            features = []
            for status in all_statuses:
                status_features = ledger_manager.get_features_by_status(status)
                features.extend([f for f in status_features if f.get("type") == args.type])
            filter_text = f" (type: {args.type})"
        else:
            # Get all features by getting features from all statuses
            stats = ledger_manager.get_feature_statistics()
            all_statuses = stats.get("by_status", {}).keys()
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
            title = feature.get("title", "")
            if len(title) > 30:
                title = title[:27] + "..."

            rows.append(
                [
                    feature.get("feature_id", "N/A"),
                    title,
                    feature.get("type", "N/A"),
                    feature.get("status", "N/A"),
                    feature.get("date_created", "N/A")[:10],  # Show only date part
                ]
            )

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


def handle_feature_new(ledger_manager: ProjectLedgerManager, args: Namespace, project_dir: str) -> int:
    """
    Handle 'antigine feature new' command using LangGraph workflow.

    Args:
        ledger_manager: ProjectLedgerManager instance
        args: Parsed command-line arguments
        project_dir: Project directory path

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    try:
        # Import here to avoid circular imports
        from ...core.agents.feature_request_agent import FeatureRequestAgent
        
        # Get feature details from args or prompt user
        title = args.title
        description = args.description
        feature_type = args.type

        # Interactive prompting if values not provided
        if not title:
            title = input("Enter feature title: ").strip()
            if not title:
                print_error("Feature title is required.")
                return 1

        if not description:
            print_info("Enter feature description (press Enter twice to finish):")
            description_lines = []
            empty_line_count = 0
            while True:
                line = input()
                if line.strip() == "":
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        break
                    description_lines.append("")
                else:
                    empty_line_count = 0
                    description_lines.append(line)
            
            description = "\n".join(description_lines).strip()
            if not description:
                print_error("Feature description is required.")
                return 1

        if not feature_type:
            print_info("Select feature type:")
            print_info("  1. new_feature - Add new functionality")
            print_info("  2. bug_fix - Fix existing bug")
            print_info("  3. refactor - Improve code structure")
            print_info("  4. enhancement - Improve existing feature")
            
            type_map = {
                "1": "new_feature",
                "2": "bug_fix", 
                "3": "refactor",
                "4": "enhancement"
            }
            
            while True:
                choice = input("Enter choice (1-4): ").strip()
                if choice in type_map:
                    feature_type = type_map[choice]
                    break
                else:
                    print_error("Invalid choice. Please enter 1-4.")

        # Initialize the feature request agent
        db_path = os.path.join(project_dir, ".antigine", "ledger.db")
        agent = FeatureRequestAgent(project_dir, db_path)
        
        # Execute the LangGraph workflow
        print_info("Processing feature request...")
        
        try:
            final_state = agent.process_feature_request(title, description, feature_type)
        except Exception as e:
            print_error(f"Failed to process feature request: {e}")
            return 1
        
        # Handle workflow results based on final state
        return _handle_workflow_results(final_state)

    except KeyboardInterrupt:
        print_error("Feature creation cancelled by user.")
        return 130
    
    except Exception as e:
        print_error(f"Failed to create feature: {e}")
        return 1


def _handle_workflow_results(state: dict) -> int:
    """
    Handle the results from the LangGraph workflow with human-in-the-loop interactions.
    
    Args:
        state: Final state from the workflow
        
    Returns:
        int: Exit code
    """
    try:
        # Check if we need user confirmation for relationships
        if state["current_stage"] == "user_confirmation":
            return _handle_user_confirmation_stage(state)
        
        # Check final results
        if state.get("stored_successfully", False):
            print_success("Feature request created successfully!")
            print_info(f"Feature ID: {state['feature_id']}")
            print_info(f"Title: {state['title']}")
            print_info(f"Type: {state['feature_type']}")
            print_info("Status: requested")
            
            # Show any confirmed relationships
            if state.get("relationship_confirmations"):
                print_info("\nConfirmed relationships:")
                for related_id, rel_type in state["relationship_confirmations"].items():
                    print_info(f"  - {rel_type}: {related_id}")
            
            print_info("\nNext steps:")
            print_info(f"  - View details: antigine feature show {state['feature_id']}")
            print_info(f"  - List all features: antigine feature list")
            
            return 0
        
        elif state.get("error_message"):
            print_error(f"Feature creation failed: {state['error_message']}")
            
            # Show validation issues if available
            if state.get("validation_issues"):
                print_info("Validation issues identified:")
                for issue in state["validation_issues"]:
                    print_info(f"  - {issue}")
                    
            if state.get("validation_suggestions"):
                print_info("Suggestions for improvement:")
                for suggestion in state["validation_suggestions"]:
                    print_info(f"  - {suggestion}")
            
            return 1
        
        else:
            print_warning("Feature creation completed with unknown status.")
            return 1
            
    except Exception as e:
        print_error(f"Error handling workflow results: {e}")
        return 1


def _handle_user_confirmation_stage(state: dict) -> int:
    """
    Handle the user confirmation stage of the workflow.
    
    Args:
        state: Current workflow state
        
    Returns:
        int: Exit code
    """
    try:
        # Show validation results
        print_info("Feature Request Validation Results:")
        print_info(f"  Confidence Score: {state['confidence_score']:.2f}")
        
        if state["validation_issues"]:
            print_warning("Validation Issues:")
            for issue in state["validation_issues"]:
                print_info(f"  - {issue}")
        
        if state["validation_suggestions"]:
            print_info("Suggestions:")
            for suggestion in state["validation_suggestions"]:
                print_info(f"  - {suggestion}")
        
        # Show similar features found
        if state["potential_relationships"]:
            print_warning(f"\nFound {len(state['potential_relationships'])} potentially related features:")
            
            for i, relationship in enumerate(state["potential_relationships"], 1):
                print_info(f"\n{i}. {relationship['title']} (ID: {relationship['feature_id']})")
                print_info(f"   Relationship: {relationship['relationship_type']}")
                print_info(f"   Confidence: {relationship['confidence_score']:.2f}")
                print_info(f"   Description: {relationship['description'][:100]}...")
                
                # Check for high-confidence duplicates or conflicts
                if (relationship['relationship_type'] in ['duplicate', 'conflicts_with'] 
                    and relationship['confidence_score'] >= 0.8):
                    print_warning(f"   ⚠️  HIGH CONFIDENCE {relationship['relationship_type'].upper()}")
        
        # Get user decision
        print_info("\nOptions:")
        print_info("  1. Proceed with feature creation")
        print_info("  2. Cancel and revise feature")
        print_info("  3. Show detailed comparison")
        
        while True:
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                # User approves - update state and continue workflow
                state["user_approved"] = True
                
                # Ask about relationship confirmations for high-confidence matches
                confirmed_relationships = {}
                for rel in state["potential_relationships"]:
                    if (rel['relationship_type'] in ['duplicate', 'supersedes', 'conflicts_with'] 
                        and rel['confidence_score'] >= 0.7):
                        
                        while True:
                            confirm = input(
                                f"Confirm relationship '{rel['relationship_type']}' with {rel['feature_id']}? (y/n): "
                            ).strip().lower()
                            
                            if confirm in ['y', 'yes']:
                                confirmed_relationships[rel['feature_id']] = rel['relationship_type']
                                break
                            elif confirm in ['n', 'no']:
                                break
                            else:
                                print_error("Please enter 'y' or 'n'")
                
                state["relationship_confirmations"] = confirmed_relationships
                
                # Re-run the workflow from storage node
                from ...core.agents.feature_request_agent import FeatureRequestAgent
                agent = FeatureRequestAgent(state["project_root"], state["db_path"])
                storage_result = agent._store_feature_node(state)
                
                return _handle_workflow_results(storage_result)
            
            elif choice == "2":
                print_info("Feature creation cancelled. Please revise and try again.")
                return 0
            
            elif choice == "3":
                # Show detailed comparisons
                _show_detailed_comparisons(state)
                continue
            
            else:
                print_error("Invalid choice. Please enter 1-3.")
    
    except Exception as e:
        print_error(f"Error in user confirmation: {e}")
        return 1


def _show_detailed_comparisons(state: dict) -> None:
    """Show detailed comparisons between new and existing features."""
    print_info("\n" + "="*50)
    print_info("DETAILED FEATURE COMPARISONS")
    print_info("="*50)
    
    print_info(f"\nYOUR FEATURE:")
    print_info(f"Title: {state['title']}")
    print_info(f"Type: {state['feature_type']}")
    print_info(f"Description: {state['description']}")
    
    for i, rel in enumerate(state["potential_relationships"], 1):
        print_info(f"\n{'-'*40}")
        print_info(f"SIMILAR FEATURE #{i}:")
        print_info(f"ID: {rel['feature_id']}")
        print_info(f"Title: {rel['title']}")
        print_info(f"Relationship: {rel['relationship_type']}")
        print_info(f"Confidence: {rel['confidence_score']:.2f}")
        print_info(f"Description: {rel['description']}")
    
    print_info("="*50)
    input("Press Enter to return to options...")
