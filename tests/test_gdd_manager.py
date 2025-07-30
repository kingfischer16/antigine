"""
test_gdd_manager.py
###################

Unit tests for the GDDManager class.
Tests GDD file operations, backup functionality, and project structure management.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import time

from antigine.core.gdd_manager import GDDManager


class TestGDDManager(unittest.TestCase):
    """Test cases for GDDManager class."""
    
    def setUp(self):
        """Set up test environment with temporary project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create .antigine folder to simulate valid project
        self.antigine_folder = self.project_root / ".antigine"
        self.antigine_folder.mkdir()
        
        # Initialize GDDManager
        self.gdd_manager = GDDManager(str(self.project_root))
        
        # Sample GDD content for testing
        self.sample_gdd = """# Test Game Design Document

## Core Vision
This is a test game for unit testing.

## MDA Breakdown
- Mechanics: Jump and run
- Dynamics: Platforming challenges
- Aesthetics: Fun and engaging

## Features
- Basic movement
- Simple graphics
"""
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_init_valid_project(self):
        """Test GDDManager initialization with valid project."""
        manager = GDDManager(str(self.project_root))
        self.assertEqual(manager.project_root, self.project_root)
        self.assertEqual(manager.docs_folder, self.project_root / "docs")
        self.assertEqual(manager.gdd_file, self.project_root / "docs" / "gdd.md")
    
    def test_init_invalid_project(self):
        """Test GDDManager initialization with invalid project (no .antigine folder)."""
        invalid_dir = tempfile.mkdtemp()
        try:
            with self.assertRaises(ValueError) as context:
                GDDManager(invalid_dir)
            self.assertIn("Not an Antigine project", str(context.exception))
        finally:
            shutil.rmtree(invalid_dir)
    
    def test_gdd_exists_false_initially(self):
        """Test that GDD doesn't exist initially."""
        self.assertFalse(self.gdd_manager.gdd_exists())
    
    def test_create_gdd_new(self):
        """Test creating a new GDD file."""
        success, message = self.gdd_manager.create_gdd(self.sample_gdd)
        
        self.assertTrue(success)
        self.assertIn("GDD created successfully", message)
        self.assertTrue(self.gdd_manager.gdd_exists())
        self.assertEqual(self.gdd_manager.read_gdd(), self.sample_gdd)
    
    def test_create_gdd_with_backup(self):
        """Test creating GDD with backup of existing file."""
        # First, create initial GDD
        self.gdd_manager.create_gdd("Initial content")
        
        # Then create new GDD, should backup the old one
        new_content = "Updated content"
        success, message = self.gdd_manager.create_gdd(new_content, backup_existing=True)
        
        self.assertTrue(success)
        self.assertIn("backed up", message)
        self.assertEqual(self.gdd_manager.read_gdd(), new_content)
        
        # Check that backup was created
        backups = self.gdd_manager.list_backups()
        self.assertEqual(len(backups), 1)
    
    def test_create_gdd_without_backup(self):
        """Test creating GDD without backup."""
        # First, create initial GDD
        self.gdd_manager.create_gdd("Initial content")
        
        # Then create new GDD without backup
        new_content = "Updated content"
        success, message = self.gdd_manager.create_gdd(new_content, backup_existing=False)
        
        self.assertTrue(success)
        self.assertNotIn("backed up", message)
        self.assertEqual(self.gdd_manager.read_gdd(), new_content)
        
        # Check that no backup was created
        backups = self.gdd_manager.list_backups()
        self.assertEqual(len(backups), 0)
    
    def test_update_gdd_existing(self):
        """Test updating existing GDD file."""
        # Create initial GDD
        self.gdd_manager.create_gdd("Initial content")
        
        # Update it
        updated_content = "Updated content"
        success, message = self.gdd_manager.update_gdd(updated_content)
        
        self.assertTrue(success)
        self.assertIn("GDD created successfully", message)
        self.assertEqual(self.gdd_manager.read_gdd(), updated_content)
    
    def test_update_gdd_nonexistent(self):
        """Test updating non-existent GDD file."""
        success, message = self.gdd_manager.update_gdd("Content")
        
        self.assertFalse(success)
        self.assertIn("No existing GDD found", message)
    
    def test_import_gdd_valid_file(self):
        """Test importing GDD from external file."""
        # Create temporary source file
        source_file = self.project_root / "source.md"
        source_file.write_text("Imported content", encoding='utf-8')
        
        success, message = self.gdd_manager.import_gdd(str(source_file))
        
        self.assertTrue(success)
        self.assertIn("GDD created successfully", message)
        self.assertEqual(self.gdd_manager.read_gdd(), "Imported content")
    
    def test_import_gdd_nonexistent_file(self):
        """Test importing from non-existent file."""
        success, message = self.gdd_manager.import_gdd("nonexistent.md")
        
        self.assertFalse(success)
        self.assertIn("Source file not found", message)
    
    def test_import_gdd_wrong_extension(self):
        """Test importing from file with wrong extension."""
        # Create temporary source file with wrong extension
        source_file = self.project_root / "source.txt"
        source_file.write_text("Content", encoding='utf-8')
        
        success, message = self.gdd_manager.import_gdd(str(source_file))
        
        self.assertFalse(success)
        self.assertIn("must be a Markdown (.md) file", message)
    
    def test_read_gdd_existing(self):
        """Test reading existing GDD file."""
        self.gdd_manager.create_gdd(self.sample_gdd)
        content = self.gdd_manager.read_gdd()
        self.assertEqual(content, self.sample_gdd)
    
    def test_read_gdd_nonexistent(self):
        """Test reading non-existent GDD file."""
        with self.assertRaises(FileNotFoundError):
            self.gdd_manager.read_gdd()
    
    def test_get_gdd_info_existing(self):
        """Test getting info for existing GDD."""
        self.gdd_manager.create_gdd(self.sample_gdd)
        info = self.gdd_manager.get_gdd_info()
        
        self.assertTrue(info["exists"])
        self.assertGreater(info["size"], 0)
        self.assertIsNotNone(info["modified"])
        self.assertIn("gdd.md", info["path"])
    
    def test_get_gdd_info_nonexistent(self):
        """Test getting info for non-existent GDD."""
        info = self.gdd_manager.get_gdd_info()
        
        self.assertFalse(info["exists"])
        self.assertEqual(info["size"], 0)
        self.assertIsNone(info["modified"])
    
    def test_list_backups_empty(self):
        """Test listing backups when none exist."""
        backups = self.gdd_manager.list_backups()
        self.assertEqual(len(backups), 0)
    
    def test_list_backups_with_backups(self):
        """Test listing backups when they exist."""
        # Create initial GDD
        self.gdd_manager.create_gdd("Content 1")
        time.sleep(2)  # Ensure different timestamps 
        
        # Update GDD (creates first backup)
        self.gdd_manager.update_gdd("Content 2")
        time.sleep(2)  # Ensure different timestamps
        
        # Update again (creates second backup)
        self.gdd_manager.update_gdd("Content 3")
        
        backups = self.gdd_manager.list_backups()
        
        # Each update should create one backup, so we expect 2 backups total
        self.assertEqual(len(backups), 2)
        
        # Check that backups are sorted by creation time (newest first)
        self.assertGreater(backups[0]["created"], backups[1]["created"])
    
    def test_restore_backup_existing(self):
        """Test restoring from existing backup."""
        # Create initial GDD and update it (creates backup)
        original_content = "Original content"
        self.gdd_manager.create_gdd(original_content)
        self.gdd_manager.update_gdd("Updated content")
        
        # Get backup filename
        backups = self.gdd_manager.list_backups()
        backup_filename = backups[0]["filename"]
        
        # Restore backup
        success, message = self.gdd_manager.restore_backup(backup_filename)
        
        self.assertTrue(success)
        self.assertIn("GDD created successfully", message)
        self.assertEqual(self.gdd_manager.read_gdd(), original_content)
    
    def test_restore_backup_nonexistent(self):
        """Test restoring from non-existent backup."""
        success, message = self.gdd_manager.restore_backup("nonexistent_backup.md")
        
        self.assertFalse(success)
        self.assertIn("Backup file not found", message)
    
    def test_get_project_structure_info(self):
        """Test getting project structure information."""
        # Create GDD and backup
        self.gdd_manager.create_gdd("Content")
        self.gdd_manager.update_gdd("Updated content")
        
        info = self.gdd_manager.get_project_structure_info()
        
        self.assertIn("project_root", info)
        self.assertIn("docs_folder", info)
        self.assertIn("gdd_file", info)
        self.assertIn("backup_folder", info)
        
        self.assertTrue(info["docs_folder"]["exists"])
        self.assertTrue(info["gdd_file"]["exists"])
        self.assertEqual(info["backup_folder"]["backup_count"], 1)
    
    def test_docs_folder_creation(self):
        """Test that docs folder is created when needed."""
        # Initially, docs folder shouldn't exist
        self.assertFalse(self.gdd_manager.docs_folder.exists())
        
        # Creating GDD should create docs folder
        self.gdd_manager.create_gdd("Content")
        self.assertTrue(self.gdd_manager.docs_folder.exists())
    
    def test_backup_folder_creation(self):
        """Test that backup folder is created when needed."""
        # Initially, backup folder shouldn't exist
        self.assertFalse(self.gdd_manager.backup_folder.exists())
        
        # Creating GDD with backup should create backup folder
        self.gdd_manager.create_gdd("Initial content")
        self.gdd_manager.update_gdd("Updated content")  # This creates backup
        
        self.assertTrue(self.gdd_manager.backup_folder.exists())


if __name__ == '__main__':
    unittest.main()