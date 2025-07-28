"""
cli.py
######

Main CLI entry point for Antigine. This file handles argument parsing and delegates
to appropriate command implementations. No business logic should be implemented here.
"""

import sys
import argparse
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the main argument parser for Antigine CLI.

    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="antigine",
        description="The Agentic Anti-Engine Game Development Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  antigine init                     Initialize a new project
  antigine status                   Show project status
  antigine feature list             List all features
  antigine feature show <id>        Show feature details
        """,
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands", metavar="<command>")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new Antigine project")
    init_parser.add_argument("--name", help="Project name (interactive prompt if not provided)")
    init_parser.add_argument(
        "--language",
        help="Programming language (e.g. 'Lua', 'Python', 'C++', 'C') - interactive prompt if not provided",
    )
    init_parser.add_argument(
        "--tech-stack",
        help="Game tech stack - single framework (e.g. 'Love2D') or multiple libraries separated by '+' (e.g. 'SDL2+OpenGL+GLM')",
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show project status and statistics")
    status_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed status information")

    # Feature commands
    feature_parser = subparsers.add_parser("feature", help="Feature management commands")
    feature_subparsers = feature_parser.add_subparsers(
        dest="feature_command", help="Feature operations", metavar="<operation>"
    )

    # Feature list
    list_parser = feature_subparsers.add_parser("list", help="List features")
    list_parser.add_argument(
        "--status", help="Filter by status (requested, planned, in_progress, implemented, validated, superseded)"
    )
    list_parser.add_argument("--type", help="Filter by type (new_feature, bug_fix, refactor, enhancement)")

    # Feature show
    show_parser = feature_subparsers.add_parser("show", help="Show detailed feature information")
    show_parser.add_argument("feature_id", help="Feature ID to show details for")

    # Config command
    config_parser = subparsers.add_parser("config", help="View and manage project configuration")
    config_parser.add_argument("--list", "-l", action="store_true", help="List all configuration values")
    config_parser.add_argument("--get", help="Get specific configuration value")
    config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set configuration key to value")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point function. This is called by the installed 'antigine' command.

    Args:
        argv: Optional argument list (defaults to sys.argv[1:])

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = create_parser()
    args = parser.parse_args(argv)

    # Handle case where no command is provided
    if not args.command:
        parser.print_help()
        return 1

    try:
        # Import and delegate to appropriate command handlers
        # Imports are done here to avoid circular imports and speed up CLI startup

        if args.command == "init":
            from .cli.commands.init import handle_init

            return handle_init(args)

        elif args.command == "status":
            from .cli.commands.status import handle_status

            return handle_status(args)

        elif args.command == "feature":
            from .cli.commands.feature import handle_feature

            return handle_feature(args)

        elif args.command == "config":
            from .cli.commands.config import handle_config

            return handle_config(args)

        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130

    except ImportError as e:
        print(f"ImportError: {e}. Please ensure all required dependencies are installed.", file=sys.stderr)
        return 1
    
    except PermissionError as e:
        print(f"PermissionError: {e}. Please check your file permissions.", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}. Please report this issue.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
