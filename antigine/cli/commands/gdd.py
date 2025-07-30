"""
gdd.py
######

CLI commands for GDD (Game Design Document) creation and management.
Integrates with the GDD Creator Agent for interactive document creation.
"""

# Imports
import asyncio
import sys
from pathlib import Path
from typing import Optional

from ...core.agents.gdd_creator import GDDCreatorAgent
from ...core.agents.gdd_session import GDDState
from ..utils.output import print_success, print_error, print_info, print_warning


class GDDCommands:
    """CLI commands for GDD creation and management."""
    
    def __init__(self, project_root: str):
        """Initialize GDD commands for a specific project."""
        self.project_root = project_root
        self.agent: Optional[GDDCreatorAgent] = None
        self.current_state: Optional[GDDState] = None
    
    def _initialize_agent(self, style: str = "coach", model_tier: str = "standard") -> bool:
        """Initialize the GDD Creator Agent."""
        try:
            self.agent = GDDCreatorAgent(self.project_root, style, model_tier)
            return True
        except Exception as e:
            print_error(f"Failed to initialize GDD Creator Agent: {e}")
            return False
    
    async def create_gdd(self, args) -> int:
        """
        Start interactive GDD creation process.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        style = getattr(args, 'style', 'coach')
        model_tier = getattr(args, 'model', 'standard')
        force_new = getattr(args, 'force', False)
        
        print_info(f"🎮 Starting GDD creation with {style} style using {model_tier} model...")
        
        if not self._initialize_agent(style, model_tier):
            return 1
        
        # Check for existing session
        if not force_new:
            success, message, state = await self.agent.resume_session()
            if success and state:
                print_info(f"📄 Resuming existing session: {message}")
                self.current_state = state
                return await self._continue_interactive_session()
        
        # Start new session
        success, message, state = await self.agent.start_new_session()
        if not success:
            print_error(f"Failed to start GDD creation: {message}")
            return 1
        
        print_success(f"✨ {message}")
        self.current_state = state
        
        # Show initial instructions
        self._show_session_instructions()
        
        # Start interactive session
        return await self._continue_interactive_session()
    
    async def resume_gdd(self, args) -> int:
        """
        Resume an existing GDD creation session.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        style = getattr(args, 'style', 'coach')
        model_tier = getattr(args, 'model', 'standard')
        
        if not self._initialize_agent(style, model_tier):
            return 1
        
        success, message, state = await self.agent.resume_session()
        if not success:
            print_error(f"Failed to resume session: {message}")
            return 1
        
        print_success(f"📄 {message}")
        self.current_state = state
        
        # Show current progress
        self._show_progress_summary()
        
        # Continue interactive session
        return await self._continue_interactive_session()
    
    def status_gdd(self, args) -> int:
        """
        Show current GDD creation status.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        style = getattr(args, 'style', 'coach')
        model_tier = getattr(args, 'model', 'standard')
        
        if not self._initialize_agent(style, model_tier):
            return 1
        
        # Try to load existing session
        success, message, state = asyncio.run(self.agent.resume_session())
        if not success:
            print_info("📋 No active GDD creation session found.")
            return 0
        
        print_info("📊 GDD Creation Status:")
        print()
        
        # Show progress summary
        status = self.agent.get_session_status(state)
        progress = status["progress"]
        
        print(f"Session ID: {progress['session_id']}")
        print(f"Tech Stack: {progress['tech_stack']} / {progress['language']}")
        print(f"Style: {progress['style']}")
        print(f"Progress: {progress['completed_sections']}/{progress['total_sections']} sections ({progress['completion_percentage']:.1f}%)")
        print(f"Duration: {progress['session_duration_minutes']:.1f} minutes")
        print()
        
        # Show section details
        print("Section Status:")
        for section in status["sections"]:
            status_emoji = {
                "completed": "✅",
                "in_progress": "🔄",
                "pending": "⏳"
            }.get(section["status"], "❓")
            
            print(f"  {status_emoji} Section {section['number']}: {section['name']} ({section['status']})")
            
            if section['interaction_count'] > 0:
                print(f"      {section['interaction_count']} interactions")
        
        # Show validation issues if any
        if status["validation_issues"]:
            print()
            print_warning("⚠️  Validation Issues:")
            for issue in status["validation_issues"]:
                print(f"  - {issue}")
        
        return 0
    
    def export_gdd(self, args) -> int:
        """
        Export current GDD to a file.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        output_path = getattr(args, 'output', None)
        preview_only = getattr(args, 'preview', False)
        
        if not self._initialize_agent():
            return 1
        
        # Load existing session
        success, message, state = asyncio.run(self.agent.resume_session())
        if not success:
            print_error("No GDD session found to export.")
            return 1
        
        try:
            if preview_only:
                # Show preview in terminal
                preview = self.agent.export_gdd_preview(state)
                print("📄 GDD Preview:")
                print("=" * 50)
                print(preview)
                print("=" * 50)
            else:
                # Export to file
                if not output_path:
                    output_path = Path(self.project_root) / "docs" / "gdd_export.md"
                else:
                    output_path = Path(output_path)
                
                gdd_content = self.agent.export_gdd_preview(state)
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(gdd_content, encoding='utf-8')
                
                print_success(f"📁 GDD exported to: {output_path}")
            
            return 0
            
        except Exception as e:
            print_error(f"Failed to export GDD: {e}")
            return 1
    
    async def _continue_interactive_session(self) -> int:
        """Continue the interactive GDD creation session."""
        if not self.agent or not self.current_state:
            print_error("No active session to continue.")
            return 1
        
        print()
        print_info("💬 Interactive GDD Creation Mode")
        print_info("Type 'help' for commands, 'quit' to exit, 'status' for progress")
        print()
        
        # Show initial agent response if available
        if self.current_state.get("current_agent_response"):
            print("🤖 Agent:", self.current_state["current_agent_response"])
            print()
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print_info("👋 Ending GDD creation session.")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'status':
                    self._show_progress_summary()
                    continue
                elif user_input.lower() == 'save':
                    self._save_session()
                    continue
                elif user_input.lower() == 'preview':
                    self._show_gdd_preview()
                    continue
                
                # Process user input through the agent
                success, agent_response, updated_state = await self.agent.process_user_input(
                    user_input, self.current_state
                )
                
                if not success:
                    print_error(f"❌ Error: {agent_response}")
                    continue
                
                # Update current state
                self.current_state = updated_state
                
                # Show agent response
                print()
                print("🤖 Agent:", agent_response)
                print()
                
                # Check if GDD is complete
                if self.current_state.get("is_completed"):
                    print_success("🎉 GDD creation complete!")
                    
                    # Ask if user wants to save the final GDD
                    save_response = input("💾 Save the completed GDD to docs/gdd.md? (y/n): ").strip().lower()
                    if save_response in ['y', 'yes']:
                        # The finalization should have already saved it, but confirm
                        print_success("✅ GDD saved successfully!")
                    
                    break
                
            except KeyboardInterrupt:
                print()
                print_info("👋 Session interrupted. Progress has been saved.")
                break
            except Exception as e:
                print_error(f"Unexpected error: {e}")
                break
        
        return 0
    
    def _show_session_instructions(self):
        """Show instructions for the interactive session."""
        print()
        print_info("📋 GDD Creation Instructions:")
        print("• Answer the agent's questions to build your Game Design Document")
        print("• Type 'help' to see available commands")
        print("• Type 'status' to check your progress")
        print("• Type 'preview' to see your current GDD")
        print("• Type 'quit' to exit and save progress")
        print()
    
    def _show_help(self):
        """Show help information for interactive commands."""
        print()
        print_info("📖 Available Commands:")
        print("• help     - Show this help message")
        print("• status   - Show current progress and section status") 
        print("• preview  - Show current GDD document preview")
        print("• save     - Manually save session progress")
        print("• quit     - Exit and save progress")
        print()
        print_info("💡 Tips:")
        print("• Be specific and detailed in your responses")
        print("• You can revise previous answers by mentioning the section")
        print("• The agent will guide you through each section systematically")
        print()
    
    def _show_progress_summary(self):
        """Show a summary of current progress."""
        if not self.agent or not self.current_state:
            return
        
        status = self.agent.get_session_status(self.current_state)
        progress = status["progress"]
        
        print()
        print_info("📊 Progress Summary:")
        print(f"Current Section: {progress['current_section_name']} ({progress['current_section']}/8)")
        print(f"Completed: {progress['completed_sections']} sections ({progress['completion_percentage']:.1f}%)")
        print(f"Session Duration: {progress['session_duration_minutes']:.1f} minutes")
        print()
    
    def _show_gdd_preview(self):
        """Show a preview of the current GDD."""
        if not self.agent or not self.current_state:
            return
        
        try:
            preview = self.agent.export_gdd_preview(self.current_state)
            print()
            print_info("📄 Current GDD Preview:")
            print("=" * 60)
            print(preview)
            print("=" * 60)
            print()
        except Exception as e:
            print_error(f"Failed to generate preview: {e}")
    
    def _save_session(self):
        """Manually save the current session."""
        if not self.current_state:
            print_warning("No session to save.")
            return
        
        try:
            # Session is auto-saved by the agent, but we can confirm it
            print_success("💾 Session progress saved!")
        except Exception as e:
            print_error(f"Failed to save session: {e}")


