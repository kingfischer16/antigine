"""
gdd.py
######

CLI commands for GDD (Game Design Document) creation and management.
Uses the new atomic Flash Lite architecture with deterministic Python control.
"""

# Imports
import sys
from pathlib import Path
from typing import Optional

from ...core.agents.gdd_creator import GDDController
from ..utils.output import print_success, print_error, print_info, print_warning


class GDDCommands:
    """CLI commands for GDD creation and management using atomic Flash Lite operations."""
    
    def __init__(self, project_root: str):
        """Initialize GDD commands for a specific project."""
        self.project_root = project_root
        self.controller: Optional[GDDController] = None
    
    def _initialize_controller(self) -> bool:
        """Initialize the GDD Controller."""
        try:
            self.controller = GDDController(self.project_root)
            return True
        except Exception as e:
            print_error(f"Failed to initialize GDD Controller: {e}")
            return False
    
    def create_gdd(self, args) -> int:
        """
        Start interactive GDD creation process.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        force_new = getattr(args, 'force', False)
        
        print_info("🎮 Starting GDD creation with atomic Flash Lite approach...")
        
        if not self._initialize_controller():
            return 1
        
        # Check for existing session
        if not force_new:
            success, message = self.controller.load_existing_session()
            if success:
                print_info(f"📄 Resuming existing session: {message}")
                return self._continue_interactive_session()
        
        # Start new session
        success, message = self.controller.create_new_session()
        if not success:
            print_error(f"Failed to start GDD creation: {message}")
            return 1
        
        print_success(f"✨ {message}")
        
        # Show initial instructions
        self._show_session_instructions()
        
        # Start with first section
        success, start_message, questions = self.controller.start_section(1)
        if not success:
            print_error(f"Failed to start first section: {start_message}")
            return 1
        
        print_info(f"📝 {start_message}")
        self._show_questions(questions)
        
        # Start interactive session
        return self._continue_interactive_session()
    
    def resume_gdd(self, args) -> int:
        """
        Resume an existing GDD creation session.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        if not self._initialize_controller():
            return 1
        
        success, message = self.controller.load_existing_session()
        if not success:
            print_error(f"Failed to resume session: {message}")
            return 1
        
        print_success(f"📄 {message}")
        
        # Show current progress
        self._show_progress_summary()
        
        # Continue interactive session
        return self._continue_interactive_session()
    
    def status_gdd(self, args) -> int:
        """
        Show current GDD creation status.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        if not self._initialize_controller():
            return 1
        
        # Try to load existing session
        success, message = self.controller.load_existing_session()
        if not success:
            print_info("No active GDD creation session found.")
            return 0
        
        print_info("📊 GDD Creation Status:")
        print()
        
        # Show progress summary
        status = self.controller.get_session_status()
        
        print(f"Session ID: {status['session_id']}")
        print(f"Tech Stack: {status['tech_stack']} / {status['language']}")
        print(f"Progress: {status['completed_sections']}/{status['total_sections']} sections ({status['completion_percentage']:.1f}%)")
        print()
        
        # Show current section info
        current_info = self.controller.get_current_section_info()
        if "error" not in current_info:
            print(f"Current Section: {current_info['section_number']}. {current_info['name']}")
            print(f"Status: {current_info['status']}")
            print(f"Questions asked: {current_info['questions_asked_count']}")
            print(f"Responses given: {current_info['responses_given_count']}")
        
        return 0
    
    def export_gdd(self, args) -> int:
        """
        Export current GDD to a file.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        preview_only = getattr(args, 'preview', False)
        
        if not self._initialize_controller():
            return 1
        
        # Load existing session
        success, message = self.controller.load_existing_session()
        if not success:
            print_error("No GDD session found to export.")
            return 1
        
        try:
            if preview_only:
                # Show current progress as preview
                self._show_gdd_preview()
            else:
                # Generate final GDD
                success, result_message = self.controller.generate_final_gdd()
                if success:
                    print_success(f"📁 {result_message}")
                else:
                    print_error(f"Export failed: {result_message}")
                    return 1
            
            return 0
            
        except Exception as e:
            print_error(f"Failed to export GDD: {e}")
            return 1
    
    def _continue_interactive_session(self) -> int:
        """Continue the interactive GDD creation session."""
        if not self.controller:
            print_error("No controller initialized.")
            return 1
        
        print()
        print_info("💬 Interactive GDD Creation Mode")
        print_info("Type 'help' for commands, 'quit' to exit, 'status' for progress")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print_info("👋 Ending GDD creation session. Progress has been saved.")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'status':
                    self._show_progress_summary()
                    continue
                elif user_input.lower() == 'next':
                    self._show_next_section_preview()
                    continue
                elif user_input.lower() == 'preview':
                    self._show_gdd_preview()
                    continue
                elif user_input.lower().startswith('section '):
                    # Jump to specific section
                    try:
                        section_num = int(user_input.split()[1])
                        success, start_message, questions = self.controller.start_section(section_num)
                        if success:
                            print_info(f"📝 {start_message}")
                            self._show_questions(questions)
                        else:
                            print_error(start_message)
                    except (ValueError, IndexError):
                        print_error("Usage: section <number> (e.g., 'section 3')")
                    continue
                
                # Process user response through the controller
                success, feedback, next_questions = self.controller.process_user_response(user_input)
                
                if not success:
                    print_error(f"❌ Error: {feedback}")
                    continue
                
                # Show feedback
                print()
                print("🤖 Coach:", feedback)
                
                # If section is complete and GDD is done
                if next_questions is None and "GDD creation is now complete" in feedback:
                    print()
                    print_success("🎉 Congratulations! Your GDD is complete!")
                    
                    # Ask if user wants to generate final document
                    save_response = input("💾 Generate final GDD document? (y/n): ").strip().lower()
                    if save_response in ['y', 'yes']:
                        success, result_message = self.controller.generate_final_gdd()
                        if success:
                            print_success(f"✅ {result_message}")
                        else:
                            print_error(f"Failed to generate final GDD: {result_message}")
                    
                    break
                
                # If section is complete but more sections remain
                elif next_questions is None:
                    print()
                    next_preview = self.controller.get_next_section_preview()
                    if next_preview:
                        print_info(f"🎯 Next: Section {next_preview['section_number']}. {next_preview['name']}")
                        print_info(f"   {next_preview['description']}")
                        print()
                        continue_response = input("Continue to next section? (y/n): ").strip().lower()
                        if continue_response in ['y', 'yes', '']:
                            next_section_num = next_preview['section_number']
                            success, start_message, questions = self.controller.start_section(next_section_num)
                            if success:
                                print_info(f"📝 {start_message}")
                                self._show_questions(questions)
                            else:
                                print_error(start_message)
                
                # Show follow-up questions if available
                elif next_questions:
                    print()
                    self._show_questions(next_questions)
                
                print()
                
            except KeyboardInterrupt:
                print()
                print_info("👋 Session interrupted. Progress has been saved.")
                break
            except Exception as e:
                print_error(f"Unexpected error: {e}")
                break
        
        return 0
    
    def _show_questions(self, questions):
        """Display questions to the user."""
        if not questions:
            return
        
        print_info("📋 Questions to help you develop this section:")
        for i, question in enumerate(questions, 1):
            print(f"   {i}. {question}")
        print()
    
    def _show_session_instructions(self):
        """Show instructions for the interactive session."""
        print()
        print_info("📋 GDD Creation Instructions:")
        print("• Answer the coach's questions to build your Game Design Document")
        print("• Type 'help' to see available commands")
        print("• Type 'status' to check your progress")
        print("• Type 'next' to see what's coming up")
        print("• Type 'preview' to see your current GDD")
        print("• Type 'section <number>' to jump to a specific section")
        print("• Type 'quit' to exit and save progress")
        print()
    
    def _show_help(self):
        """Show help information for interactive commands."""
        print()
        print_info("📖 Available Commands:")
        print("• help          - Show this help message")
        print("• status        - Show current progress and section status") 
        print("• next          - Preview the next section")
        print("• preview       - Show current GDD document preview")
        print("• section <num> - Jump to a specific section (e.g., 'section 3')")
        print("• quit          - Exit and save progress")
        print()
        print_info("💡 Tips:")
        print("• Be specific and detailed in your responses")
        print("• The coach will evaluate when you've provided enough information")
        print("• You can always return to previous sections if needed")
        print()
    
    def _show_progress_summary(self):
        """Show a summary of current progress."""
        if not self.controller:
            return
        
        status = self.controller.get_session_status()
        current_info = self.controller.get_current_section_info()
        
        print()
        print_info("📊 Progress Summary:")
        print(f"Current Section: {current_info.get('name', 'Unknown')} ({status['current_section']}/8)")
        print(f"Completed: {status['completed_sections']} sections ({status['completion_percentage']:.1f}%)")
        print()
    
    def _show_next_section_preview(self):
        """Show preview of the next section."""
        if not self.controller:
            return
        
        next_preview = self.controller.get_next_section_preview()
        if next_preview:
            print()
            print_info(f"🎯 Next Section: {next_preview['section_number']}. {next_preview['name']}")
            print(f"   {next_preview['description']}")
            print()
        else:
            print_info("🎉 You're on the final section!")
    
    def _show_gdd_preview(self):
        """Show a preview of the current GDD."""
        if not self.controller:
            return
        
        try:
            status = self.controller.get_session_status()
            print()
            print_info("📄 Current GDD Progress:")
            print("=" * 60)
            print(f"Project: {status['tech_stack']}/{status['language']} Game")
            print(f"Progress: {status['completed_sections']}/{status['total_sections']} sections")
            print("=" * 60)
            print()
            
            # Show completed sections
            for i in range(1, 9):
                section_name = self.controller.SECTIONS_DEFINITION[i]["name"]
                if i <= status['completed_sections']:
                    print(f"✅ Section {i}: {section_name}")
                elif i == status['current_section']:
                    print(f"🔄 Section {i}: {section_name} (In Progress)")
                else:
                    print(f"⏳ Section {i}: {section_name}")
            
            print("=" * 60)
            print()
        except Exception as e:
            print_error(f"Failed to generate preview: {e}")


