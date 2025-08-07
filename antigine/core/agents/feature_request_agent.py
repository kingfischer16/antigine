"""
feature_request_agent.py
#########################

This module provides the Feature Request Agent using LangGraph workflow for validating
and completing feature descriptions. The agent ensures feature requests contain sufficient
information for the architecture phase and integrates with semantic search for duplicate detection.

The workflow handles multi-stage validation, semantic search, relationship classification,
and human approval gates using LangGraph orchestration.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple, TypedDict
from dataclasses import dataclass

from langgraph.graph import StateGraph, END

from ..models import LLMManager
from ..semantic_search import SemanticSearchEngine
from ..database import get_connection


class FeatureRequestState(TypedDict):
    """State for the feature request workflow."""
    # User input
    title: str
    description: str
    feature_type: str
    
    # Validation results
    is_valid: bool
    validation_issues: List[str]
    validation_suggestions: List[str]
    confidence_score: float
    
    # Semantic search results
    similar_features: List[Dict[str, Any]]
    potential_relationships: List[Dict[str, Any]]
    
    # User decisions
    user_approved: bool
    relationship_confirmations: Dict[str, str]  # feature_id -> relationship_type
    
    # Final results
    feature_id: Optional[str]
    stored_successfully: bool
    
    # Workflow control
    current_stage: str
    retry_count: int
    max_retries: int
    error_message: Optional[str]
    
    # Context
    project_root: str
    db_path: str
    gdd_context: str


@dataclass
class ValidationResult:
    """Result of feature request validation."""
    is_complete: bool
    confidence_score: float
    issues: List[str]
    suggestions: List[str]
    missing_elements: List[str]


class FeatureRequestAgent:
    """
    LangGraph-based agent for feature request validation and creation workflow.
    
    Orchestrates the complete feature request lifecycle from user input through
    validation, semantic search, relationship detection, and database storage
    with human approval gates at critical decision points.
    """
    
    def __init__(self, project_root: str, db_path: str):
        """
        Initialize the Feature Request Agent.
        
        Args:
            project_root (str): Path to the project root directory
            db_path (str): Path to the SQLite database (kept for compatibility, ChromaDB uses project_root)
        """
        self.project_root = project_root
        self.db_path = db_path
        self.llm_manager = LLMManager()
        self.semantic_search = SemanticSearchEngine(project_root)
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> Any:
        """Build the LangGraph workflow for feature request processing."""
        
        workflow = StateGraph(FeatureRequestState)
        
        # Add nodes
        workflow.add_node("validate_request", self._validate_request_node)
        workflow.add_node("search_similar", self._search_similar_node)  
        workflow.add_node("classify_relationships", self._classify_relationships_node)
        workflow.add_node("confirm_with_user", self._confirm_with_user_node)
        workflow.add_node("store_feature", self._store_feature_node)
        workflow.add_node("handle_retry", self._handle_retry_node)
        
        # Set entry point
        workflow.set_entry_point("validate_request")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "validate_request",
            self._should_proceed_after_validation,
            {
                "proceed": "search_similar",
                "retry": "handle_retry", 
                "end": END
            }
        )
        
        workflow.add_edge("search_similar", "classify_relationships")
        
        workflow.add_conditional_edges(
            "classify_relationships", 
            self._should_confirm_relationships,
            {
                "confirm": "confirm_with_user",
                "store": "store_feature"
            }
        )
        
        workflow.add_conditional_edges(
            "confirm_with_user",
            self._process_user_confirmation, 
            {
                "approved": "store_feature",
                "retry": "handle_retry",
                "cancelled": END
            }
        )
        
        workflow.add_edge("store_feature", END)
        
        workflow.add_conditional_edges(
            "handle_retry",
            self._should_retry,
            {
                "retry": "validate_request", 
                "end": END
            }
        )
        
        return workflow.compile()
    
    def process_feature_request(
        self, 
        title: str, 
        description: str, 
        feature_type: str
    ) -> FeatureRequestState:
        """
        Process a complete feature request through the LangGraph workflow.
        
        Args:
            title (str): Feature title
            description (str): Feature description
            feature_type (str): Feature type
            
        Returns:
            FeatureRequestState: Final workflow state with results
        """
        # Initialize state
        initial_state: FeatureRequestState = {
            "title": title,
            "description": description, 
            "feature_type": feature_type,
            "is_valid": False,
            "validation_issues": [],
            "validation_suggestions": [],
            "confidence_score": 0.0,
            "similar_features": [],
            "potential_relationships": [],
            "user_approved": False,
            "relationship_confirmations": {},
            "feature_id": None,
            "stored_successfully": False,
            "current_stage": "validation",
            "retry_count": 0,
            "max_retries": 3,
            "error_message": None,
            "project_root": self.project_root,
            "db_path": self.db_path,
            "gdd_context": self._get_gdd_context()
        }
        
        # Execute workflow
        final_state = self.workflow.invoke(initial_state)
        # Type cast to ensure return type compliance
        return final_state  # type: ignore[no-any-return]
    
    def _validate_request_node(self, state: FeatureRequestState) -> FeatureRequestState:
        """Validate feature request using LLM analysis."""
        try:
            state["current_stage"] = "validation"
            
            # Build validation prompt
            validation_prompt = self._build_validation_prompt(
                state["title"], 
                state["description"], 
                state["feature_type"],
                state["gdd_context"]
            )
            
            # Get LLM validation
            response = self.llm_manager.generate_response(
                prompt=validation_prompt,
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse validation result
            validation_result = self._parse_validation_response(response)
            
            # Update state
            state["is_valid"] = validation_result.is_complete
            state["confidence_score"] = validation_result.confidence_score
            state["validation_issues"] = validation_result.issues
            state["validation_suggestions"] = validation_result.suggestions
            
        except Exception as e:
            state["error_message"] = f"Validation failed: {e}"
            state["is_valid"] = False
            state["confidence_score"] = 0.0
            
        return state
    
    def _search_similar_node(self, state: FeatureRequestState) -> FeatureRequestState:
        """Search for similar features using semantic search."""
        try:
            state["current_stage"] = "semantic_search"
            
            # Search for similar features
            similar_features = self.semantic_search.find_similar_features(
                text=state["description"],
                document_type="feature_request", 
                similarity_threshold=0.7,
                max_results=10
            )
            
            state["similar_features"] = similar_features
            
        except Exception as e:
            state["error_message"] = f"Semantic search failed: {e}"
            state["similar_features"] = []
            
        return state
    
    def _classify_relationships_node(self, state: FeatureRequestState) -> FeatureRequestState:
        """Classify relationships with similar features."""
        try:
            state["current_stage"] = "relationship_classification"
            
            relationships = []
            for similar_feature in state["similar_features"]:
                # Use LLM to classify relationship more accurately than heuristics
                relationship_type = self._classify_relationship_with_llm(
                    state["description"],
                    similar_feature["description"], 
                    similar_feature["similarity_score"]
                )
                
                if relationship_type:
                    relationships.append({
                        "feature_id": similar_feature["feature_id"],
                        "title": similar_feature["title"],
                        "relationship_type": relationship_type,
                        "confidence_score": similar_feature["similarity_score"],
                        "description": similar_feature["description"]
                    })
            
            state["potential_relationships"] = relationships
            
        except Exception as e:
            state["error_message"] = f"Relationship classification failed: {e}"
            state["potential_relationships"] = []
            
        return state
    
    def _confirm_with_user_node(self, state: FeatureRequestState) -> FeatureRequestState:
        """Present findings to user for confirmation (human-in-the-loop)."""
        # This will be called by the CLI to present information to the user
        # The actual user interaction happens in the CLI, this node just sets up the state
        state["current_stage"] = "user_confirmation"
        return state
    
    def _store_feature_node(self, state: FeatureRequestState) -> FeatureRequestState:
        """Store the feature request in the database."""
        try:
            state["current_stage"] = "storage"
            
            # Import here to avoid circular imports
            from ...managers.ProjectLedgerManager import ProjectLedgerManager
            
            # Create feature data
            feature_data = {
                "type": state["feature_type"],
                "title": state["title"],
                "description": state["description"],
                "keywords": []
            }
            
            # Initialize ledger manager and create feature
            ledger_manager = ProjectLedgerManager(state["project_root"])
            feature_id = ledger_manager.add_feature(feature_data)
            
            # Store document embedding for semantic search
            feature_metadata = {
                "title": state["title"],
                "type": state["feature_type"],
                "status": "requested"
            }
            self.semantic_search.store_feature_document(
                feature_id,
                "feature_request", 
                state["description"],
                feature_metadata
            )
            
            # Store confirmed relationships
            if state["relationship_confirmations"]:
                with get_connection(state["db_path"]) as conn:
                    for related_id, relationship_type in state["relationship_confirmations"].items():
                        conn.execute(
                            """
                            INSERT INTO feature_relationships (
                                feature_id, related_feature_id, relationship_type, 
                                confidence_score, created_at
                            ) VALUES (?, ?, ?, ?, datetime('now'))
                            """,
                            (feature_id, related_id, relationship_type, 0.9)
                        )
                    conn.commit()
            
            state["feature_id"] = feature_id
            state["stored_successfully"] = True
            
        except Exception as e:
            state["error_message"] = f"Storage failed: {e}"
            state["stored_successfully"] = False
            
        return state
    
    def _handle_retry_node(self, state: FeatureRequestState) -> FeatureRequestState:
        """Handle retry logic."""
        state["retry_count"] += 1
        state["error_message"] = None  # Clear error for retry
        return state
    
    # Conditional edge functions
    def _should_proceed_after_validation(self, state: FeatureRequestState) -> str:
        """Determine next step after validation."""
        if state["error_message"]:
            if state["retry_count"] < state["max_retries"]:
                return "retry"
            return "end"
            
        if state["is_valid"] and state["confidence_score"] >= 0.7:
            return "proceed"
        elif state["retry_count"] < state["max_retries"]:
            return "retry"
        else:
            return "end"
    
    def _should_confirm_relationships(self, state: FeatureRequestState) -> str:
        """Determine if user confirmation is needed for relationships."""
        if state["potential_relationships"]:
            # Check for high-confidence duplicates or conflicts
            high_confidence_issues = [
                r for r in state["potential_relationships"]
                if r["relationship_type"] in ["duplicate", "conflicts_with"] 
                and r["confidence_score"] >= 0.8
            ]
            if high_confidence_issues:
                return "confirm"
        return "store"
    
    def _process_user_confirmation(self, state: FeatureRequestState) -> str:
        """Process user's confirmation decision."""
        # This logic will be handled by the CLI interaction
        # The CLI will update state["user_approved"] and state["relationship_confirmations"]
        if state.get("user_approved", False):
            return "approved"
        elif state["retry_count"] < state["max_retries"]:
            return "retry"
        else:
            return "cancelled"
    
    def _should_retry(self, state: FeatureRequestState) -> str:
        """Determine if workflow should retry."""
        if state["retry_count"] >= state["max_retries"]:
            return "end"
        return "retry"
    
    # Helper methods
    def _get_gdd_context(self) -> str:
        """Extract relevant GDD context if available."""
        try:
            gdd_path = os.path.join(self.project_root, "docs", "gdd.md")
            if os.path.exists(gdd_path):
                with open(gdd_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content[:2000]  # Limit context size
        except Exception:
            pass
        return ""
    
    def _build_validation_prompt(
        self, 
        title: str, 
        description: str, 
        feature_type: str, 
        gdd_context: str
    ) -> str:
        """Build the validation prompt for LLM analysis."""
        prompt_parts = [
            "You are a senior game developer reviewing a feature request for completeness.",
            "Your task is to determine if the feature request contains enough information",
            "to proceed to technical architecture design.",
            "",
            f"FEATURE TYPE: {feature_type}",
            f"FEATURE TITLE: {title}",
            f"FEATURE DESCRIPTION:",
            description,
            ""
        ]
        
        if gdd_context:
            prompt_parts.extend([
                "GAME DESIGN DOCUMENT CONTEXT:",
                gdd_context,
                ""
            ])
            
        prompt_parts.extend([
            "Analyze this feature request and respond in JSON format with:",
            "{",
            '  "is_complete": boolean,',
            '  "confidence_score": float (0.0 to 1.0),',
            '  "issues": [list of specific problems],',
            '  "suggestions": [list of improvement suggestions],',
            '  "missing_elements": [list of missing critical elements]',
            "}",
            "",
            "Consider these aspects:",
            "- Functional requirements clarity",
            "- User interaction patterns (if applicable)", 
            "- Success criteria definition",
            "- Technical constraints mentioned",
            "- Integration points with existing systems",
            "- Testability and validation approach",
            "",
            "Focus on elements needed for technical architecture, not implementation details."
        ])
        
        return "\n".join(prompt_parts)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing markdown formatting."""
        response_clean = response.strip()
        if response_clean.startswith("```json"):
            response_clean = response_clean[7:]
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]
        return response_clean.strip()
    
    def _parse_validation_response(self, response: str) -> ValidationResult:
        """Parse LLM validation response into ValidationResult."""
        try:
            data = json.loads(self._clean_json_response(response))
            
            return ValidationResult(
                is_complete=bool(data.get("is_complete", False)),
                confidence_score=float(data.get("confidence_score", 0.5)),
                issues=list(data.get("issues", [])),
                suggestions=list(data.get("suggestions", [])),
                missing_elements=list(data.get("missing_elements", []))
            )
            
        except Exception:
            # Fallback validation
            return ValidationResult(
                is_complete=False,
                confidence_score=0.3,
                issues=["Failed to parse validation response"],
                suggestions=["Please review feature request manually"],
                missing_elements=["Unknown due to parsing error"]
            )
    
    def _classify_relationship_with_llm(
        self, 
        new_description: str, 
        existing_description: str, 
        similarity_score: float
    ) -> Optional[str]:
        """Use LLM to classify relationship between feature descriptions."""
        try:
            prompt = f"""
            Analyze the relationship between these two game features:
            
            NEW FEATURE:
            {new_description}
            
            EXISTING FEATURE: 
            {existing_description}
            
            Similarity Score: {similarity_score:.2f}
            
            Classify their relationship as one of:
            - "duplicate": Essentially the same feature
            - "supersedes": New feature replaces/improves existing feature
            - "builds_on": New feature extends existing feature  
            - "fixes": New feature fixes issues in existing feature
            - "conflicts_with": Features cannot coexist
            - "none": No significant relationship
            
            Respond with only the relationship type.
            """
            
            response = self.llm_manager.generate_response(
                prompt=prompt,
                temperature=0.1,
                max_tokens=50
            )
            
            relationship = response.strip().lower()
            valid_relationships = ["duplicate", "supersedes", "builds_on", "fixes", "conflicts_with"]
            
            return relationship if relationship in valid_relationships else None
            
        except Exception:
            # Fallback to heuristic classification
            if similarity_score >= 0.9:
                return "duplicate"
            elif similarity_score >= 0.8:
                return "builds_on"
            return None