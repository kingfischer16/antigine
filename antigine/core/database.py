"""
database.py
###########

This module provides database schema and initialization functions for the SQLite ledger database.
It defines the structure for storing features, relations, and documents in the project ledger.

This module cannot import from other modules in this package to avoid circular dependencies.
"""

# Imports
import sqlite3
import os
from typing import Optional


# Database schema SQL statements
SCHEMA_SQL = """
-- Features table (main ledger)
CREATE TABLE IF NOT EXISTS features (
    feature_id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('new_feature', 'bug_fix', 'refactor', 'enhancement')),
    status TEXT NOT NULL CHECK (status IN ('requested', 'in_review', 'awaiting_implementation', 'awaiting_validation', 'validated', 'superseded')),
    title TEXT NOT NULL,
    description TEXT,
    keywords TEXT, -- JSON array as text
    date_created TEXT NOT NULL,
    date_implemented TEXT,
    date_superseded TEXT,
    commit_hash TEXT,
    changed_files TEXT -- JSON array as text
);

-- Feature relations table
CREATE TABLE IF NOT EXISTS feature_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_id TEXT NOT NULL,
    relation_type TEXT NOT NULL CHECK (relation_type IN ('builds_on', 'supersedes', 'refactors', 'fixes')),
    target_id TEXT NOT NULL,
    FOREIGN KEY (feature_id) REFERENCES features (feature_id),
    FOREIGN KEY (target_id) REFERENCES features (feature_id)
);

-- Documents table (for artifacts)
CREATE TABLE IF NOT EXISTS feature_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_id TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN ('feature_request', 'technical_architecture_specification', 'feature_implementation_plan')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (feature_id) REFERENCES features (feature_id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_features_status ON features(status);
CREATE INDEX IF NOT EXISTS idx_features_type ON features(type);
CREATE INDEX IF NOT EXISTS idx_feature_relations_feature_id ON feature_relations(feature_id);
CREATE INDEX IF NOT EXISTS idx_feature_relations_target_id ON feature_relations(target_id);
CREATE INDEX IF NOT EXISTS idx_feature_documents_feature_id ON feature_documents(feature_id);
CREATE INDEX IF NOT EXISTS idx_feature_documents_type ON feature_documents(document_type);
"""


def initialize_database(db_path: str) -> None:
    """
    Initialize the SQLite database with the required schema.
    
    Args:
        db_path (str): Path to the SQLite database file.
        
    Raises:
        sqlite3.Error: If database initialization fails.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Execute schema creation
            conn.executescript(SCHEMA_SQL)
            
            # Commit changes
            conn.commit()
            
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to initialize database at {db_path}: {e}")


def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Get a connection to the SQLite database with proper configuration.
    
    Args:
        db_path (str): Path to the SQLite database file.
        
    Returns:
        sqlite3.Connection: Configured database connection.
        
    Raises:
        sqlite3.Error: If connection fails.
    """
    if not os.path.exists(db_path):
        raise sqlite3.Error(f"Database file does not exist: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Configure connection
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Enable dict-like row access
        
        return conn
        
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to connect to database at {db_path}: {e}")


def validate_database_schema(db_path: str) -> bool:
    """
    Validate that the database has the expected schema.
    
    Args:
        db_path (str): Path to the SQLite database file.
        
    Returns:
        bool: True if schema is valid, False otherwise.
    """
    expected_tables = {'features', 'feature_relations', 'feature_documents'}
    
    try:
        with get_connection(db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            return expected_tables.issubset(existing_tables)
            
    except sqlite3.Error:
        return False