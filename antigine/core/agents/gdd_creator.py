"""
gdd_creator.py
##############

Main GDD Creator Agent using LangGraph for interactive game design document creation.
Integrates with existing Antigine infrastructure for tech stack awareness and file management.
"""

# Imports
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from ..models import lite_model, standard_model, pro_model
from ..prompts import GDD_CREATOR_SYSTEM_PROMPT
from ..gdd_manager import GDDManager
from ...managers.ProjectLedgerManager import ProjectLedgerManager
from .gdd_session import GDDState, GDDSessionManager, SectionStatus
from .gdd_generator import GDDContentGenerator


class GDDCreatorAgent:
    """
    Interactive GDD creation agent with LangGraph state management.
    Supports both coach and assembler interaction styles with tech stack awareness.
    """
    
    def __init__(self, project_root: str, style: str = "coach", model_tier: str = "standard"):
        """
        Initialize the GDD Creator Agent.
        
        Args:
            project_root (str): Path to the project root directory
            style (str): Interaction style - "coach" or "assembler"
            model_tier (str): Model complexity - "lite", "standard", or "pro"
        """
        self.project_root = Path(project_root)
        self.style = style
        self.model_tier = model_tier
        
        # Initialize core components
        self.gdd_manager = GDDManager(project_root)
        self.project_manager = ProjectLedgerManager(project_root)
        self.session_manager = GDDSessionManager()
        
        # Get tech stack context
        self.tech_stack, self.language = self._get_tech_stack_info()
        
        # Initialize content generator
        self.content_generator = GDDContentGenerator(self.tech_stack, self.language)
        
        # Initialize LangChain components
        self.model = self._get_model(model_tier)
        self.system_prompt = GDD_CREATOR_SYSTEM_PROMPT(self.tech_stack, self.language, style)
        
        # Session persistence
        self.session_folder = self.project_root / ".antigine" / "gdd_sessions"
        self.session_folder.mkdir(parents=True, exist_ok=True)
        self.current_session_file = self.session_folder / "current_session.json"
        
        # Initialize LangGraph
        self.graph = self._create_langgraph()
        
        # Memory checkpointer for conversation persistence (can be upgraded to SQLite later)
        self.checkpointer = MemorySaver()
    
    def _get_tech_stack_info(self) -> Tuple[str, str]:
        """Get tech stack and language from project configuration."""
        try:
            config = self.project_manager.get_project_config()
            tech_stack = config.get('tech_stack', 'Unknown')
            language = config.get('language', 'Unknown')
            return tech_stack, language
        except Exception:
            return "Unknown", "Unknown"
    
    def _get_model(self, model_tier: str):
        """Get the appropriate model based on tier."""
        models = {
            "lite": lite_model,
            "standard": standard_model,
            "pro": pro_model
        }
        return models.get(model_tier, standard_model)
    
    def _create_langgraph(self) -> StateGraph:
        """Create the LangGraph workflow for GDD creation."""
        workflow = StateGraph(GDDState)
        
        # Define nodes
        workflow.add_node("start_session", self._start_session_node)
        workflow.add_node("process_input", self._process_input_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("update_state", self._update_state_node)
        workflow.add_node("check_completion", self._check_completion_node)
        workflow.add_node("finalize_gdd", self._finalize_gdd_node)
        
        # Define edges
        workflow.set_entry_point("start_session")
        workflow.add_edge("start_session", "generate_response")
        workflow.add_edge("process_input", "generate_response")
        workflow.add_edge("generate_response", "update_state")
        workflow.add_edge("update_state", "check_completion")
        
        # Conditional edges from check_completion
        workflow.add_conditional_edges(
            "check_completion",
            self._should_continue,
            {
                "continue": "process_input",
                "finalize": "finalize_gdd",
                "end": END
            }
        )
        
        workflow.add_edge("finalize_gdd", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _start_session_node(self, state: GDDState) -> GDDState:
        """Initialize or resume a GDD creation session."""
        # If this is a new session, start the first section
        if state["current_section"] == 1 and not state["sections"]["1"]["started_at"]:
            state = self.session_manager.start_current_section(state)
        
        state["awaiting_user_input"] = True
        return state
    
    def _process_input_node(self, state: GDDState) -> GDDState:
        """Process user input and prepare for response generation."""
        # This node receives user input from the CLI/interface
        # The input should be in state["current_user_input"]
        return state
    
    def _generate_response_node(self, state: GDDState) -> GDDState:
        """Generate agent response using the LLM."""
        try:
            # Create chat prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{user_input}")
            ])
            
            # Get current section context
            current_section = self.session_manager.get_current_section_data(state)
            progress = self.session_manager.get_progress_summary(state)
            
            # Prepare context
            context = {
                "user_input": state.get("current_user_input", ""),
                "current_section": current_section["name"],
                "section_number": current_section["number"],
                "progress": f"{progress['completed_sections']}/{progress['total_sections']} sections complete",
                "tech_stack": self.tech_stack,
                "language": self.language
            }
            
            # If there's previous conversation in this section, include it
            if current_section["user_responses"]:
                context["previous_responses"] = current_section["user_responses"][-3:]  # Last 3 for context
            
            # Generate response
            chain = prompt_template | self.model
            
            # Format the full input including context
            full_input = self._format_input_with_context(state.get("current_user_input", ""), context)
            
            response = chain.invoke({"user_input": full_input})
            
            # Extract response content
            if hasattr(response, 'content'):
                agent_response = response.content
            else:
                agent_response = str(response)
            
            state["current_agent_response"] = agent_response
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            state["current_agent_response"] = error_msg
            state["last_error"] = error_msg
            state["retry_count"] = state.get("retry_count", 0) + 1
        
        return state
    
    def _update_state_node(self, state: GDDState) -> GDDState:
        """Update session state with the conversation turn."""
        user_input = state.get("current_user_input", "")
        agent_response = state.get("current_agent_response", "")
        
        if user_input and agent_response:
            # Add conversation turn
            state = self.session_manager.add_conversation_turn(state, user_input, agent_response)
            
            # Save session state to file
            self._save_session_state(state)
        
        return state
    
    def _check_completion_node(self, state: GDDState) -> GDDState:
        """Check if current section or entire GDD is complete."""
        # This is where we would analyze the conversation to determine
        # if the current section has enough information to be considered complete
        
        # For now, we'll rely on explicit completion commands from the user
        # In a full implementation, this could use NLP to detect completion
        
        current_section = self.session_manager.get_current_section_data(state)
        
        # Check if user indicated section completion
        user_input = state.get("current_user_input", "").lower()
        completion_indicators = ["done", "complete", "finished", "next section", "move on"]
        
        if any(indicator in user_input for indicator in completion_indicators):
            # Extract content from conversation and mark section complete
            content = self._extract_section_content(state, state["current_section"])
            state = self.session_manager.complete_current_section(state, content)
            
            # Try to advance to next section
            state = self.session_manager.advance_section(state)
        
        return state
    
    def _finalize_gdd_node(self, state: GDDState) -> GDDState:
        """Generate and save the final GDD document."""
        try:
            # Generate the complete GDD document
            gdd_content = self.content_generator.generate_gdd_document(state)
            
            # Save to file using GDDManager
            success, message = self.gdd_manager.create_gdd(gdd_content, backup_existing=True)
            
            if success:
                state["current_agent_response"] = f"🎉 GDD creation complete! {message}"
            else:
                state["current_agent_response"] = f"❌ Failed to save GDD: {message}"
                state["last_error"] = message
            
        except Exception as e:
            error_msg = f"Error finalizing GDD: {str(e)}"
            state["current_agent_response"] = error_msg
            state["last_error"] = error_msg
        
        return state
    
    def _should_continue(self, state: GDDState) -> Literal["continue", "finalize", "end"]:
        """Determine the next action based on state."""
        if state.get("last_error"):
            return "end"  # Stop if there's an error
        
        if state["is_completed"]:
            return "finalize"
        
        # Check if we should continue with more input
        if state.get("awaiting_user_input", True):
            return "continue"
        
        return "end"
    
    def _format_input_with_context(self, user_input: str, context: Dict[str, Any]) -> str:
        """Format user input with additional context for the model."""
        context_parts = [
            f"Current Section: {context['current_section']} (#{context['section_number']})",
            f"Progress: {context['progress']}",
            f"Tech Stack: {context['tech_stack']} / {context['language']}"
        ]
        
        if context.get("previous_responses"):
            context_parts.append(f"Previous responses: {'; '.join(context['previous_responses'][-2:])}")
        
        context_str = " | ".join(context_parts)
        return f"[Context: {context_str}]\n\nUser: {user_input}"
    
    def _extract_section_content(self, state: GDDState, section_num: int) -> Dict[str, Any]:
        """Extract structured content from section conversation."""
        section_data = state["sections"][str(section_num)]
        
        # For now, return a simple structure with the user responses
        # In a full implementation, this could use NLP to extract structured data
        return {
            "responses": section_data["user_responses"],
            "extracted_at": datetime.now().isoformat(),
            "section_name": section_data["name"]
        }
    
    def _save_session_state(self, state: GDDState) -> None:
        """Save current session state to file."""
        try:
            self.session_manager.save_state_to_file(state, self.current_session_file)
        except Exception as e:
            print(f"Warning: Failed to save session state: {e}")
    
    def _load_session_state(self) -> Optional[GDDState]:
        """Load existing session state from file."""
        try:
            success, state, message = self.session_manager.load_state_from_file(self.current_session_file)
            if success:
                return state
        except Exception:
            pass
        return None
    
    # Public Interface Methods
    
    async def start_new_session(self) -> Tuple[bool, str, Optional[GDDState]]:
        """
        Start a new GDD creation session.
        
        Returns:
            Tuple[bool, str, Optional[GDDState]]: (success, message, initial_state)
        """
        try:
            # Create initial state
            initial_state = self.session_manager.create_initial_state(
                self.tech_stack, self.language, self.style
            )
            
            # Run through the graph to get initial response
            config = {"configurable": {"thread_id": initial_state["session_id"]}}
            result = await self.graph.ainvoke(initial_state, config)
            
            return True, "New GDD session started successfully", result
            
        except Exception as e:
            return False, f"Failed to start session: {str(e)}", None
    
    async def resume_session(self) -> Tuple[bool, str, Optional[GDDState]]:
        """
        Resume an existing GDD creation session.
        
        Returns:
            Tuple[bool, str, Optional[GDDState]]: (success, message, current_state)
        """
        try:
            # Load existing state
            state = self._load_session_state()
            if not state:
                return False, "No existing session found", None
            
            # Validate state integrity
            issues = self.session_manager.validate_state_integrity(state)
            if issues:
                return False, f"Session integrity issues: {'; '.join(issues)}", None
            
            return True, "Session resumed successfully", state
            
        except Exception as e:
            return False, f"Failed to resume session: {str(e)}", None
    
    async def process_user_input(self, user_input: str, current_state: GDDState) -> Tuple[bool, str, GDDState]:
        """
        Process user input and return updated state with agent response.
        
        Args:
            user_input (str): The user's input
            current_state (GDDState): The current session state
            
        Returns:
            Tuple[bool, str, GDDState]: (success, agent_response, updated_state)
        """
        try:
            # Update state with user input
            current_state["current_user_input"] = user_input
            current_state["awaiting_user_input"] = False
            
            # Process through the graph
            config = {"configurable": {"thread_id": current_state["session_id"]}}
            result = await self.graph.ainvoke(current_state, config)
            
            agent_response = result.get("current_agent_response", "No response generated")
            
            return True, agent_response, result
            
        except Exception as e:
            error_msg = f"Error processing input: {str(e)}"
            current_state["last_error"] = error_msg
            return False, error_msg, current_state
    
    def get_session_status(self, state: GDDState) -> Dict[str, Any]:
        """Get detailed session status information."""
        return {
            "progress": self.session_manager.get_progress_summary(state),
            "sections": self.session_manager.get_section_status_list(state),
            "validation_issues": self.session_manager.validate_state_integrity(state),
            "content_completeness": self.content_generator.validate_content_completeness(state)
        }
    
    def generate_progress_report(self, state: GDDState) -> str:
        """Generate a markdown progress report."""
        return self.content_generator.generate_progress_summary_markdown(state)
    
    def export_gdd_preview(self, state: GDDState) -> str:
        """Generate a preview of the current GDD document."""
        return self.content_generator.generate_gdd_document(state)
    
    def cleanup_session(self) -> Tuple[bool, str]:
        """Clean up current session files."""
        try:
            if self.current_session_file.exists():
                # Archive the session instead of deleting
                archive_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                archive_path = self.session_folder / "archives" / archive_name
                archive_path.parent.mkdir(exist_ok=True)
                
                self.current_session_file.rename(archive_path)
                return True, f"Session archived to {archive_path}"
            else:
                return True, "No session to clean up"
                
        except Exception as e:
            return False, f"Failed to cleanup session: {str(e)}"