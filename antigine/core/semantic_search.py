"""
semantic_search.py
##################

This module provides semantic search capabilities for feature requests, technical architectures,
and implementation plans. Uses ChromaDB for vector storage and similarity search operations.

ChromaDB handles embedding generation, storage, and similarity search out-of-the-box,
eliminating the need for custom similarity calculations and database vector storage.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Literal

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .database import get_connection

# Type definitions for document types
DocumentType = Literal['feature_request', 'technical_architecture', 'implementation_plan']


class SemanticSearchEngine:
    """
    Semantic search engine using ChromaDB for vector operations.
    
    Leverages ChromaDB's built-in similarity search and embedding capabilities
    for efficient semantic search across feature documents.
    """
    
    def __init__(self, project_root: str, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic search engine with ChromaDB.
        
        Args:
            project_root (str): Path to the project root (for ChromaDB storage)
            model_name (str): Sentence transformer model name
        """
        self.project_root = project_root
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB client
        chroma_path = os.path.join(project_root, ".antigine", "chroma_db")
        os.makedirs(chroma_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection with embedding function
        self.collection = self.client.get_or_create_collection(
            name="feature_documents",
            embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_name
            )
        )
        
    def store_feature_document(
        self, 
        feature_id: str, 
        document_type: DocumentType, 
        text: str,
        feature_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store feature document text in ChromaDB with automatic embedding.
        
        Args:
            feature_id (str): Feature ID
            document_type (DocumentType): Type of document
            text (str): Text content to embed and store
            feature_metadata (dict, optional): Additional feature metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not text or not text.strip():
            self.logger.warning(f"Empty text for {feature_id} ({document_type})")
            return False
            
        try:
            # Create document ID combining feature_id and document_type
            doc_id = f"{feature_id}_{document_type}"
            
            # Prepare metadata
            metadata = {
                "feature_id": feature_id,
                "document_type": document_type,
                "model_name": self.model_name
            }
            
            if feature_metadata:
                metadata.update(feature_metadata)
            
            # Store in ChromaDB (handles embedding automatically)
            self.collection.upsert(
                ids=[doc_id],
                documents=[text.strip()],
                metadatas=[metadata]
            )
            
            self.logger.info(f"Stored document for {feature_id} ({document_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store document for {feature_id}: {e}")
            return False
    
    def find_similar_features(
        self, 
        text: str, 
        document_type: Optional[DocumentType] = None,
        similarity_threshold: float = 0.7,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find features with similar content using ChromaDB's built-in search.
        
        Args:
            text (str): Text to search for similar content
            document_type (DocumentType, optional): Filter by document type
            similarity_threshold (float): Minimum similarity score (0.0 to 1.0)
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of similar features with metadata and similarity scores
        """
        if not text or not text.strip():
            self.logger.warning("Empty search text provided")
            return []
            
        try:
            # Build query filters
            where_filter = {}
            if document_type:
                where_filter["document_type"] = document_type
                
            # Query ChromaDB for similar documents
            results = self.collection.query(
                query_texts=[text.strip()],
                n_results=max_results * 2,  # Get extra results to filter by threshold
                where=where_filter if where_filter else None
            )
            
            if not results['ids'] or not results['ids'][0]:
                self.logger.info("No similar documents found")
                return []
            
            # Process results and filter by similarity threshold
            similar_features = []
            for i, doc_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                # Convert distance to similarity (ChromaDB returns distances, lower = more similar)
                similarity_score = max(0.0, 1.0 - distance)
                
                if similarity_score >= similarity_threshold:
                    metadata = results['metadatas'][0][i]
                    feature_id = metadata.get('feature_id', doc_id.split('_')[0])
                    
                    # Get additional feature info from SQLite
                    feature_info = self._get_feature_info(feature_id)
                    
                    similar_features.append({
                        'feature_id': feature_id,
                        'document_type': metadata.get('document_type', ''),
                        'similarity_score': similarity_score,
                        'title': feature_info.get('title', ''),
                        'description': feature_info.get('description', ''),
                        'type': feature_info.get('type', ''),
                        'status': feature_info.get('status', '')
                    })
            
            # Sort by similarity score (highest first)
            similar_features.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_features[:max_results]
            
        except Exception as e:
            self.logger.error(f"Failed to find similar features: {e}")
            return []
    
    def get_feature_relationships_by_similarity(
        self, 
        feature_id: str, 
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find potential relationships for a feature based on semantic similarity.
        
        Args:
            feature_id (str): Feature ID to find relationships for
            similarity_threshold (float): Minimum similarity for relationship detection
            
        Returns:
            List[Dict[str, Any]]: List of potential relationships with confidence scores
        """
        try:
            # Get feature description for search
            feature_info = self._get_feature_info(feature_id)
            if not feature_info or not feature_info.get('description'):
                self.logger.warning(f"No description found for feature {feature_id}")
                return []
            
            search_text = feature_info['description']
            
            # Find similar features
            similar_features = self.find_similar_features(
                search_text,
                document_type='feature_request',
                similarity_threshold=similarity_threshold,
                max_results=20
            )
            
            # Filter out self and classify relationships
            relationships = []
            for similar in similar_features:
                if similar['feature_id'] == feature_id:
                    continue
                    
                # Classify relationship type
                relationship_type = self._classify_relationship(
                    search_text,
                    similar['description'],
                    similar['similarity_score']
                )
                
                if relationship_type:
                    relationships.append({
                        'related_feature_id': similar['feature_id'],
                        'relationship_type': relationship_type,
                        'confidence_score': similar['similarity_score'],
                        'title': similar['title'],
                        'description': similar['description']
                    })
            
            return relationships
            
        except Exception as e:
            self.logger.error(f"Failed to find relationships for {feature_id}: {e}")
            return []
    
    def _get_feature_info(self, feature_id: str) -> Dict[str, Any]:
        """Get feature information from SQLite database."""
        try:
            db_path = os.path.join(self.project_root, ".antigine", "ledger.db")
            with get_connection(db_path) as conn:
                cursor = conn.execute(
                    "SELECT title, description, type, status FROM features WHERE feature_id = ?",
                    (feature_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        'title': row['title'],
                        'description': row['description'],
                        'type': row['type'],
                        'status': row['status']
                    }
                    
        except Exception as e:
            self.logger.warning(f"Failed to get feature info for {feature_id}: {e}")
            
        return {}
    
    def _classify_relationship(self, text1: str, text2: str, similarity_score: float) -> Optional[str]:
        """
        Classify the type of relationship between two feature descriptions.
        
        Args:
            text1 (str): First feature description
            text2 (str): Second feature description  
            similarity_score (float): Similarity score between the features
            
        Returns:
            Optional[str]: Relationship type or None if no clear relationship
        """
        # Simple heuristic-based classification
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # High similarity suggests potential duplicate
        if similarity_score >= 0.9:
            return 'duplicate'
        
        # Check for enhancement/improvement keywords
        enhancement_keywords = ['improve', 'enhance', 'better', 'optimize', 'refactor']
        if any(keyword in text1_lower for keyword in enhancement_keywords):
            if any(keyword in text2_lower for keyword in enhancement_keywords):
                return 'builds_on'
        
        # Check for fix keywords  
        fix_keywords = ['fix', 'bug', 'error', 'issue', 'problem']
        if any(keyword in text1_lower for keyword in fix_keywords):
            return 'fixes'
        
        # Default for high similarity
        if similarity_score >= 0.8:
            return 'builds_on'
            
        return None