def setup_gdd_parser(subparsers):
    """Set up the GDD command parser."""
    gdd_parser = subparsers.add_parser('gdd', help='Game Design Document creation and management')
    gdd_subparsers = gdd_parser.add_subparsers(dest='gdd_command', help='GDD commands')
    
    # Create command
    create_parser = gdd_subparsers.add_parser('create', help='Start interactive GDD creation')
    create_parser.add_argument('--style', choices=['coach', 'assembler'], default='coach',
                              help='Interaction style (default: coach)')
    create_parser.add_argument('--model', choices=['lite', 'standard', 'pro'], default='standard',
                              help='Model complexity tier (default: standard)')
    create_parser.add_argument('--force', action='store_true',
                              help='Force new session even if one exists')
    
    # Resume command
    resume_parser = gdd_subparsers.add_parser('resume', help='Resume existing GDD creation session')
    resume_parser.add_argument('--style', choices=['coach', 'assembler'], default='coach',
                              help='Interaction style (default: coach)')
    resume_parser.add_argument('--model', choices=['lite', 'standard', 'pro'], default='standard',
                              help='Model complexity tier (default: standard)')
    
    # Status command
    status_parser = gdd_subparsers.add_parser('status', help='Show GDD creation status')
    
    # Export command
    export_parser = gdd_subparsers.add_parser('export', help='Export GDD to file')
    export_parser.add_argument('--output', '-o', help='Output file path')
    export_parser.add_argument('--preview', action='store_true', help='Show preview instead of saving')
    
    return gdd_parser


async def handle_gdd_command(args, project_root: str) -> int:
    """
    Handle GDD commands.
    
    Args:
        args: Parsed command line arguments
        project_root (str): Path to the project root
        
    Returns:
        int: Exit code
    """
    gdd_commands = GDDCommands(project_root)
    
    if args.gdd_command == 'create':
        return await gdd_commands.create_gdd(args)
    elif args.gdd_command == 'resume':
        return await gdd_commands.resume_gdd(args)
    elif args.gdd_command == 'status':
        return gdd_commands.status_gdd(args)
    elif args.gdd_command == 'export':
        return gdd_commands.export_gdd(args)
    else:
        print_error("No GDD command specified. Use --help for available commands.")
        return 1