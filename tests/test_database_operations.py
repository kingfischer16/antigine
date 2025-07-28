"""
test_database_operations.py
###########################

Unit tests for database operations and ProjectLedgerManager functionality.
Uses temporary files with proper context managers for testing without side effects.
"""

import unittest
import tempfile
import os
import json
import shutil
from contextlib import contextmanager
from antigine.core.database import initialize_database, get_connection, validate_database_schema
from antigine.managers.ProjectLedgerManager import ProjectLedgerManager


@contextmanager
def temporary_database():
    """Context manager that creates a temporary database file and ensures cleanup."""
    # Create temporary file with proper suffix
    fd, temp_path = tempfile.mkstemp(suffix=".db")
    try:
        # Close the file descriptor since we just need the path
        os.close(fd)
        # Initialize the database
        initialize_database(temp_path)
        yield temp_path
    finally:
        # Ensure cleanup even if an exception occurs
        try:
            os.unlink(temp_path)
        except (OSError, FileNotFoundError):
            pass  # File might already be deleted


@contextmanager
def temporary_project():
    """Context manager that creates a temporary project structure and ensures cleanup."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Create .antigine folder and database
        antigine_folder = os.path.join(temp_dir, ".antigine")
        os.makedirs(antigine_folder, exist_ok=True)

        db_path = os.path.join(antigine_folder, "ledger.db")
        initialize_database(db_path)

        # Create project configuration
        config_path = os.path.join(antigine_folder, "project.json")
        project_config = {
            "project_name": "TestProject",
            "project_initials": "TP",
            "project_language": "C++",
            "tech_stack": "SDL2+OpenGL",
        }
        with open(config_path, "w") as f:
            json.dump(project_config, f)

        yield temp_dir
    finally:
        # Ensure cleanup even if an exception occurs
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestDatabaseOperations(unittest.TestCase):
    """Test cases for core database operations."""

    def test_database_tables_exist(self):
        """Test that database has required tables."""
        with temporary_database() as db_path:
            with get_connection(db_path) as conn:
                # Check that tables exist
                cursor = conn.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """
                )
                tables = [row[0] for row in cursor.fetchall()]

                expected_tables = ["features", "feature_relations", "feature_documents"]
                for table in expected_tables:
                    self.assertIn(table, tables, f"Table {table} not created")

    def test_validate_database_schema_with_existing(self):
        """Test schema validation with existing valid database."""
        with temporary_database() as db_path:
            self.assertTrue(validate_database_schema(db_path))

    def test_validate_database_schema_missing_file(self):
        """Test schema validation with missing database file."""
        self.assertFalse(validate_database_schema("/nonexistent/path/db.sqlite"))

    def test_database_connection_works(self):
        """Test that database connection works correctly."""
        with temporary_database() as db_path:
            with get_connection(db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM features")
                result = cursor.fetchone()
                self.assertEqual(result[0], 0)  # Should be empty initially


class TestProjectLedgerManager(unittest.TestCase):
    """Test cases for ProjectLedgerManager functionality."""

    def test_manager_initialization(self):
        """Test that ProjectLedgerManager initializes correctly."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            db_path = os.path.join(project_folder, ".antigine", "ledger.db")

            self.assertEqual(manager.project_folder, project_folder)
            self.assertEqual(manager.project_name, "TestProject")
            self.assertEqual(manager.project_initials, "TP")
            self.assertEqual(manager.db_path, db_path)

    def test_add_feature_basic(self):
        """Test adding a basic feature."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            feature_data = {
                "type": "new_feature",
                "title": "Test Feature",
                "description": "A test feature for unit testing",
                "keywords": ["test", "example"],
            }

            feature_id = manager.add_feature(feature_data)

            # Should generate correct ID format
            self.assertEqual(feature_id, "TP-001")

            # Feature should be retrievable
            retrieved_feature = manager.get_feature_by_id(feature_id)
            self.assertIsNotNone(retrieved_feature)
            self.assertEqual(retrieved_feature["title"], "Test Feature")
            self.assertEqual(retrieved_feature["type"], "new_feature")
            self.assertEqual(retrieved_feature["status"], "requested")

    def test_add_multiple_features_increments_id(self):
        """Test that adding multiple features increments IDs correctly."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            feature1_data = {"type": "new_feature", "title": "Feature 1"}
            feature2_data = {"type": "bug_fix", "title": "Feature 2"}

            id1 = manager.add_feature(feature1_data)
            id2 = manager.add_feature(feature2_data)

            self.assertEqual(id1, "TP-001")
            self.assertEqual(id2, "TP-002")

    def test_add_feature_with_relations(self):
        """Test adding a feature with relations to other features."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            # Add base feature first
            base_feature = {"type": "new_feature", "title": "Base Feature"}
            base_id = manager.add_feature(base_feature)

            # Add feature with relation
            related_feature = {
                "type": "enhancement",
                "title": "Related Feature",
                "relations": [{"type": "builds_on", "target_id": base_id}],
            }

            related_id = manager.add_feature(related_feature)

            # Check that relation was stored
            retrieved = manager.get_feature_by_id(related_id)
            self.assertEqual(len(retrieved["relations"]), 1)
            self.assertEqual(retrieved["relations"][0]["type"], "builds_on")
            self.assertEqual(retrieved["relations"][0]["target_id"], base_id)

    def test_get_feature_by_id_nonexistent(self):
        """Test getting a feature that doesn't exist."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            result = manager.get_feature_by_id("TP-999")
            self.assertIsNone(result)

    def test_get_features_by_status(self):
        """Test getting features filtered by status."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            # Add features with different statuses
            feature1 = {"type": "new_feature", "title": "Feature 1"}
            feature2 = {"type": "bug_fix", "title": "Feature 2"}

            id1 = manager.add_feature(feature1)
            id2 = manager.add_feature(feature2)

            # Update one feature's status
            manager.update_feature_status(id2, "awaiting_implementation")

            # Test filtering
            requested_features = manager.get_features_by_status("requested")
            awaiting_features = manager.get_features_by_status("awaiting_implementation")

            self.assertEqual(len(requested_features), 1)
            self.assertEqual(requested_features[0]["feature_id"], id1)

            self.assertEqual(len(awaiting_features), 1)
            self.assertEqual(awaiting_features[0]["feature_id"], id2)

    def test_update_feature_status(self):
        """Test updating feature status."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            feature_data = {"type": "new_feature", "title": "Test Feature"}
            feature_id = manager.add_feature(feature_data)

            # Update status
            success = manager.update_feature_status(feature_id, "awaiting_implementation")
            self.assertTrue(success)

            # Verify update
            feature = manager.get_feature_by_id(feature_id)
            self.assertEqual(feature["status"], "awaiting_implementation")

            # Test updating non-existent feature
            success = manager.update_feature_status("TP-999", "validated")
            self.assertFalse(success)

    def test_mark_feature_implemented(self):
        """Test marking a feature as implemented."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            feature_data = {"type": "new_feature", "title": "Test Feature"}
            feature_id = manager.add_feature(feature_data)

            commit_hash = "abc123def"
            changed_files = ["src/main.cpp", "include/game.h"]

            success = manager.mark_feature_implemented(feature_id, commit_hash, changed_files)
            self.assertTrue(success)

            # Verify implementation details were stored
            feature = manager.get_feature_by_id(feature_id)
            self.assertEqual(feature["status"], "validated")
            self.assertEqual(feature["commit_hash"], commit_hash)
            self.assertEqual(feature["changed_files"], changed_files)
            self.assertIsNotNone(feature["date_implemented"])

    def test_mark_feature_superseded(self):
        """Test marking a feature as superseded."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            feature_data = {"type": "new_feature", "title": "Test Feature"}
            feature_id = manager.add_feature(feature_data)

            success = manager.mark_feature_superseded(feature_id)
            self.assertTrue(success)

            feature = manager.get_feature_by_id(feature_id)
            self.assertEqual(feature["status"], "superseded")
            self.assertIsNotNone(feature["date_superseded"])

    def test_add_feature_document(self):
        """Test adding documents to features."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            feature_data = {"type": "new_feature", "title": "Test Feature"}
            feature_id = manager.add_feature(feature_data)

            # Add feature request document
            doc_content = "This is a detailed feature request document."
            success = manager.add_feature_document(feature_id, "feature_request", doc_content)
            self.assertTrue(success)

            # Verify document was stored
            feature = manager.get_feature_by_id(feature_id)
            self.assertIn("feature_request", feature["documents"])
            self.assertEqual(feature["documents"]["feature_request"]["content"], doc_content)
            self.assertIsNotNone(feature["documents"]["feature_request"]["created_at"])

    def test_keyword_search(self):
        """Test keyword search functionality."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            # Add features with different keywords
            feature1 = {
                "type": "new_feature",
                "title": "Player Movement",
                "description": "Implement player character movement",
                "keywords": ["player", "movement", "input"],
            }
            feature2 = {
                "type": "new_feature",
                "title": "Enemy AI",
                "description": "Create enemy artificial intelligence",
                "keywords": ["enemy", "ai", "behavior"],
            }

            manager.add_feature(feature1)
            manager.add_feature(feature2)

            # Search for "player"
            results = manager.keyword_search(["player"])
            self.assertEqual(len(results), 1)
            self.assertIn("Player Movement", results[0]["title"])

            # Search for "movement"
            results = manager.keyword_search(["movement"])
            self.assertEqual(len(results), 1)

            # Search for non-existent term
            results = manager.keyword_search(["nonexistent"])
            self.assertEqual(len(results), 0)

    def test_get_feature_statistics(self):
        """Test feature statistics generation."""
        with temporary_project() as project_folder:
            manager = ProjectLedgerManager(project_folder)
            # Add features with different types and statuses
            features_data = [
                {"type": "new_feature", "title": "Feature 1"},
                {"type": "new_feature", "title": "Feature 2"},
                {"type": "bug_fix", "title": "Bug Fix 1"},
                {"type": "enhancement", "title": "Enhancement 1"},
            ]

            ids = []
            for feature_data in features_data:
                feature_id = manager.add_feature(feature_data)
                ids.append(feature_id)

            # Update some statuses
            manager.update_feature_status(ids[1], "awaiting_implementation")
            manager.update_feature_status(ids[2], "validated")

            stats = manager.get_feature_statistics()

            # Check total count
            self.assertEqual(stats["total_features"], 4)

            # Check status counts
            self.assertEqual(stats["by_status"]["requested"], 2)
            self.assertEqual(stats["by_status"]["awaiting_implementation"], 1)
            self.assertEqual(stats["by_status"]["validated"], 1)

            # Check type counts
            self.assertEqual(stats["by_type"]["new_feature"], 2)
            self.assertEqual(stats["by_type"]["bug_fix"], 1)
            self.assertEqual(stats["by_type"]["enhancement"], 1)

    def test_manager_with_missing_config(self):
        """Test manager behavior with missing project configuration."""
        with temporary_project() as project_folder:
            # Remove config file
            config_path = os.path.join(project_folder, ".antigine", "project.json")
            os.unlink(config_path)

            # Should raise FileNotFoundError
            with self.assertRaises(FileNotFoundError):
                ProjectLedgerManager(project_folder)

    def test_manager_with_invalid_database(self):
        """Test manager behavior with invalid database."""
        # Create a new temp directory to avoid file locking issues
        temp_dir = tempfile.mkdtemp()
        try:
            antigine_folder = os.path.join(temp_dir, ".antigine")
            os.makedirs(antigine_folder)

            # Create invalid config
            config_path = os.path.join(antigine_folder, "project.json")
            with open(config_path, "w") as f:
                json.dump({"project_name": "Test", "project_initials": "T"}, f)

            # Don't create database - this should cause an error
            # Should raise sqlite3.Error
            with self.assertRaises(sqlite3.Error):  # Catch specific database error
                ProjectLedgerManager(temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
