"""
test_database_operations.py
###########################

Unit tests for database operations and ProjectLedgerManager functionality.
Uses in-memory SQLite databases for testing without side effects.
"""

import unittest
import tempfile
import os
import json
import shutil
from datetime import datetime
from antigine.core.database import initialize_database, get_connection, validate_database_schema
from antigine.managers.ProjectLedgerManager import ProjectLedgerManager


class TestDatabaseOperations(unittest.TestCase):
    """Test cases for core database operations."""

    def setUp(self):
        """Set up test fixtures with temporary database file."""
        # Use temporary file for testing (in-memory doesn't work with directory creation)
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_file.name
        self.temp_file.close()  # Close so we can use the path
        initialize_database(self.db_path)

    def tearDown(self):
        """Clean up temporary database file."""
        try:
            os.unlink(self.db_path)
        except (OSError, FileNotFoundError):
            pass  # File might already be deleted

    def test_database_tables_exist(self):
        """Test that database has required tables."""
        # Use the already-initialized database from setUp
        with get_connection(self.db_path) as conn:
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
        # Use the database from setUp which is already valid
        self.assertTrue(validate_database_schema(self.db_path))

    def test_validate_database_schema_missing_file(self):
        """Test schema validation with missing database file."""
        self.assertFalse(validate_database_schema("/nonexistent/path/db.sqlite"))

    def test_database_connection_works(self):
        """Test that database connection works correctly."""
        # Test connection to existing database
        with get_connection(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM features")
            result = cursor.fetchone()
            self.assertEqual(result[0], 0)  # Should be empty initially


class TestProjectLedgerManager(unittest.TestCase):
    """Test cases for ProjectLedgerManager functionality."""

    def setUp(self):
        """Set up test fixtures with temporary project directory."""
        # Create temporary directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.project_folder = self.temp_dir

        # Create .antigine folder and database
        antigine_folder = os.path.join(self.project_folder, ".antigine")
        os.makedirs(antigine_folder, exist_ok=True)

        self.db_path = os.path.join(antigine_folder, "ledger.db")
        initialize_database(self.db_path)

        # Create project configuration
        self.config_path = os.path.join(antigine_folder, "project.json")
        project_config = {
            "project_name": "TestProject",
            "project_initials": "TP",
            "project_language": "C++",
            "tech_stack": "SDL2+OpenGL",
        }
        with open(self.config_path, "w") as f:
            json.dump(project_config, f)

        # Initialize manager
        self.manager = ProjectLedgerManager(self.project_folder)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manager_initialization(self):
        """Test that ProjectLedgerManager initializes correctly."""
        self.assertEqual(self.manager.project_folder, self.project_folder)
        self.assertEqual(self.manager.project_name, "TestProject")
        self.assertEqual(self.manager.project_initials, "TP")
        self.assertEqual(self.manager.db_path, self.db_path)

    def test_add_feature_basic(self):
        """Test adding a basic feature."""
        feature_data = {
            "type": "new_feature",
            "title": "Test Feature",
            "description": "A test feature for unit testing",
            "keywords": ["test", "example"],
        }

        feature_id = self.manager.add_feature(feature_data)

        # Should generate correct ID format
        self.assertEqual(feature_id, "TP-001")

        # Feature should be retrievable
        retrieved_feature = self.manager.get_feature_by_id(feature_id)
        self.assertIsNotNone(retrieved_feature)
        self.assertEqual(retrieved_feature["title"], "Test Feature")
        self.assertEqual(retrieved_feature["type"], "new_feature")
        self.assertEqual(retrieved_feature["status"], "requested")

    def test_add_multiple_features_increments_id(self):
        """Test that adding multiple features increments IDs correctly."""
        feature1_data = {"type": "new_feature", "title": "Feature 1"}
        feature2_data = {"type": "bug_fix", "title": "Feature 2"}

        id1 = self.manager.add_feature(feature1_data)
        id2 = self.manager.add_feature(feature2_data)

        self.assertEqual(id1, "TP-001")
        self.assertEqual(id2, "TP-002")

    def test_add_feature_with_relations(self):
        """Test adding a feature with relations to other features."""
        # Add base feature first
        base_feature = {"type": "new_feature", "title": "Base Feature"}
        base_id = self.manager.add_feature(base_feature)

        # Add feature with relation
        related_feature = {
            "type": "enhancement",
            "title": "Related Feature",
            "relations": [{"type": "builds_on", "target_id": base_id}],
        }

        related_id = self.manager.add_feature(related_feature)

        # Check that relation was stored
        retrieved = self.manager.get_feature_by_id(related_id)
        self.assertEqual(len(retrieved["relations"]), 1)
        self.assertEqual(retrieved["relations"][0]["type"], "builds_on")
        self.assertEqual(retrieved["relations"][0]["target_id"], base_id)

    def test_get_feature_by_id_nonexistent(self):
        """Test getting a feature that doesn't exist."""
        result = self.manager.get_feature_by_id("TP-999")
        self.assertIsNone(result)

    def test_get_features_by_status(self):
        """Test getting features filtered by status."""
        # Add features with different statuses
        feature1 = {"type": "new_feature", "title": "Feature 1"}
        feature2 = {"type": "bug_fix", "title": "Feature 2"}

        id1 = self.manager.add_feature(feature1)
        id2 = self.manager.add_feature(feature2)

        # Update one feature's status
        self.manager.update_feature_status(id2, "awaiting_implementation")

        # Test filtering
        requested_features = self.manager.get_features_by_status("requested")
        awaiting_features = self.manager.get_features_by_status("awaiting_implementation")

        self.assertEqual(len(requested_features), 1)
        self.assertEqual(requested_features[0]["feature_id"], id1)

        self.assertEqual(len(awaiting_features), 1)
        self.assertEqual(awaiting_features[0]["feature_id"], id2)

    def test_update_feature_status(self):
        """Test updating feature status."""
        feature_data = {"type": "new_feature", "title": "Test Feature"}
        feature_id = self.manager.add_feature(feature_data)

        # Update status
        success = self.manager.update_feature_status(feature_id, "awaiting_implementation")
        self.assertTrue(success)

        # Verify update
        feature = self.manager.get_feature_by_id(feature_id)
        self.assertEqual(feature["status"], "awaiting_implementation")

        # Test updating non-existent feature
        success = self.manager.update_feature_status("TP-999", "validated")
        self.assertFalse(success)

    def test_mark_feature_implemented(self):
        """Test marking a feature as implemented."""
        feature_data = {"type": "new_feature", "title": "Test Feature"}
        feature_id = self.manager.add_feature(feature_data)

        commit_hash = "abc123def"
        changed_files = ["src/main.cpp", "include/game.h"]

        success = self.manager.mark_feature_implemented(feature_id, commit_hash, changed_files)
        self.assertTrue(success)

        # Verify implementation details were stored
        feature = self.manager.get_feature_by_id(feature_id)
        self.assertEqual(feature["status"], "validated")
        self.assertEqual(feature["commit_hash"], commit_hash)
        self.assertEqual(feature["changed_files"], changed_files)
        self.assertIsNotNone(feature["date_implemented"])

    def test_mark_feature_superseded(self):
        """Test marking a feature as superseded."""
        feature_data = {"type": "new_feature", "title": "Test Feature"}
        feature_id = self.manager.add_feature(feature_data)

        success = self.manager.mark_feature_superseded(feature_id)
        self.assertTrue(success)

        feature = self.manager.get_feature_by_id(feature_id)
        self.assertEqual(feature["status"], "superseded")
        self.assertIsNotNone(feature["date_superseded"])

    def test_add_feature_document(self):
        """Test adding documents to features."""
        feature_data = {"type": "new_feature", "title": "Test Feature"}
        feature_id = self.manager.add_feature(feature_data)

        # Add feature request document
        doc_content = "This is a detailed feature request document."
        success = self.manager.add_feature_document(feature_id, "feature_request", doc_content)
        self.assertTrue(success)

        # Verify document was stored
        feature = self.manager.get_feature_by_id(feature_id)
        self.assertIn("feature_request", feature["documents"])
        self.assertEqual(feature["documents"]["feature_request"]["content"], doc_content)
        self.assertIsNotNone(feature["documents"]["feature_request"]["created_at"])

    def test_keyword_search(self):
        """Test keyword search functionality."""
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

        self.manager.add_feature(feature1)
        self.manager.add_feature(feature2)

        # Search for "player"
        results = self.manager.keyword_search(["player"])
        self.assertEqual(len(results), 1)
        self.assertIn("Player Movement", results[0]["title"])

        # Search for "movement"
        results = self.manager.keyword_search(["movement"])
        self.assertEqual(len(results), 1)

        # Search for non-existent term
        results = self.manager.keyword_search(["nonexistent"])
        self.assertEqual(len(results), 0)

    def test_get_feature_statistics(self):
        """Test feature statistics generation."""
        # Add features with different types and statuses
        features_data = [
            {"type": "new_feature", "title": "Feature 1"},
            {"type": "new_feature", "title": "Feature 2"},
            {"type": "bug_fix", "title": "Bug Fix 1"},
            {"type": "enhancement", "title": "Enhancement 1"},
        ]

        ids = []
        for feature_data in features_data:
            feature_id = self.manager.add_feature(feature_data)
            ids.append(feature_id)

        # Update some statuses
        self.manager.update_feature_status(ids[1], "awaiting_implementation")
        self.manager.update_feature_status(ids[2], "validated")

        stats = self.manager.get_feature_statistics()

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
        # Remove config file
        os.unlink(self.config_path)

        # Should raise FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            ProjectLedgerManager(self.project_folder)

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
            with self.assertRaises(Exception):  # Could be sqlite3.Error or other
                ProjectLedgerManager(temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
