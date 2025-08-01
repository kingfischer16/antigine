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
from typing import Dict, Any, List, Optional, Tuple, TypedDict, Union
from dataclasses import dataclass
from enum import Enum

from ..models import lite_model
from ..gdd_manager import GDDManager
from ...managers.ProjectLedgerManager import ProjectLedgerManager


class SectionStatus(Enum):
    """Status of each GDD section."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    NEEDS_REVISION = "needs_revision"


class SectionDefinition(TypedDict):
    """TypedDict for section definition structure."""

    name: str
    description: str
    criteria: List[str]


class StructuredContent(TypedDict, total=False):
    """TypedDict for structured section content."""

    raw_content: str
    user_responses: List[str]
    structured_at: str
    error: str  # Optional, only present when there's an error


class SectionInfo(TypedDict):
    """TypedDict for section information."""

    section_number: int
    name: str
    description: str
    criteria: List[str]
    status: str
    questions_asked_count: int
    responses_given_count: int


class SectionPreview(TypedDict):
    """TypedDict for section preview information."""

    section_number: int
    name: str
    description: str


class SessionStatus(TypedDict):
    """TypedDict for session status information."""

    session_id: str
    current_section: int
    completed_sections: int
    total_sections: int
    completion_percentage: float
    tech_stack: str
    language: str
    is_completed: bool


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
    structured_content: StructuredContent
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
    SECTIONS_DEFINITION: Dict[int, SectionDefinition] = {
        1: {
            "name": "Core Vision",
            "description": "Elevator pitch and design pillars that prevent scope creep",
            "criteria": [
                "Clear one-sentence game description",
                "Target audience definition",
                "Core emotional experience",
                "2-3 core design pillars that guide decisions",
            ],
        },
        2: {
            "name": "MDA Breakdown",
            "description": "Mechanics, Dynamics, and Aesthetics with ruthless focus",
            "criteria": [
                "Primary mechanics (1-2 core mechanics maximum)",
                "Intended dynamics (player behaviors)",
                "Target aesthetics (emotional responses)",
                "How they connect to create the experience",
            ],
        },
        3: {
            "name": "Core Gameplay Loop",
            "description": "Minute-to-minute player experience definition",
            "criteria": [
                "Step-by-step player actions in a typical session",
                "Loop duration and pacing",
                "Progression hooks and rewards",
                "How the loop stays engaging over time",
            ],
        },
        4: {
            "name": "MVP Feature Set",
            "description": "Absolute minimum scope with ruthless prioritization",
            "criteria": [
                "Maximum 3-5 essential features that deliver core experience",
                "Features explicitly cut from MVP",
                "Success metrics for MVP validation",
                "Estimated development time/scope",
            ],
        },
        5: {
            "name": "Vertical Slice Definition",
            "description": "Concrete demo scope for immediate development focus",
            "criteria": [
                "Specific playable scenario/level",
                "Exact features to implement",
                "Assets and content needed",
                "Success criteria for the slice",
            ],
        },
        6: {
            "name": "Visual Style & Assets",
            "description": "Art direction focused on achievable execution",
            "criteria": [
                "Visual style description and references",
                "Asset requirements and creation plan",
                "Technical art constraints",
                "Placeholder vs final art strategy",
            ],
        },
        7: {
            "name": "Technical Overview",
            "description": "High-level technical decisions without implementation details",
            "criteria": [
                "Architecture approach for the tech stack",
                "Key technical challenges and solutions",
                "Performance targets and constraints",
                "Third-party tools and libraries needed",
            ],
        },
        8: {
            "name": "Development Roadmap",
            "description": "Realistic timeline with frequent validation points",
            "criteria": [
                "Major milestones and deliverables (every 2-4 weeks maximum)",
                "Risk assessment and mitigation",
                "Resource requirements",
                "Regular check-in and pivot points",
            ],
        },
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

    def _extract_response_content(self, response: Any) -> str:
        """
        Safely extract string content from LLM response.

        Args:
            response: LLM response object

        Returns:
            str: The response content as a string
        """
        if hasattr(response, "content"):
            content = response.content
            return str(content) if content is not None else ""
        return str(response)

    def _get_project_context(self) -> Tuple[str, str]:
        """Get tech stack and language from project configuration."""
        try:
            # Access project_data directly from ProjectLedgerManager
            config = self.project_manager.project_data
            tech_stack = config.get("tech_stack", "Unknown")
            language = config.get("project_language", "Unknown")
            return tech_stack, language
        except (AttributeError, TypeError, KeyError):
            # Expected errors when project_data is malformed or missing
            return "Unknown", "Unknown"
        except Exception as e:
            # Log unexpected errors for debugging
            print(f"Warning: Unexpected error reading project context: {e}")
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
                    structured_content={},
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
                game_context={},
            )

            # Save session
            self._save_session()

            return True, f"New GDD session created: {session_id}"

        except (OSError, PermissionError) as e:
            return False, f"File system error creating session: {str(e)}"
        except (TypeError, ValueError) as e:
            return False, f"Data error creating session: {str(e)}"
        except Exception as e:
            print(f"Warning: Unexpected error creating session: {e}")
            return False, "Unexpected error creating session"

    def load_existing_session(self) -> Tuple[bool, str]:
        """
        Load existing session from file.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.current_session_file.exists():
                return False, "No existing session found"

            with open(self.current_session_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate required keys exist
            required_keys = ["session_id", "tech_stack", "language", "sections", "game_context"]
            if not all(key in data for key in required_keys):
                return False, "Invalid session file format - missing required fields"

            # Reconstruct session object
            sections = {}
            for num_str, section_data in data["sections"].items():
                sections[int(num_str)] = SectionData(
                    number=section_data["number"],
                    name=section_data["name"],
                    description=section_data["description"],
                    criteria=section_data["criteria"],
                    status=SectionStatus(section_data["status"]),
                    questions_asked=section_data["questions_asked"],
                    user_responses=section_data["user_responses"],
                    structured_content=section_data["structured_content"],
                    started_at=section_data.get("started_at"),
                    completed_at=section_data.get("completed_at"),
                )

            self.current_session = GDDSession(
                session_id=data["session_id"],
                tech_stack=data["tech_stack"],
                language=data["language"],
                created_at=data["created_at"],
                last_updated=data["last_updated"],
                current_section=data["current_section"],
                sections=sections,
                game_context=data["game_context"],
                is_completed=data["is_completed"],
                completion_time=data.get("completion_time"),
            )

            return True, f"Session loaded: {self.current_session.session_id}"

        except json.JSONDecodeError as e:
            return False, f"Corrupted session file: {str(e)}"
        except (KeyError, ValueError, TypeError) as e:
            return False, f"Invalid session data format: {str(e)}"
        except (OSError, PermissionError) as e:
            return False, f"File system error: {str(e)}"
        except Exception as e:
            print(f"Warning: Unexpected error loading session: {e}")
            return False, "Unexpected error loading session"

    def _save_session(self) -> None:
        """Save current session to file."""
        if not self.current_session:
            return

        try:
            # Convert to JSON-serializable format
            data: Dict[str, Any] = {
                "session_id": self.current_session.session_id,
                "tech_stack": self.current_session.tech_stack,
                "language": self.current_session.language,
                "created_at": self.current_session.created_at,
                "last_updated": self.current_session.last_updated,
                "current_section": self.current_session.current_section,
                "game_context": self.current_session.game_context,
                "is_completed": self.current_session.is_completed,
                "completion_time": self.current_session.completion_time,
                "sections": {},
            }

            # Convert sections
            for num, section in self.current_session.sections.items():
                data["sections"][str(num)] = {
                    "number": section.number,
                    "name": section.name,
                    "description": section.description,
                    "criteria": section.criteria,
                    "status": section.status.value,
                    "questions_asked": section.questions_asked,
                    "user_responses": section.user_responses,
                    "structured_content": section.structured_content,
                    "started_at": section.started_at,
                    "completed_at": section.completed_at,
                }

            with open(self.current_session_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.current_session.last_updated = datetime.now().isoformat()

        except (OSError, PermissionError) as e:
            print(f"Warning: File system error saving session: {e}")
        except (TypeError, ValueError) as e:
            print(f"Warning: Data serialization error: {e}")
        except Exception as e:
            print(f"Warning: Unexpected error saving session: {e}")

    # === Atomic LLM Operations ===

    def _generate_questions(self, section_num: int, context: str = "") -> List[str]:
        """
        Use Flash Lite to generate contextual questions for a section.

        Args:
            section_num (int): Section number
            context (str): Complete context from previous sections

        Returns:
            List[str]: Generated questions
        """
        section_def = self.SECTIONS_DEFINITION[section_num]

        prompt = f"""You are helping create a Game Design Document for a {self.tech_stack}/{self.language} game.

CURRENT SECTION: {section_def['name']}
DESCRIPTION: {section_def['description']}

CRITERIA TO COVER:
{chr(10).join(f"- {criterion}" for criterion in section_def['criteria'])}

COMPLETE GAME CONTEXT SO FAR:
{context if context else "This is the first section - no previous context available."}

Your job is to generate 2-3 contextual, conversational questions that:

1. REFERENCE what has already been established in previous sections (show you understand the game)
2. Ask for the missing information needed to complete this section
3. Feel like a natural conversation with someone who knows the game concept
4. Are specific to indie solo development

If the context already provides substantial information for some criteria, acknowledge that and focus
questions on what's still needed.

Example style: "Based on your [reference to previous context], I'm thinking your [current section topic]
might involve [suggestion based on context]. Does this sound right, or would you like to take a different approach?"

Format as a simple numbered list:
1. [contextual question]
2. [contextual question]
3. [contextual question if needed]"""

        try:
            response = self.llm.invoke(prompt)
            content = self._extract_response_content(response)

            # Parse questions from response
            questions = []
            for line in content.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Remove number/bullet and clean up
                    if line.startswith("-"):
                        question = line[1:].strip()
                    elif "." in line and line[0].isdigit():
                        question = line.split(".", 1)[1].strip()
                    else:
                        question = line.strip()

                    if question and not question.startswith("[") and not question.startswith("Format"):
                        questions.append(question)

            fallback = f"What are the key aspects of {section_def['name'].lower()} for your game?"
            return questions[:3] if questions else [fallback]

        except (ConnectionError, TimeoutError, ValueError) as e:
            print(f"Warning: LLM error in question generation: {e}")
            return [f"What are the key aspects of {section_def['name'].lower()} for your game?"]
        except Exception as e:
            print(f"Warning: Unexpected error in question generation: {e}")
            return [f"What are the key aspects of {section_def['name'].lower()} for your game?"]

    def _can_generate_preview(self, section_num: int, context: str) -> bool:
        """
        Determine if we have enough context to generate a preview instead of asking questions.

        Args:
            section_num (int): Section number
            context (str): Complete context from previous sections

        Returns:
            bool: True if preview generation is appropriate
        """
        # Only generate previews for sections 3+ where we have substantial context
        if section_num < 3:
            return False

        # Must have meaningful context (not just tech stack info)
        if not context or len(context.strip()) < 200:
            return False

        # Check if context contains completed sections
        return "SECTION 1:" in context and "SECTION 2:" in context

    def _generate_section_preview(self, section_num: int, context: str) -> Tuple[str, List[str]]:
        """
        Generate a preview of what the section should contain based on context.

        Args:
            section_num (int): Section number
            context (str): Complete context from previous sections

        Returns:
            Tuple[str, List[str]]: (preview_content, follow_up_questions)
        """
        section_def = self.SECTIONS_DEFINITION[section_num]
        criteria_list = chr(10).join(f"- {criterion}" for criterion in section_def["criteria"])

        preview_prompt = f"""You are helping create a Game Design Document for a {self.tech_stack}/{self.language} game.

CURRENT SECTION: {section_def['name']}
DESCRIPTION: {section_def['description']}

CRITERIA TO COVER:
{criteria_list}

COMPLETE GAME CONTEXT:
{context}

Based on the rich context from previous sections, generate a thoughtful preview of what this section
should contain. Be specific and reference the established game elements.

Your preview should:
1. Draw logical conclusions from the previous sections
2. Address all the required criteria
3. Feel conversational and show understanding of their game
4. Be detailed enough to be useful, but leave room for the user to modify

After the preview, ask 1-2 follow-up questions to confirm or refine specific aspects.

Format your response as:
PREVIEW:
[Detailed preview content organized by criteria]

FOLLOW-UP QUESTIONS:
1. [Question to confirm or refine the preview]
2. [Optional second question]"""

        try:
            response = self.llm.invoke(preview_prompt)
            content = self._extract_response_content(response)

            # Parse preview and questions
            parts = content.split("FOLLOW-UP QUESTIONS:")
            preview_content = parts[0].replace("PREVIEW:", "").strip()

            questions = []
            if len(parts) > 1:
                question_text = parts[1].strip()
                for line in question_text.split("\n"):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith("-")):
                        if line.startswith("-"):
                            question = line[1:].strip()
                        elif "." in line and line[0].isdigit():
                            question = line.split(".", 1)[1].strip()
                        else:
                            question = line.strip()

                        if question and not question.startswith("["):
                            questions.append(question)

            # Fallback questions if none were generated
            if not questions:
                questions = [
                    f"Does this capture your vision for {section_def['name'].lower()}?",
                    "What would you like to adjust or add?",
                ]

            return preview_content, questions[:2]

        except Exception as e:
            print(f"Warning: Preview generation failed: {e}")
            # Fallback to regular question generation
            return "", self._generate_questions(section_num, context)

    def _evaluate_response_completeness(
        self, section_num: int, user_response: str, previous_responses: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Evaluate if section is complete by checking user responses against criteria with full context.

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

        # Get complete context from previous sections
        full_context = self._build_context_summary()

        criteria_list = chr(10).join(f"- {criterion}" for criterion in section_def["criteria"])

        evaluation_prompt = f"""You are helping evaluate if a GDD section is complete.

CURRENT SECTION: {section_def['name']}
REQUIRED CRITERIA:
{criteria_list}

COMPLETE GAME CONTEXT (from previous sections):
{full_context}

USER RESPONSES FOR THIS SECTION:
{combined_response}

Your job is to determine if the section is complete by checking if ALL criteria are satisfied, considering both:
1. The complete game context from previous sections
2. The user's responses for this section

Some criteria might already be partially or fully addressed in previous sections. Be intelligent about this.

For each criterion, extract relevant information or mark as "MISSING" if not adequately covered.

Respond in EXACTLY this format:
CRITERION 1: [extracted content from context+responses or MISSING]
CRITERION 2: [extracted content from context+responses or MISSING]
CRITERION 3: [extracted content from context+responses or MISSING]
CRITERION 4: [extracted content from context+responses or MISSING]

Be thorough - check both the previous context AND current responses for each criterion."""

        try:
            evaluation_response = self.llm.invoke(evaluation_prompt)
            evaluation_content = self._extract_response_content(evaluation_response)

            # Parse evaluation results
            extracted_criteria = {}
            missing_criteria = []

            criterion_lines = [
                line.strip() for line in evaluation_content.split("\n") if line.strip().startswith("CRITERION")
            ]

            for i, line in enumerate(criterion_lines, 1):
                if i <= len(section_def["criteria"]):
                    if "MISSING" in line.upper():
                        missing_criteria.append(section_def["criteria"][i - 1])
                    else:
                        # Extract the content after the colon
                        content_part = line.split(":", 1)[1].strip() if ":" in line else ""
                        if content_part and content_part.upper() != "MISSING":
                            extracted_criteria[section_def["criteria"][i - 1]] = content_part

            # Determine if section is complete
            if len(missing_criteria) == 0:
                return True, "✅ Section completed! All criteria covered based on context and responses."

            # Generate feedback showing what was understood and what's missing
            feedback_parts = []

            if extracted_criteria:
                feedback_parts.append("📝 Here's what I understand so far (from context + your responses):")
                for criterion, content in extracted_criteria.items():
                    feedback_parts.append(f"• **{criterion}**: {content}")
                feedback_parts.append("")

            if missing_criteria:
                feedback_parts.append("❓ I still need information about:")
                for criterion in missing_criteria:
                    feedback_parts.append(f"• {criterion}")

            return False, "\n".join(feedback_parts)

        except (ConnectionError, TimeoutError, ValueError) as e:
            print(f"Warning: LLM error in response evaluation: {e}")
            criteria_str = ", ".join(section_def["criteria"])
            return False, f"Unable to process response. Please provide more details about: {criteria_str}"
        except Exception as e:
            print(f"Warning: Unexpected error in response evaluation: {e}")
            criteria_str = ", ".join(section_def["criteria"])
            return False, f"Unable to process response. Please provide more details about: {criteria_str}"

    def _extract_missing_criteria_from_feedback(self, feedback: str, all_criteria: List[str]) -> List[str]:
        """
        Extract missing criteria from feedback message.

        Args:
            feedback (str): The feedback message containing missing criteria
            all_criteria (List[str]): All criteria for the section

        Returns:
            List[str]: List of missing criteria
        """
        missing_criteria = []

        # Look for criteria mentioned in the "I still need information about:" section
        lines = feedback.split("\n")
        in_missing_section = False

        for line in lines:
            line = line.strip()
            if "I still need information about:" in line:
                in_missing_section = True
                continue
            elif in_missing_section and line.startswith("•"):
                # Extract the criterion from the bullet point
                criterion_text = line[1:].strip()  # Remove bullet point
                # Match against actual criteria
                for criterion in all_criteria:
                    if criterion.lower() in criterion_text.lower() or criterion_text.lower() in criterion.lower():
                        missing_criteria.append(criterion)
                        break

        # Fallback: if no specific criteria found, return all criteria
        if not missing_criteria:
            missing_criteria = all_criteria

        return missing_criteria

    def _generate_targeted_questions(self, section_num: int, context: str, missing_criteria: List[str]) -> List[str]:
        """
        Generate targeted questions for specific missing criteria.

        Args:
            section_num (int): Section number
            context (str): Context from previous sections
            missing_criteria (List[str]): Specific criteria that need information

        Returns:
            List[str]: List of targeted questions
        """
        section_def = self.SECTIONS_DEFINITION[section_num]
        missing_list = chr(10).join(f"- {criterion}" for criterion in missing_criteria)
        context_str = context if context else "This is the first section - no previous context available."

        prompt = f"""You are helping create a Game Design Document for a {self.tech_stack}/{self.language} game.

SECTION: {section_def['name']}
DESCRIPTION: {section_def['description']}

MISSING CRITERIA (focus on these):
{missing_list}

GAME CONTEXT SO FAR:
{context_str}

Generate 1-2 specific, focused questions that will help gather the MISSING information above.
Make the questions:
1. Specific to the missing criteria only
2. Appropriate for indie game development
3. Focused on getting concrete, useful answers
4. Acknowledge what the user has already provided

Format as a simple numbered list:
1. [question]
2. [question]"""

        try:
            response = self.llm.invoke(prompt)
            content = self._extract_response_content(response)

            # Parse questions from response
            questions = []
            for line in content.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Remove numbering and add to questions
                    if line.startswith("-"):
                        # Handle bullet format: "- question text"
                        question = line[1:].strip()
                    elif "." in line and line[0].isdigit():
                        # Handle numbered format: "1. question text"
                        question = line.split(".", 1)[1].strip()
                    else:
                        # Fallback: use the whole line
                        question = line.strip()

                    if question and not question.startswith("[") and not question.startswith("Format"):
                        questions.append(question)

            criteria_str = ", ".join(missing_criteria)
            fallback_question = f"Can you provide more details about: {criteria_str}?"
            return questions[:2] if questions else [fallback_question]

        except (ConnectionError, TimeoutError, ValueError) as e:
            # Expected LLM-related errors
            print(f"Warning: LLM error in targeted question generation: {e}")
            criteria_str = ", ".join(missing_criteria)
            return [f"Can you provide more details about: {criteria_str}?"]
        except Exception as e:
            # Unexpected errors - log for debugging
            print(f"Warning: Unexpected error in targeted question generation: {e}")
            criteria_str = ", ".join(missing_criteria)
            return [f"Can you provide more details about: {criteria_str}?"]

    def _structure_section_content(self, section_num: int, user_responses: List[str]) -> StructuredContent:
        """
        Use Flash Lite to structure user responses into organized section content with full context.

        Args:
            section_num (int): Section number
            user_responses (List[str]): All user responses for the section

        Returns:
            StructuredContent: Structured content with standardized fields
        """
        section_def = self.SECTIONS_DEFINITION[section_num]
        combined_responses = "\n\n".join(user_responses)

        # Get complete context for proper structuring
        full_context = self._build_context_summary()

        prompt = f"""Structure the following user responses into organized content for a Game Design Document section.

CURRENT SECTION: {section_def['name']}

COMPLETE GAME CONTEXT (for reference - use actual game title, mechanics, etc.):
{full_context}

USER RESPONSES FOR THIS SECTION:
{combined_responses}

Structure the user responses into clean, professional GDD content. Make sure to:
1. Use the actual game title and details from the context (not placeholders like [Game Title])
2. Reference specific mechanics, pillars, and elements established in previous sections
3. Create appropriate subsections and bullet points
4. Make it sound cohesive with the overall game design
5. Remove redundancy but preserve all important details

The output should feel like part of a unified GDD document, not a standalone section."""

        try:
            response = self.llm.invoke(prompt)
            content = self._extract_response_content(response)

            return {
                "raw_content": content,
                "user_responses": user_responses,
                "structured_at": datetime.now().isoformat(),
            }

        except (ConnectionError, TimeoutError) as e:
            print(f"Warning: LLM connection error in content structuring: {e}")
            return {
                "raw_content": combined_responses,
                "user_responses": user_responses,
                "error": f"LLM connection error: {str(e)}",
                "structured_at": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Warning: Unexpected error in content structuring: {e}")
            return {
                "raw_content": combined_responses,
                "user_responses": user_responses,
                "error": f"Unexpected error: {str(e)}",
                "structured_at": datetime.now().isoformat(),
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

            # Check if we can generate a preview instead of questions
            if self._can_generate_preview(section_num, context):
                # Generate preview-based approach
                preview_content, questions = self._generate_section_preview(section_num, context)
                section.questions_asked.extend(questions)

                # Save session
                self._save_session()

                # Format the response with preview
                section_def = self.SECTIONS_DEFINITION[section_num]
                message_parts = [
                    f"📋 Started section {section_num}: {section.name}",
                    "",
                    "Based on your game concept so far, here's what I think this section should cover:",
                    "",
                    f"**{section_def['name']}**",
                    preview_content,
                    "",
                    "💭 Does this look right? The questions below will help us refine it:",
                ]
                message = "\n".join(message_parts)

                return True, message, questions
            else:
                # Generate regular questions
                questions = self._generate_questions(section_num, context)
                section.questions_asked.extend(questions)

                # Save session
                self._save_session()

                return True, f"Started section {section_num}: {section.name}", questions

        except (AttributeError, KeyError) as e:
            return False, f"Session data error: {str(e)}", []
        except Exception as e:
            print(f"Warning: Unexpected error starting section: {e}")
            return False, "Unexpected error starting section", []

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

        # Handle section review commands if section is pending review
        if section.status == SectionStatus.PENDING_REVIEW:
            return self._handle_section_review(user_response.strip().lower(), current_section_num)

        try:
            # Add user response
            section.user_responses.append(user_response)

            # Evaluate if section is complete
            is_complete, reason = self._evaluate_response_completeness(
                current_section_num, user_response, section.user_responses[:-1]
            )

            if is_complete:
                # Section is complete, structure the content and put it in review
                structured_content = self._structure_section_content(current_section_num, section.user_responses)

                section.structured_content = structured_content
                section.status = SectionStatus.PENDING_REVIEW

                # Save session
                self._save_session()

                # Return structured content for review
                section_def = self.SECTIONS_DEFINITION[current_section_num]
                review_message = (
                    f"📋 Great! I've organized your input for Section {current_section_num}: "
                    f"{section_def['name']}\n\n"
                )
                review_message += f"**{section_def['name']}**\n"
                review_message += structured_content.get("raw_content", "")
                review_message += "\n\n💭 Does this capture what you intended? You can:\n"
                review_message += "• Type 'approve' to finalize this section and continue\n"
                review_message += "• Type 'revise' to make changes\n"
                review_message += "• Add any additional thoughts or corrections"

                return True, review_message, None
            else:
                # Need more information, generate targeted follow-up questions
                context = self._build_context_summary()

                # Extract missing criteria from the reason/feedback
                section_def = self.SECTIONS_DEFINITION[current_section_num]
                missing_criteria = self._extract_missing_criteria_from_feedback(reason, section_def["criteria"])

                follow_up_questions = self._generate_targeted_questions(current_section_num, context, missing_criteria)
                section.questions_asked.extend(follow_up_questions)

                # Save session
                self._save_session()

                return True, f"📝 {reason}", follow_up_questions

        except (AttributeError, KeyError) as e:
            return False, f"Session data error: {str(e)}", None
        except Exception as e:
            print(f"Warning: Unexpected error processing response: {e}")
            return False, "Unexpected error processing response", None

    def _handle_section_review(self, user_input: str, section_num: int) -> Tuple[bool, str, Optional[List[str]]]:
        """
        Handle user input during section review phase.

        Args:
            user_input (str): User's input (lowercased and stripped)
            section_num (int): Current section number

        Returns:
            Tuple[bool, str, Optional[List[str]]]: (success, feedback, next_questions_or_none)
        """
        if not self.current_session:
            return False, "No active session", None

        try:
            if user_input in ["approve", "approved", "yes", "y", "looks good", "continue"]:
                return self._approve_section(section_num)
            elif user_input in ["revise", "revision", "change", "edit", "no", "n"]:
                return self._request_section_revision(section_num)
            else:
                # User provided additional input - add it and re-evaluate
                return self._handle_section_addition(user_input, section_num)

        except (AttributeError, KeyError) as e:
            return False, f"Session data error: {str(e)}", None
        except Exception as e:
            print(f"Warning: Unexpected error handling section review: {e}")
            return False, "Unexpected error handling section review", None

    def _approve_section(self, section_num: int) -> Tuple[bool, str, Optional[List[str]]]:
        """
        Approve the current section and move to next phase.

        Args:
            section_num (int): Section number to approve

        Returns:
            Tuple[bool, str, Optional[List[str]]]: (success, feedback, next_questions_or_none)
        """
        if not self.current_session:
            return False, "No active session", None

        section = self.current_session.sections[section_num]

        # Mark section as completed
        section.status = SectionStatus.COMPLETED
        section.completed_at = datetime.now().isoformat()

        # Update game context with key insights
        self._update_game_context(section_num, section.structured_content)

        # Save session
        self._save_session()

        # Check if all sections are complete
        if self._all_sections_completed():
            self.current_session.is_completed = True
            self.current_session.completion_time = datetime.now().isoformat()
            self._save_session()
            return True, f"✅ Section {section_num} approved! GDD creation is now complete.", None
        else:
            return True, f"✅ Section {section_num} approved and saved!", None

    def _request_section_revision(self, section_num: int) -> Tuple[bool, str, Optional[List[str]]]:
        """
        Handle user request to revise the section.

        Args:
            section_num (int): Section number to revise

        Returns:
            Tuple[bool, str, Optional[List[str]]]: (success, feedback, next_questions_or_none)
        """
        if not self.current_session:
            return False, "No active session", None

        section = self.current_session.sections[section_num]

        # Reset section to in progress
        section.status = SectionStatus.IN_PROGRESS
        section.structured_content = {}

        # Save session
        self._save_session()

        # Ask what they'd like to change
        revision_message = f"📝 Let's revise Section {section_num}. What would you like to change or add?\n\n"
        revision_message += "You can:\n"
        revision_message += "• Tell me what specific aspects need adjustment\n"
        revision_message += "• Provide additional information\n"
        revision_message += "• Completely rewrite any part"

        return True, revision_message, None

    def _handle_section_addition(self, user_input: str, section_num: int) -> Tuple[bool, str, Optional[List[str]]]:
        """
        Handle additional user input during review phase.

        Args:
            user_input (str): User's additional input
            section_num (int): Current section number

        Returns:
            Tuple[bool, str, Optional[List[str]]]: (success, feedback, next_questions_or_none)
        """
        if not self.current_session:
            return False, "No active session", None

        section = self.current_session.sections[section_num]

        # Add the new input to responses
        section.user_responses.append(user_input)

        # Reset to in progress and re-structure
        section.status = SectionStatus.IN_PROGRESS

        # Re-evaluate with all responses including the new one
        is_complete, reason = self._evaluate_response_completeness(section_num, user_input, section.user_responses[:-1])

        if is_complete:
            # Re-structure content with the additional input
            structured_content = self._structure_section_content(section_num, section.user_responses)
            section.structured_content = structured_content
            section.status = SectionStatus.PENDING_REVIEW

            # Save session
            self._save_session()

            # Return updated content for review
            section_def = self.SECTIONS_DEFINITION[section_num]
            review_message = (
                f"📋 I've updated Section {section_num}: {section_def['name']} " f"with your additional input:\n\n"
            )
            review_message += f"**{section_def['name']}**\n"
            review_message += structured_content.get("raw_content", "")
            review_message += "\n\n💭 Does this look better? You can:\n"
            review_message += "• Type 'approve' to finalize this section\n"
            review_message += "• Type 'revise' to make more changes\n"
            review_message += "• Add more thoughts or corrections"

            return True, review_message, None
        else:
            # Still need more information
            context = self._build_context_summary()
            section_def = self.SECTIONS_DEFINITION[section_num]
            missing_criteria = self._extract_missing_criteria_from_feedback(reason, section_def["criteria"])
            follow_up_questions = self._generate_targeted_questions(section_num, context, missing_criteria)
            section.questions_asked.extend(follow_up_questions)

            # Save session
            self._save_session()

            return True, f"📝 Thanks for the additional input! {reason}", follow_up_questions

    def _build_context_summary(self) -> str:
        """Build complete context from all completed sections and user responses."""
        if not self.current_session:
            return ""

        context_parts = []

        # Add tech stack context
        context_parts.append(f"GAME PROJECT: {self.tech_stack}/{self.language} game")
        context_parts.append("")

        # Add all completed section content
        for num in range(1, self.current_session.current_section):
            section = self.current_session.sections.get(num)
            if section and section.status == SectionStatus.COMPLETED:
                context_parts.append(f"=== SECTION {num}: {section.name.upper()} ===")

                # Include structured content if available
                if section.structured_content and "raw_content" in section.structured_content:
                    context_parts.append(section.structured_content["raw_content"])
                else:
                    # Fallback to user responses if no structured content
                    context_parts.append("User responses:")
                    for response in section.user_responses:
                        context_parts.append(f"- {response}")

                context_parts.append("")

        # If no completed sections yet, just provide tech stack info
        if not context_parts or all(not part.strip() for part in context_parts):
            context_parts = [f"This is a {self.tech_stack}/{self.language} game project. No sections completed yet."]

        return "\n".join(context_parts)

    def _update_game_context(self, section_num: int, structured_content: StructuredContent) -> None:
        """Update persistent game context with key information from completed section."""
        if not self.current_session:
            return

        # Simple approach: store the complete structured content
        if "raw_content" in structured_content:
            section_name = self.SECTIONS_DEFINITION[section_num]["name"]
            key = f"section_{section_num}_{section_name}"
            self.current_session.game_context[key] = structured_content["raw_content"]

    def _all_sections_completed(self) -> bool:
        """Check if all sections are completed."""
        if not self.current_session:
            return False

        return all(section.status == SectionStatus.COMPLETED for section in self.current_session.sections.values())

    def get_current_section_info(self) -> Union[SectionInfo, Dict[str, str]]:
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
            "responses_given_count": len(section.user_responses),
        }

    def get_next_section_preview(self) -> Optional[SectionPreview]:
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
            "description": section_def["description"],
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

        except (AttributeError, KeyError) as e:
            return False, f"Session data error: {str(e)}"
        except Exception as e:
            print(f"Warning: Unexpected error generating final GDD: {e}")
            return False, "Unexpected error generating final GDD"

    def get_session_status(self) -> Union[SessionStatus, Dict[str, str]]:
        """Get current session status information."""
        if not self.current_session:
            return {"error": "No active session"}

        completed_sections = sum(
            1 for s in self.current_session.sections.values() if s.status == SectionStatus.COMPLETED
        )

        return {
            "session_id": self.current_session.session_id,
            "current_section": self.current_session.current_section,
            "completed_sections": completed_sections,
            "total_sections": len(self.SECTIONS_DEFINITION),
            "completion_percentage": (completed_sections / len(self.SECTIONS_DEFINITION)) * 100,
            "tech_stack": self.current_session.tech_stack,
            "language": self.current_session.language,
            "is_completed": self.current_session.is_completed,
        }
