"""
gdd_session.py
##############

LangGraph-compatible state management for GDD creation workflow.
Uses TypedDict state pattern following LangGraph best practices.
"""

# Imports
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, TypedDict, Annotated
from typing_extensions import NotRequired
from enum import Enum
from langgraph.graph import add_messages


class SectionStatus(Enum):
    """Enumeration for section completion status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class GDDSectionData(TypedDict):
    """TypedDict for individual GDD section data."""
    number: int
    name: str
    description: str
    status: str  # SectionStatus.value
    content: Dict[str, Any]
    started_at: NotRequired[Optional[str]]  # ISO format datetime
    completed_at: NotRequired[Optional[str]]  # ISO format datetime
    user_responses: List[str]
    agent_prompts: List[str]


class GDDState(TypedDict):
    """
    LangGraph state for GDD creation workflow.
    This is the canonical state that flows through the LangGraph nodes.
    """
    # Core session info
    session_id: str
    tech_stack: str
    language: str
    style: str  # "coach" or "assembler"
    
    # Progress tracking
    current_section: int
    is_completed: bool
    completion_time: NotRequired[Optional[str]]  # ISO format datetime
    
    # Session metadata
    created_at: str  # ISO format datetime
    last_updated: str  # ISO format datetime
    user_preferences: Dict[str, Any]
    
    # Section data
    sections: Dict[str, GDDSectionData]  # str keys for JSON serialization
    
    # LangGraph message handling
    messages: Annotated[List[Dict[str, Any]], add_messages]
    
    # Current interaction context
    current_user_input: NotRequired[str]
    current_agent_response: NotRequired[str]
    awaiting_user_input: bool
    
    # Error handling
    last_error: NotRequired[Optional[str]]
    retry_count: NotRequired[int]


class GDDSessionManager:
    """
    Manages GDD session state operations and persistence.
    Provides utilities for working with LangGraph GDDState.
    """
    
    # Define the 8 GDD sections
    SECTIONS = [
        (1, "Core Vision", "Elevator pitch and design pillars that prevent scope creep"),
        (2, "MDA Breakdown", "Mechanics, Dynamics, and Aesthetics with ruthless focus"),
        (3, "Core Gameplay Loop", "Minute-to-minute player experience definition"),
        (4, "MVP Feature Set", "Absolute minimum scope with ruthless prioritization"),
        (5, "Vertical Slice Definition", "Concrete demo scope for immediate development focus"),
        (6, "Visual Style & Assets", "Art direction focused on achievable execution"),
        (7, "Technical Overview", "High-level technical decisions without implementation details"),
        (8, "Development Roadmap", "Realistic timeline with frequent validation points")
    ]
    
    @classmethod
    def create_initial_state(cls, tech_stack: str, language: str, style: str = "coach") -> GDDState:
        """
        Create initial GDD state for a new session.
        
        Args:
            tech_stack (str): The game development tech stack being used
            language (str): The programming language being used
            style (str): The interaction style ("coach" or "assembler")
            
        Returns:
            GDDState: Initial state for LangGraph workflow
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        now = datetime.now().isoformat()
        
        # Initialize all sections
        sections = {}
        for number, name, description in cls.SECTIONS:
            sections[str(number)] = GDDSectionData(
                number=number,
                name=name,
                description=description,
                status=SectionStatus.PENDING.value,
                content={},
                user_responses=[],
                agent_prompts=[]
            )
        
        return GDDState(
            session_id=session_id,
            tech_stack=tech_stack,
            language=language,
            style=style,
            current_section=1,
            is_completed=False,
            created_at=now,
            last_updated=now,
            user_preferences={},
            sections=sections,
            messages=[],
            awaiting_user_input=True
        )
    
    @classmethod
    def get_current_section_data(cls, state: GDDState) -> GDDSectionData:
        """Get the current active section data from state."""
        return state["sections"][str(state["current_section"])]
    
    @classmethod
    def start_current_section(cls, state: GDDState) -> GDDState:
        """Start the current section if not already started."""
        current_section = cls.get_current_section_data(state)
        
        if current_section["status"] == SectionStatus.PENDING.value:
            current_section["status"] = SectionStatus.IN_PROGRESS.value
            current_section["started_at"] = datetime.now().isoformat()
            state["last_updated"] = datetime.now().isoformat()
        
        return state
    
    @classmethod
    def complete_current_section(cls, state: GDDState, content: Dict[str, Any]) -> GDDState:
        """
        Mark current section as completed with extracted content.
        
        Args:
            state (GDDState): Current state
            content (Dict[str, Any]): The structured content extracted from the conversation
            
        Returns:
            GDDState: Updated state
        """
        current_section = cls.get_current_section_data(state)
        
        if current_section["status"] == SectionStatus.IN_PROGRESS.value:
            current_section["status"] = SectionStatus.COMPLETED.value
            current_section["content"] = content
            current_section["completed_at"] = datetime.now().isoformat()
            state["last_updated"] = datetime.now().isoformat()
        
        return state
    
    @classmethod
    def advance_section(cls, state: GDDState) -> GDDState:
        """
        Move to the next section if current section is completed.
        
        Args:
            state (GDDState): Current state
            
        Returns:
            GDDState: Updated state
        """
        current_section = cls.get_current_section_data(state)
        
        if current_section["status"] != SectionStatus.COMPLETED.value:
            return state
        
        if state["current_section"] >= 8:
            state["is_completed"] = True
            state["completion_time"] = datetime.now().isoformat()
            return state
        
        # Advance to next section
        state["current_section"] += 1
        state["last_updated"] = datetime.now().isoformat()
        
        # Start the new section
        return cls.start_current_section(state)
    
    @classmethod
    def add_conversation_turn(cls, state: GDDState, user_input: str, agent_response: str) -> GDDState:
        """
        Add a conversation turn to the current section and message history.
        
        Args:
            state (GDDState): Current state
            user_input (str): The user's input
            agent_response (str): The agent's response
            
        Returns:
            GDDState: Updated state
        """
        # Add to current section
        current_section = cls.get_current_section_data(state)
        current_section["user_responses"].append(user_input)
        current_section["agent_prompts"].append(agent_response)
        
        # Add to LangGraph messages
        state["messages"].extend([
            {"role": "user", "content": user_input, "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": agent_response, "timestamp": datetime.now().isoformat()}
        ])
        
        # Update interaction context
        state["current_user_input"] = user_input
        state["current_agent_response"] = agent_response
        state["last_updated"] = datetime.now().isoformat()
        
        return state
    
    @classmethod
    def get_progress_summary(cls, state: GDDState) -> Dict[str, Any]:
        """
        Get a human-readable progress summary from state.
        
        Args:
            state (GDDState): Current state
            
        Returns:
            Dict[str, Any]: Progress information
        """
        completed_sections = sum(
            1 for s in state["sections"].values() 
            if s["status"] == SectionStatus.COMPLETED.value
        )
        in_progress_sections = sum(
            1 for s in state["sections"].values() 
            if s["status"] == SectionStatus.IN_PROGRESS.value
        )
        
        current_section = cls.get_current_section_data(state)
        
        created_at = datetime.fromisoformat(state["created_at"])
        last_updated = datetime.fromisoformat(state["last_updated"])
        
        return {
            "session_id": state["session_id"],
            "current_section": state["current_section"],
            "current_section_name": current_section["name"],
            "completed_sections": completed_sections,
            "total_sections": len(cls.SECTIONS),
            "completion_percentage": (completed_sections / len(cls.SECTIONS)) * 100,
            "in_progress_sections": in_progress_sections,
            "is_completed": state["is_completed"],
            "tech_stack": state["tech_stack"],
            "language": state["language"],
            "style": state["style"],
            "created_at": state["created_at"],
            "last_updated": state["last_updated"],
            "session_duration_minutes": (last_updated - created_at).total_seconds() / 60,
            "message_count": len(state["messages"])
        }
    
    @classmethod
    def get_section_status_list(cls, state: GDDState) -> List[Dict[str, Any]]:
        """Get detailed status for all sections from state."""
        return [
            {
                "number": section["number"],
                "name": section["name"],
                "status": section["status"],
                "started": section.get("started_at"),
                "completed": section.get("completed_at"),
                "interaction_count": len(section["user_responses"])
            }
            for section in state["sections"].values()
        ]
    
    @classmethod
    def save_state_to_file(cls, state: GDDState, file_path: Path) -> Tuple[bool, str]:
        """
        Save GDD state to JSON file.
        
        Args:
            state (GDDState): State to save
            file_path (Path): Path where to save the session file
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(dict(state), f, indent=2, ensure_ascii=False)
            
            return True, f"State saved to {file_path}"
            
        except Exception as e:
            return False, f"Failed to save state: {str(e)}"
    
    @classmethod
    def load_state_from_file(cls, file_path: Path) -> Tuple[bool, Optional[GDDState], str]:
        """
        Load GDD state from JSON file.
        
        Args:
            file_path (Path): Path to the session file
            
        Returns:
            Tuple[bool, Optional[GDDState], str]: (success, state_object, message)
        """
        try:
            if not file_path.exists():
                return False, None, f"State file not found: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required fields
            required_fields = ["session_id", "tech_stack", "language", "style", "current_section", 
                             "is_completed", "created_at", "last_updated", "sections", "messages"]
            
            for field in required_fields:
                if field not in data:
                    return False, None, f"Invalid state file: missing field '{field}'"
            
            # Create GDDState (TypedDict doesn't need explicit construction)
            state = GDDState(data)
            
            return True, state, f"State loaded successfully from {file_path}"
            
        except Exception as e:
            return False, None, f"Failed to load state: {str(e)}"
    
    @classmethod
    def validate_state_integrity(cls, state: GDDState) -> List[str]:
        """
        Validate state data integrity and return any issues found.
        
        Args:
            state (GDDState): State to validate
            
        Returns:
            List[str]: List of validation issues (empty if valid)
        """
        issues = []
        
        # Check section completeness
        if state["current_section"] > 8:
            issues.append("Current section number exceeds maximum (8)")
        
        if state["current_section"] < 1:
            issues.append("Current section number is invalid (< 1)")
        
        # Check section sequence integrity
        for i in range(1, state["current_section"]):
            section = state["sections"].get(str(i))
            if not section or section["status"] != SectionStatus.COMPLETED.value:
                issues.append(f"Section {i} should be completed but isn't")
        
        # Check message consistency
        section_interactions = sum(len(s["user_responses"]) for s in state["sections"].values())
        user_messages = sum(1 for msg in state["messages"] if msg.get("role") == "user")
        
        if user_messages != section_interactions:
            issues.append("Message history count doesn't match section interactions")
        
        return issues