def setup_gdd_parser(subparsers):
    """Set up the GDD command parser."""
    gdd_parser = subparsers.add_parser('gdd', help='Game Design Document creation and management')
    gdd_subparsers = gdd_parser.add_subparsers(dest='gdd_command', help='GDD commands')
    
    # Create command
    create_parser = gdd_subparsers.add_parser('create', help='Start interactive GDD creation')
    create_parser.add_argument('--force', action='store_true',
                              help='Force new session even if one exists')
    
    # Resume command
    resume_parser = gdd_subparsers.add_parser('resume', help='Resume existing GDD creation session')
    
    # Status command
    status_parser = gdd_subparsers.add_parser('status', help='Show GDD creation status')
    
    # Export command
    export_parser = gdd_subparsers.add_parser('export', help='Export GDD to file')
    export_parser.add_argument('--preview', action='store_true', help='Show preview instead of generating final document')
    
    return gdd_parser


def handle_gdd_command(args, project_root: str) -> int:
    """
    Handle GDD commands with the new atomic architecture.
    
    Args:
        args: Parsed command line arguments
        project_root (str): Path to the project root
        
    Returns:
        int: Exit code
    """
    gdd_commands = GDDCommands(project_root)
    
    if args.gdd_command == 'create':
        return gdd_commands.create_gdd(args)
    elif args.gdd_command == 'resume':
        return gdd_commands.resume_gdd(args)
    elif args.gdd_command == 'status':
        return gdd_commands.status_gdd(args)
    elif args.gdd_command == 'export':
        return gdd_commands.export_gdd(args)
    else:
        print_error("No GDD command specified. Use --help for available commands.")
        return 1