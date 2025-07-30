"""
gdd_manager.py
##############

This module provides the GDDManager class for handling Game Design Document (GDD) file operations
within Antigine projects. It manages the single gdd.md file per project, handles backups,
and provides create/update/import functionality.

The GDDManager integrates with the existing project structure and ensures proper file handling
for the GDD creation workflow.
"""

# Imports
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import json


class GDDManager:
    """
    Manages Game Design Document (GDD) file operations for Antigine projects.
    
    Handles the single gdd.md file per project with backup, versioning, and
    integration with the existing project structure.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize the GDD Manager for a specific project.
        
        Args:
            project_root (str): Path to the project root directory containing .antigine folder
        """
        self.project_root = Path(project_root).resolve()
        self.antigine_folder = self.project_root / ".antigine"
        self.docs_folder = self.project_root / "docs"
        self.gdd_file = self.docs_folder / "gdd.md"
        self.backup_folder = self.antigine_folder / "gdd_backups"
        
        # Validate project structure
        if not self.antigine_folder.exists():
            raise ValueError(f"Not an Antigine project: .antigine folder not found in {project_root}")
    
    def _ensure_docs_folder(self) -> None:
        """Create the docs folder if it doesn't exist."""
        self.docs_folder.mkdir(exist_ok=True)
    
    def _ensure_backup_folder(self) -> None:
        """Create the backup folder if it doesn't exist."""
        self.backup_folder.mkdir(exist_ok=True)
    
    def _create_backup(self) -> Optional[str]:
        """
        Create a backup of the existing GDD file if it exists.
        
        Returns:
            Optional[str]: Path to the backup file, or None if no backup was needed
        """
        if not self.gdd_file.exists():
            return None
        
        self._ensure_backup_folder()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"gdd_backup_{timestamp}.md"
        backup_path = self.backup_folder / backup_filename
        
        shutil.copy2(self.gdd_file, backup_path)
        return str(backup_path)
    
    def gdd_exists(self) -> bool:
        """
        Check if a GDD file already exists in the project.
        
        Returns:
            bool: True if gdd.md exists, False otherwise
        """
        return self.gdd_file.exists()
    
    def get_gdd_info(self) -> Dict[str, Any]:
        """
        Get information about the current GDD file.
        
        Returns:
            Dict[str, Any]: Dictionary containing GDD file information
        """
        if not self.gdd_exists():
            return {
                "exists": False,
                "path": str(self.gdd_file),
                "size": 0,
                "modified": None
            }
        
        stat = self.gdd_file.stat()
        return {
            "exists": True,
            "path": str(self.gdd_file),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def read_gdd(self) -> str:
        """
        Read the contents of the current GDD file.
        
        Returns:
            str: Contents of the GDD file
            
        Raises:
            FileNotFoundError: If the GDD file doesn't exist
        """
        if not self.gdd_exists():
            raise FileNotFoundError(f"GDD file not found: {self.gdd_file}")
        
        return self.gdd_file.read_text(encoding='utf-8')
    
    def create_gdd(self, content: str, backup_existing: bool = True) -> Tuple[bool, str]:
        """
        Create a new GDD file, optionally backing up any existing file.
        
        Args:
            content (str): The GDD content to write
            backup_existing (bool): Whether to backup existing GDD before overwriting
            
        Returns:
            Tuple[bool, str]: (success, message) indicating result and any relevant info
        """
        try:
            self._ensure_docs_folder()
            
            backup_path = None
            if backup_existing and self.gdd_exists():
                backup_path = self._create_backup()
            
            # Write the new GDD content
            self.gdd_file.write_text(content, encoding='utf-8')
            
            if backup_path:
                return True, f"GDD created successfully. Previous version backed up to: {backup_path}"
            else:
                return True, "GDD created successfully."
                
        except Exception as e:
            return False, f"Failed to create GDD: {str(e)}"
    
    def update_gdd(self, content: str, backup_existing: bool = True) -> Tuple[bool, str]:
        """
        Update the existing GDD file with new content.
        
        Args:
            content (str): The updated GDD content
            backup_existing (bool): Whether to backup existing GDD before updating
            
        Returns:
            Tuple[bool, str]: (success, message) indicating result and any relevant info
        """
        if not self.gdd_exists():
            return False, "No existing GDD found. Use create_gdd() instead."
        
        return self.create_gdd(content, backup_existing)
    
    def import_gdd(self, source_path: str, backup_existing: bool = True) -> Tuple[bool, str]:
        """
        Import a GDD file from an external source.
        
        Args:
            source_path (str): Path to the GDD file to import
            backup_existing (bool): Whether to backup existing GDD before importing
            
        Returns:
            Tuple[bool, str]: (success, message) indicating result and any relevant info
        """
        source = Path(source_path)
        
        if not source.exists():
            return False, f"Source file not found: {source_path}"
        
        if not source.suffix.lower() == '.md':
            return False, "Source file must be a Markdown (.md) file"
        
        try:
            content = source.read_text(encoding='utf-8')
            return self.create_gdd(content, backup_existing)
            
        except Exception as e:
            return False, f"Failed to import GDD: {str(e)}"
    
    def list_backups(self) -> list[Dict[str, Any]]:
        """
        List all available GDD backups.
        
        Returns:
            list[Dict[str, Any]]: List of backup file information
        """
        if not self.backup_folder.exists():
            return []
        
        backups = []
        for backup_file in self.backup_folder.glob("gdd_backup_*.md"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        
        # Sort by creation time, newest first
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def restore_backup(self, backup_filename: str, backup_current: bool = True) -> Tuple[bool, str]:
        """
        Restore a GDD from a backup file.
        
        Args:
            backup_filename (str): Name of the backup file to restore
            backup_current (bool): Whether to backup the current GDD before restoring
            
        Returns:
            Tuple[bool, str]: (success, message) indicating result and any relevant info
        """
        backup_path = self.backup_folder / backup_filename
        
        if not backup_path.exists():
            return False, f"Backup file not found: {backup_filename}"
        
        try:
            content = backup_path.read_text(encoding='utf-8')
            return self.create_gdd(content, backup_current)
            
        except Exception as e:
            return False, f"Failed to restore backup: {str(e)}"
    
    def get_project_structure_info(self) -> Dict[str, Any]:
        """
        Get information about the project's documentation structure.
        
        Returns:
            Dict[str, Any]: Information about project folders and files
        """
        return {
            "project_root": str(self.project_root),
            "docs_folder": {
                "path": str(self.docs_folder),
                "exists": self.docs_folder.exists()
            },
            "gdd_file": self.get_gdd_info(),
            "backup_folder": {
                "path": str(self.backup_folder),
                "exists": self.backup_folder.exists(),
                "backup_count": len(self.list_backups())
            }
        }