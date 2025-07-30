"""
gdd_creator.py
##############

Atomic Flash Lite-based GDD Creator Controller.
Uses deterministic Python logic with focused, stateless LLM operations for cost-effective GDD creation.

Philosophy: 
- Python code manages the process and state (The Brain)
- Flash Lite handles atomic text operations (The Scribe)
- Each LLM call is simple, focused, and stateless
- Perfect separation of concerns for reliability and cost efficiency
"""

# Imports
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from ..models import lite_model
from ..gdd_manager import GDDManager
from ...managers.ProjectLedgerManager import ProjectLedgerManager


class SectionStatus(Enum):
    """Status of each GDD section."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    NEEDS_REVISION = "needs_revision"


@dataclass
class SectionData:
    """Structured data for a GDD section."""
    number: int
    name: str
    description: str
    criteria: List[str]  # What needs to be covered
    status: SectionStatus
    questions_asked: List[str]
    user_responses: List[str]
    structured_content: Dict[str, Any]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class GDDSession:
    """Complete GDD creation session state."""
    session_id: str
    tech_stack: str
    language: str
    created_at: str
    last_updated: str
    current_section: int
    sections: Dict[int, SectionData]
    game_context: Dict[str, Any]  # Core game info that persists across sections
    is_completed: bool = False
    completion_time: Optional[str] = None


class GDDController:
    """
    Deterministic GDD creation controller using atomic Flash Lite operations.
    
    This class manages the entire GDD creation process through Python logic,
    using Flash Lite only for focused text generation and evaluation tasks.
    """
    
    # Define the 8 focused GDD sections for indie games
    SECTIONS_DEFINITION = {
        1: {
            "name": "Core Vision",
            "description": "Elevator pitch and design pillars that prevent scope creep",
            "criteria": [
                "Clear one-sentence game description",
                "Target audience definition", 
                "Core emotional experience",
                "3-5 design pillars that guide decisions"
            ]
        },
        2: {
            "name": "MDA Breakdown", 
            "description": "Mechanics, Dynamics, and Aesthetics with ruthless focus",
            "criteria": [
                "Primary mechanics (max 3-5 core mechanics)",
                "Intended dynamics (player behaviors)",
                "Target aesthetics (emotional responses)",
                "How they connect to create the experience"
            ]
        },
        3: {
            "name": "Core Gameplay Loop",
            "description": "Minute-to-minute player experience definition", 
            "criteria": [
                "Step-by-step player actions in a typical session",
                "Loop duration and pacing",
                "Progression hooks and rewards",
                "How the loop stays engaging over time"
            ]
        },
        4: {
            "name": "MVP Feature Set",
            "description": "Absolute minimum scope with ruthless prioritization",
            "criteria": [
                "Must-have features for core experience",
                "Features explicitly cut from MVP",
                "Success metrics for MVP validation",
                "Estimated development time/scope"
            ]
        },
        5: {
            "name": "Vertical Slice Definition", 
            "description": "Concrete demo scope for immediate development focus",
            "criteria": [
                "Specific playable scenario/level",
                "Exact features to implement",
                "Assets and content needed",
                "Success criteria for the slice"
            ]
        },
        6: {
            "name": "Visual Style & Assets",
            "description": "Art direction focused on achievable execution",
            "criteria": [
                "Visual style description and references",
                "Asset requirements and creation plan",
                "Technical art constraints",
                "Placeholder vs final art strategy"
            ]
        },
        7: {
            "name": "Technical Overview",
            "description": "High-level technical decisions without implementation details", 
            "criteria": [
                "Architecture approach for the tech stack",
                "Key technical challenges and solutions",
                "Performance targets and constraints",
                "Third-party tools and libraries needed"
            ]
        },
        8: {
            "name": "Development Roadmap",
            "description": "Realistic timeline with frequent validation points",
            "criteria": [
                "Major milestones and deliverables",
                "Risk assessment and mitigation",
                "Resource requirements",
                "Regular check-in and pivot points"
            ]
        }
    }
    
    def __init__(self, project_root: str):
        """
        Initialize the GDD Controller.
        
        Args:
            project_root (str): Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.gdd_manager = GDDManager(project_root)
        self.project_manager = ProjectLedgerManager(project_root)
        
        # Get project context
        self.tech_stack, self.language = self._get_project_context()
        
        # Initialize Flash Lite model for atomic operations
        self.llm = lite_model
        
        # Session management
        self.session_folder = self.project_root / ".antigine" / "gdd_sessions"
        self.session_folder.mkdir(parents=True, exist_ok=True)
        self.current_session_file = self.session_folder / "current_session.json"
        
        self.current_session: Optional[GDDSession] = None
    
    def _get_project_context(self) -> Tuple[str, str]:
        """Get tech stack and language from project configuration."""
        try:
            # Access project_data directly from ProjectLedgerManager
            config = self.project_manager.project_data
            tech_stack = config.get('tech_stack', 'Unknown')
            language = config.get('project_language', 'Unknown')
            return tech_stack, language
        except Exception:
            return "Unknown", "Unknown"
    
    # === Session Management ===
    
    def create_new_session(self) -> Tuple[bool, str]:
        """
        Create a new GDD creation session.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            now = datetime.now().isoformat()
            
            # Initialize all sections
            sections = {}
            for num, definition in self.SECTIONS_DEFINITION.items():
                sections[num] = SectionData(
                    number=num,
                    name=definition["name"],
                    description=definition["description"],
                    criteria=definition["criteria"],
                    status=SectionStatus.NOT_STARTED,
                    questions_asked=[],
                    user_responses=[],
                    structured_content={}
                )
            
            # Create session
            self.current_session = GDDSession(
                session_id=session_id,
                tech_stack=self.tech_stack,
                language=self.language,
                created_at=now,
                last_updated=now,
                current_section=1,
                sections=sections,
                game_context={}
            )
            
            # Save session
            self._save_session()
            
            return True, f"New GDD session created: {session_id}"
            
        except Exception as e:
            return False, f"Failed to create session: {str(e)}"
    
    def load_existing_session(self) -> Tuple[bool, str]:
        """
        Load existing session from file.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.current_session_file.exists():
                return False, "No existing session found"
            
            with open(self.current_session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct session object
            sections = {}
            for num_str, section_data in data['sections'].items():
                sections[int(num_str)] = SectionData(
                    number=section_data['number'],
                    name=section_data['name'], 
                    description=section_data['description'],
                    criteria=section_data['criteria'],
                    status=SectionStatus(section_data['status']),
                    questions_asked=section_data['questions_asked'],
                    user_responses=section_data['user_responses'],
                    structured_content=section_data['structured_content'],
                    started_at=section_data.get('started_at'),
                    completed_at=section_data.get('completed_at')
                )
            
            self.current_session = GDDSession(
                session_id=data['session_id'],
                tech_stack=data['tech_stack'], 
                language=data['language'],
                created_at=data['created_at'],
                last_updated=data['last_updated'],
                current_section=data['current_section'],
                sections=sections,
                game_context=data['game_context'],
                is_completed=data['is_completed'],
                completion_time=data.get('completion_time')
            )
            
            return True, f"Session loaded: {self.current_session.session_id}"
            
        except Exception as e:
            return False, f"Failed to load session: {str(e)}"
    
    def _save_session(self) -> None:
        """Save current session to file."""
        if not self.current_session:
            return
        
        try:
            # Convert to JSON-serializable format
            data = {
                'session_id': self.current_session.session_id,
                'tech_stack': self.current_session.tech_stack,
                'language': self.current_session.language, 
                'created_at': self.current_session.created_at,
                'last_updated': self.current_session.last_updated,
                'current_section': self.current_session.current_section,
                'game_context': self.current_session.game_context,
                'is_completed': self.current_session.is_completed,
                'completion_time': self.current_session.completion_time,
                'sections': {}
            }
            
            # Convert sections
            for num, section in self.current_session.sections.items():
                data['sections'][str(num)] = {
                    'number': section.number,
                    'name': section.name,
                    'description': section.description, 
                    'criteria': section.criteria,
                    'status': section.status.value,
                    'questions_asked': section.questions_asked,
                    'user_responses': section.user_responses,
                    'structured_content': section.structured_content,
                    'started_at': section.started_at,
                    'completed_at': section.completed_at
                }
            
            with open(self.current_session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.current_session.last_updated = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Warning: Failed to save session: {e}")
    
    # === Atomic LLM Operations ===
    
    def _generate_questions(self, section_num: int, context: str = "") -> List[str]:
        """
        Use Flash Lite to generate focused questions for a section.
        
        Args:
            section_num (int): Section number
            context (str): Additional context if available
            
        Returns:
            List[str]: Generated questions
        """
        section_def = self.SECTIONS_DEFINITION[section_num]
        
        prompt = f"""You are helping create a Game Design Document for a {self.tech_stack}/{self.language} game.

SECTION: {section_def['name']}
DESCRIPTION: {section_def['description']}

CRITERIA TO COVER:
{chr(10).join(f"- {criterion}" for criterion in section_def['criteria'])}

GAME CONTEXT SO FAR:
{context if context else "This is the first section - no previous context available."}

Generate 2-3 specific, focused questions that will help gather the information needed to satisfy all the criteria above. Make the questions:
1. Specific and actionable
2. Appropriate for indie game development
3. Focused on getting concrete, useful answers

Format as a simple numbered list:
1. [question]
2. [question]
3. [question]"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse questions from response
            questions = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove number/bullet and clean up
                    question = line.split('.', 1)[-1].split('-', 1)[-1].strip()
                    if question:
                        questions.append(question)
            
            return questions[:3]  # Limit to 3 questions max
            
        except Exception as e:
            # Fallback questions if LLM fails
            return [f"What are the key aspects of {section_def['name'].lower()} for your game?"]
    
    def _evaluate_response_completeness(self, section_num: int, user_response: str, 
                                      previous_responses: List[str] = None) -> Tuple[bool, str]:
        """
        Use Flash Lite to evaluate if user responses satisfy section criteria.
        
        Args:
            section_num (int): Section number
            user_response (str): User's latest response
            previous_responses (List[str]): Previous responses in this section
            
        Returns:
            Tuple[bool, str]: (is_complete, reason/feedback)
        """
        section_def = self.SECTIONS_DEFINITION[section_num]
        all_responses = (previous_responses or []) + [user_response]
        combined_response = "\n\n".join(all_responses)
        
        prompt = f"""You are evaluating responses for a Game Design Document section.

SECTION: {section_def['name']}
REQUIRED CRITERIA:
{chr(10).join(f"- {criterion}" for criterion in section_def['criteria'])}

USER RESPONSES:
{combined_response}

Evaluate if the user responses adequately cover ALL the required criteria above.

Respond with EXACTLY this format:
COMPLETE: Yes/No
REASON: [Brief explanation of what's covered or what's missing]

Be reasonably lenient - if the user has provided thoughtful responses that address the core intent of each criterion, consider it complete."""

        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            is_complete = False
            reason = "Unable to evaluate response"
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('COMPLETE:'):
                    is_complete = 'yes' in line.lower()
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()
            
            return is_complete, reason
            
        except Exception as e:
            # Conservative fallback
            return False, f"Error evaluating response: {str(e)}"
    
    def _structure_section_content(self, section_num: int, user_responses: List[str]) -> Dict[str, Any]:
        """
        Use Flash Lite to structure user responses into organized section content.
        
        Args:
            section_num (int): Section number
            user_responses (List[str]): All user responses for the section
            
        Returns:
            Dict[str, Any]: Structured content
        """
        section_def = self.SECTIONS_DEFINITION[section_num]
        combined_responses = "\n\n".join(user_responses)
        
        prompt = f"""Structure the following user responses into organized content for a Game Design Document section.

SECTION: {section_def['name']}
USER RESPONSES:
{combined_responses}

Extract and organize the information into a clean, structured format. Create appropriate subsections and bullet points. Make it professional and ready for a GDD document.

Focus on clarity and organization. Remove redundancy but preserve all important details."""

        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "raw_content": content,
                "user_responses": user_responses,
                "structured_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "raw_content": combined_responses,
                "user_responses": user_responses,
                "error": str(e),
                "structured_at": datetime.now().isoformat()
            }
    
    # === Process Control Methods ===
    
    def start_section(self, section_num: int) -> Tuple[bool, str, List[str]]:
        """
        Start working on a specific section.
        
        Args:
            section_num (int): Section number to start
            
        Returns:
            Tuple[bool, str, List[str]]: (success, message, initial_questions)
        """
        if not self.current_session:
            return False, "No active session", []
        
        if section_num < 1 or section_num > len(self.SECTIONS_DEFINITION):
            return False, f"Invalid section number: {section_num}", []
        
        try:
            section = self.current_session.sections[section_num]
            
            if section.status == SectionStatus.COMPLETED:
                return False, f"Section {section_num} is already completed", []
            
            # Mark section as in progress
            section.status = SectionStatus.IN_PROGRESS
            section.started_at = datetime.now().isoformat()
            
            # Update current section
            self.current_session.current_section = section_num
            
            # Build context from previous sections
            context = self._build_context_summary()
            
            # Generate initial questions
            questions = self._generate_questions(section_num, context)
            section.questions_asked.extend(questions)
            
            # Save session
            self._save_session()
            
            return True, f"Started section {section_num}: {section.name}", questions
            
        except Exception as e:
            return False, f"Error starting section: {str(e)}", []
    
    def process_user_response(self, user_response: str) -> Tuple[bool, str, Optional[List[str]]]:
        """
        Process user response for the current section.
        
        Args:
            user_response (str): User's response
            
        Returns:
            Tuple[bool, str, Optional[List[str]]]: (success, feedback, next_questions_or_none)
        """
        if not self.current_session:
            return False, "No active session", None
        
        current_section_num = self.current_session.current_section
        section = self.current_session.sections[current_section_num]
        
        try:
            # Add user response
            section.user_responses.append(user_response)
            
            # Evaluate if section is complete
            is_complete, reason = self._evaluate_response_completeness(
                current_section_num, user_response, section.user_responses[:-1]
            )
            
            if is_complete:
                # Section is complete, structure the content
                structured_content = self._structure_section_content(
                    current_section_num, section.user_responses
                )
                
                section.structured_content = structured_content
                section.status = SectionStatus.COMPLETED
                section.completed_at = datetime.now().isoformat()
                
                # Update game context with key insights
                self._update_game_context(current_section_num, structured_content)
                
                # Save session
                self._save_session()
                
                # Check if all sections are complete
                if self._all_sections_completed():
                    self.current_session.is_completed = True
                    self.current_session.completion_time = datetime.now().isoformat()
                    self._save_session()
                    return True, f"✅ Section {current_section_num} completed! GDD creation is now complete.", None
                else:
                    return True, f"✅ Section {current_section_num} completed! {reason}", None
            else:
                # Need more information, generate follow-up questions
                context = self._build_context_summary()
                follow_up_questions = self._generate_questions(current_section_num, context)
                section.questions_asked.extend(follow_up_questions)
                
                # Save session
                self._save_session()
                
                return True, f"📝 {reason}", follow_up_questions
                
        except Exception as e:
            return False, f"Error processing response: {str(e)}", None
    
    def _build_context_summary(self) -> str:
        """Build a summary of completed sections for context."""
        if not self.current_session:
            return ""
        
        context_parts = []
        
        # Add game context
        if self.current_session.game_context:
            context_parts.append("GAME CONTEXT:")
            for key, value in self.current_session.game_context.items():
                context_parts.append(f"- {key}: {value}")
            context_parts.append("")
        
        # Add completed sections
        completed_sections = []
        for num in range(1, self.current_session.current_section):
            section = self.current_session.sections.get(num)
            if section and section.status == SectionStatus.COMPLETED:
                completed_sections.append(f"Section {num} ({section.name}): Completed")
        
        if completed_sections:
            context_parts.append("COMPLETED SECTIONS:")
            context_parts.extend(completed_sections)
        
        return "\n".join(context_parts)
    
    def _update_game_context(self, section_num: int, structured_content: Dict[str, Any]) -> None:
        """Update persistent game context with key information from completed section."""
        if not self.current_session:
            return
        
        # Extract key information based on section
        if section_num == 1:  # Core Vision
            # Extract core game description and design pillars
            if "raw_content" in structured_content:
                content = structured_content["raw_content"]
                # Store essential game vision info
                self.current_session.game_context["core_vision"] = content[:200] + "..." if len(content) > 200 else content
        
        elif section_num == 2:  # MDA Breakdown  
            if "raw_content" in structured_content:
                content = structured_content["raw_content"]
                self.current_session.game_context["mda_summary"] = content[:200] + "..." if len(content) > 200 else content
        
        # Add other section-specific context extraction as needed
    
    def _all_sections_completed(self) -> bool:
        """Check if all sections are completed."""
        if not self.current_session:
            return False
        
        return all(
            section.status == SectionStatus.COMPLETED 
            for section in self.current_session.sections.values()
        )
    
    def get_current_section_info(self) -> Dict[str, Any]:
        """Get information about the current section."""
        if not self.current_session:
            return {"error": "No active session"}
        
        current_section_num = self.current_session.current_section
        section = self.current_session.sections[current_section_num]
        
        return {
            "section_number": current_section_num,
            "name": section.name,
            "description": section.description,
            "criteria": section.criteria,
            "status": section.status.value,
            "questions_asked_count": len(section.questions_asked),
            "responses_given_count": len(section.user_responses)
        }
    
    def get_next_section_preview(self) -> Optional[Dict[str, Any]]:
        """Get preview of the next section."""
        if not self.current_session:
            return None
        
        next_section_num = self.current_session.current_section + 1
        if next_section_num > len(self.SECTIONS_DEFINITION):
            return None
        
        section_def = self.SECTIONS_DEFINITION[next_section_num]
        return {
            "section_number": next_section_num,
            "name": section_def["name"],
            "description": section_def["description"]
        }
    
    def generate_final_gdd(self) -> Tuple[bool, str]:
        """
        Generate the final GDD document from all completed sections.
        
        Returns:
            Tuple[bool, str]: (success, result_message)
        """
        if not self.current_session or not self.current_session.is_completed:
            return False, "GDD session is not completed yet"
        
        try:
            # Build complete GDD content
            gdd_sections = []
            
            for num in range(1, len(self.SECTIONS_DEFINITION) + 1):
                section = self.current_session.sections[num]
                if section.status == SectionStatus.COMPLETED:
                    gdd_sections.append(f"## {num}. {section.name}")
                    gdd_sections.append("")
                    gdd_sections.append(section.structured_content.get("raw_content", ""))
                    gdd_sections.append("")
            
            # Create complete GDD document
            gdd_content = f"""# Game Design Document
            
**Project:** {self.current_session.tech_stack}/{self.current_session.language} Game
**Created:** {self.current_session.created_at}
**Completed:** {self.current_session.completion_time}

---

{chr(10).join(gdd_sections)}

---

*Generated by Antigine GDD Creator*
"""
            
            # Save using GDD Manager
            success, message = self.gdd_manager.create_gdd(gdd_content, backup_existing=True)
            
            if success:
                return True, f"Final GDD generated successfully: {message}"
            else:
                return False, f"Failed to save GDD: {message}"
                
        except Exception as e:
            return False, f"Error generating final GDD: {str(e)}"
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status information."""
        if not self.current_session:
            return {"error": "No active session"}
        
        completed_sections = sum(1 for s in self.current_session.sections.values() 
                               if s.status == SectionStatus.COMPLETED)
        
        return {
            "session_id": self.current_session.session_id,
            "current_section": self.current_session.current_section,
            "completed_sections": completed_sections,
            "total_sections": len(self.SECTIONS_DEFINITION),
            "completion_percentage": (completed_sections / len(self.SECTIONS_DEFINITION)) * 100,
            "tech_stack": self.current_session.tech_stack,
            "language": self.current_session.language,
            "is_completed": self.current_session.is_completed
        }