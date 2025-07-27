"""
ProjectLedgerManager.py
#######################

This module provides the ProjectLedgerManager class, which is responsible for managing project ledgers
using SQLite database for persistent storage of features, relations, and documents.

The manager handles all CRUD operations for features and maintains data integrity through proper
database transactions and foreign key constraints.
"""

# Imports
from datetime import datetime
import os
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from ..core.database import get_connection, validate_database_schema


class ProjectLedgerManager:
    """
    ProjectLedgerManager handles all interactions with the project ledger SQLite database.
    
    The ledger stores:
    - Features: Main entries with metadata, status, and timestamps
    - Relations: Dependencies and relationships between features  
    - Documents: Feature request documents, FIPs, and ADRs
    """
    
    def __init__(self, project_folder: str):
        """
        Initialize the ProjectLedgerManager with database connection.
        
        Args:
            project_folder (str): The path to the game project folder.
            
        Raises:
            sqlite3.Error: If database connection or validation fails.
            FileNotFoundError: If project configuration is missing.
        """
        # Create instance attributes
        self.project_folder = project_folder
        self.db_path = os.path.join(self.project_folder, ".antigine", "ledger.db")
        self.project_config_path = os.path.join(self.project_folder, ".antigine", "project.json")
        
        # Validate database exists and has correct schema
        if not validate_database_schema(self.db_path):
            raise sqlite3.Error(f"Invalid or missing database schema at {self.db_path}")
        
        # Load project configuration
        if not os.path.exists(self.project_config_path):
            raise FileNotFoundError(f"Project configuration not found: {self.project_config_path}")
            
        with open(self.project_config_path, 'r', encoding='utf-8') as f:
            self.project_data = json.load(f)
            
        self.project_name = self.project_data.get("project_name", "Unnamed Project")
        self.project_initials = self.project_data.get("project_initials", "UP")
        
    def add_feature(self, feature_data: Dict[str, Any]) -> str:
        """
        Adds a new feature to the ledger and returns its unique feature ID.

        Args:
            feature_data (dict): A dictionary containing the feature data with fields:
                - type: Feature type ('new_feature', 'bug_fix', 'refactor', 'enhancement')
                - title: Short descriptive title
                - description: Detailed description (optional)
                - keywords: List of keywords (optional)
                - relations: List of relation dicts with 'type' and 'target_id' (optional)

        Returns:
            str: The unique feature ID assigned to the new feature.
            
        Raises:
            sqlite3.Error: If database operation fails.
        """
        with get_connection(self.db_path) as conn:
            try:
                # Get next feature number
                cursor = conn.execute("""
                    SELECT feature_id FROM features 
                    WHERE feature_id LIKE ? 
                    ORDER BY CAST(SUBSTR(feature_id, LENGTH(?) + 2) AS INTEGER) DESC 
                    LIMIT 1
                """, (f"{self.project_initials}-%", self.project_initials))
                
                last_feature = cursor.fetchone()
                if last_feature:
                    last_num = int(last_feature[0].split("-")[1])
                    new_feature_num = last_num + 1
                else:
                    new_feature_num = 1
                
                # Create new feature ID
                feature_id = f"{self.project_initials}-{new_feature_num:03d}"
                
                # Insert feature record
                conn.execute("""
                    INSERT INTO features (
                        feature_id, type, status, title, description, keywords, date_created
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    feature_id,
                    feature_data.get("type", "new_feature"),
                    feature_data.get("status", "requested"),
                    feature_data.get("title", ""),
                    feature_data.get("description", ""),
                    json.dumps(feature_data.get("keywords", [])),
                    datetime.now().isoformat()
                ))
                
                # Add relations if provided
                relations = feature_data.get("relations", [])
                for relation in relations:
                    conn.execute("""
                        INSERT INTO feature_relations (feature_id, relation_type, target_id)
                        VALUES (?, ?, ?)
                    """, (feature_id, relation["type"], relation["target_id"]))
                
                conn.commit()
                return feature_id
                
            except sqlite3.Error as e:
                conn.rollback()
                raise sqlite3.Error(f"Failed to add feature: {e}")
    
    def get_feature_by_id(self, feature_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns the full data for a single feature including relations and documents.
        
        Args:
            feature_id (str): The unique feature identifier.
            
        Returns:
            Optional[Dict[str, Any]]: Feature data dict or None if not found.
        """
        with get_connection(self.db_path) as conn:
            # Get main feature data
            cursor = conn.execute("SELECT * FROM features WHERE feature_id = ?", (feature_id,))
            feature_row = cursor.fetchone()
            
            if not feature_row:
                return None
            
            # Convert to dict and parse JSON fields
            feature = dict(feature_row)
            feature["keywords"] = json.loads(feature["keywords"]) if feature["keywords"] else []
            feature["changed_files"] = json.loads(feature["changed_files"]) if feature["changed_files"] else []
            
            # Get relations
            cursor = conn.execute("""
                SELECT relation_type, target_id FROM feature_relations 
                WHERE feature_id = ?
            """, (feature_id,))
            feature["relations"] = [
                {"type": row[0], "target_id": row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Get documents
            cursor = conn.execute("""
                SELECT document_type, content, created_at, updated_at 
                FROM feature_documents 
                WHERE feature_id = ?
                ORDER BY document_type, updated_at DESC
            """, (feature_id,))
            
            documents = {}
            for row in cursor.fetchall():
                doc_type, content, created_at, updated_at = row
                documents[doc_type] = {
                    "content": content,
                    "created_at": created_at,
                    "updated_at": updated_at
                }
            feature["documents"] = documents
            
            return feature
    
    def get_features_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Returns a list of all features matching a status.
        
        Args:
            status (str): The status to filter by.
            
        Returns:
            List[Dict[str, Any]]: List of feature data dictionaries.
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT feature_id, type, status, title, description, date_created 
                FROM features 
                WHERE status = ?
                ORDER BY date_created DESC
            """, (status,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_feature_status(self, feature_id: str, status: str, timestamp_field: Optional[str] = None) -> bool:
        """
        Updates a feature's status and optionally sets a timestamp field.
        
        Args:
            feature_id (str): The feature to update.
            status (str): The new status.
            timestamp_field (Optional[str]): Which date field to update ('date_implemented' or 'date_superseded').
            
        Returns:
            bool: True if update succeeded, False if feature not found.
        """
        with get_connection(self.db_path) as conn:
            if timestamp_field and timestamp_field in ('date_implemented', 'date_superseded'):
                cursor = conn.execute(f"""
                    UPDATE features 
                    SET status = ?, {timestamp_field} = ? 
                    WHERE feature_id = ?
                """, (status, datetime.now().isoformat(), feature_id))
            else:
                cursor = conn.execute("""
                    UPDATE features 
                    SET status = ? 
                    WHERE feature_id = ?
                """, (status, feature_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def mark_feature_implemented(self, feature_id: str, commit_hash: Optional[str] = None, changed_files: Optional[List[str]] = None) -> bool:
        """
        Marks a feature as implemented and records implementation details.
        
        Args:
            feature_id (str): The feature to mark as implemented.
            commit_hash (Optional[str]): Git commit hash where feature was implemented.
            changed_files (Optional[List[str]]): List of files changed in implementation.
            
        Returns:
            bool: True if update succeeded, False if feature not found.
        """
        with get_connection(self.db_path) as conn:
            now = datetime.now().isoformat()
            
            cursor = conn.execute("""
                UPDATE features 
                SET status = 'validated', date_implemented = ?, commit_hash = ?, changed_files = ?
                WHERE feature_id = ?
            """, (
                now, 
                commit_hash, 
                json.dumps(changed_files) if changed_files else None,
                feature_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def mark_feature_superseded(self, feature_id: str) -> bool:
        """
        Marks a feature as superseded by another feature.
        
        Args:
            feature_id (str): The feature to mark as superseded.
            
        Returns:
            bool: True if update succeeded, False if feature not found.
        """
        return self.update_feature_status(feature_id, 'superseded', 'date_superseded')
    
    def add_feature_document(self, feature_id: str, document_type: str, content: str) -> bool:
        """
        Adds or updates a document for a feature.
        
        Args:
            feature_id (str): The feature ID.
            document_type (str): Type of document ('feature_request', 'technical_architecture_specification', 'feature_implementation_plan').
            content (str): The document content.
            
        Returns:
            bool: True if operation succeeded.
        """
        with get_connection(self.db_path) as conn:
            now = datetime.now().isoformat()
            
            # Check if document already exists
            cursor = conn.execute("""
                SELECT id FROM feature_documents 
                WHERE feature_id = ? AND document_type = ?
            """, (feature_id, document_type))
            
            if cursor.fetchone():
                # Update existing document
                conn.execute("""
                    UPDATE feature_documents 
                    SET content = ?, updated_at = ?
                    WHERE feature_id = ? AND document_type = ?
                """, (content, now, feature_id, document_type))
            else:
                # Insert new document
                conn.execute("""
                    INSERT INTO feature_documents (feature_id, document_type, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (feature_id, document_type, content, now, now))
            
            conn.commit()
            return True
    
    def keyword_search(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """
        Performs a keyword search across feature titles, descriptions, and keywords.
        
        Args:
            search_terms (List[str]): List of terms to search for.
            
        Returns:
            List[Dict[str, Any]]: List of matching features with relevance scores.
        """
        if not search_terms:
            return []
        
        with get_connection(self.db_path) as conn:
            # Build search query
            search_conditions = []
            params = []
            
            for term in search_terms:
                term_lower = f"%{term.lower()}%"
                search_conditions.append("""
                    (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(keywords) LIKE ?)
                """)
                params.extend([term_lower, term_lower, term_lower])
            
            query = f"""
                SELECT feature_id, type, status, title, description, date_created,
                       ({' + '.join(['1'] * len(search_terms))}) as relevance_score
                FROM features 
                WHERE {' OR '.join(search_conditions)}
                ORDER BY relevance_score DESC, date_created DESC
            """
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_feature_statistics(self) -> Dict[str, Any]:
        """
        Returns summary statistics about features in the ledger.
        
        Returns:
            Dict[str, Any]: Statistics including counts by status and type.
        """
        with get_connection(self.db_path) as conn:
            stats = {}
            
            # Count by status
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM features 
                GROUP BY status
            """)
            stats["by_status"] = dict(cursor.fetchall())
            
            # Count by type
            cursor = conn.execute("""
                SELECT type, COUNT(*) as count 
                FROM features 
                GROUP BY type
            """)
            stats["by_type"] = dict(cursor.fetchall())
            
            # Total count
            cursor = conn.execute("SELECT COUNT(*) FROM features")
            stats["total_features"] = cursor.fetchone()[0]
            
            return stats