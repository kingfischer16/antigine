"""
output.py
#########

CLI output formatting utilities. Provides consistent styling and messaging for CLI commands.
"""

import sys
from typing import Any, Dict, List, Optional


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(f"[OK] {message}")


def print_error(message: str) -> None:
    """Print an error message in red to stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(f"[WARN] {message}")


def print_info(message: str) -> None:
    """Print an informational message."""
    print(f"[INFO] {message}")


def print_header(message: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * len(message)}")
    print(message)
    print('=' * len(message))


def print_table(headers: List[str], rows: List[List[str]], max_width: int = 80) -> None:
    """
    Print a formatted table.
    
    Args:
        headers: Column headers
        rows: Table data rows
        max_width: Maximum table width
    """
    if not rows:
        print("No data to display")
        return
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Ensure table fits within max_width
    total_width = sum(col_widths) + len(headers) * 3 + 1
    if total_width > max_width:
        # Proportionally reduce column widths
        reduction_factor = (max_width - len(headers) * 3 - 1) / sum(col_widths)
        col_widths = [max(8, int(width * reduction_factor)) for width in col_widths]
    
    # Print header
    header_row = "| " + " | ".join(
        header.ljust(col_widths[i]) for i, header in enumerate(headers)
    ) + " |"
    print(header_row)
    print("|" + "|".join("-" * (width + 2) for width in col_widths) + "|")
    
    # Print rows
    for row in rows:
        row_str = "| " + " | ".join(
            str(cell).ljust(col_widths[i])[:col_widths[i]] for i, cell in enumerate(row)
        ) + " |"
        print(row_str)


def print_feature_summary(feature: Dict[str, Any]) -> None:
    """
    Print a formatted summary of a feature.
    
    Args:
        feature: Feature data dictionary
    """
    print_header(f"Feature {feature['feature_id']}: {feature['title']}")
    print(f"Type: {feature['type']}")
    print(f"Status: {feature['status']}")
    print(f"Created: {feature['date_created']}")
    
    if feature.get('description'):
        print(f"\nDescription:\n{feature['description']}")
    
    if feature.get('keywords'):
        keywords = ', '.join(feature['keywords'])
        print(f"\nKeywords: {keywords}")
    
    if feature.get('relations'):
        print(f"\nRelations:")
        for relation in feature['relations']:
            print(f"  {relation['type']}: {relation['target_id']}")
    
    if feature.get('documents'):
        print(f"\nDocuments:")
        for doc_type in feature['documents']:
            doc = feature['documents'][doc_type]
            print(f"  {doc_type}: Updated {doc['updated_at']}")


def print_project_status(stats: Dict[str, Any], project_name: str) -> None:
    """
    Print formatted project status information.
    
    Args:
        stats: Project statistics from ProjectLedgerManager
        project_name: Name of the project
    """
    print_header(f"Project Status: {project_name}")
    
    print(f"Total Features: {stats.get('total_features', 0)}")
    
    if 'by_status' in stats:
        print(f"\nBy Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status.replace('_', ' ').title()}: {count}")
    
    if 'by_type' in stats:
        print(f"\nBy Type:")
        for feature_type, count in stats['by_type'].items():
            print(f"  {feature_type.replace('_', ' ').title()}: {count}")