"""
test_gdd_cli_integration.py
###########################

Integration tests for GDD CLI commands with the new atomic Flash Lite architecture.
Tests the interaction between CLI commands and GDDController.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO

from antigine.cli.commands.gdd import GDDCommands, handle_gdd_command
from antigine.core.agents.gdd_creator import SectionStatus


class TestGDDCLIIntegration(unittest.TestCase):
    """Integration test cases for GDD CLI commands."""

    def setUp(self):
        """Set up test environment with temporary project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create .antigine folder to simulate valid project
        self.antigine_folder = self.project_root / ".antigine"
        self.antigine_folder.mkdir()

        # Create basic project config
        config_file = self.antigine_folder / "project.json"
        config_data = {"tech_stack": "Love2D", "project_language": "Lua", "project_name": "TestGame"}
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        # Initialize database schema for ProjectLedgerManager
        from antigine.core.database import initialize_database

        db_path = self.antigine_folder / "ledger.db"
        initialize_database(str(db_path))

        # Initialize GDD commands
        self.gdd_commands = GDDCommands(str(self.project_root))

        # Mock args for testing
        self.mock_args = Mock()
        self.mock_args.force = False
        self.mock_args.preview = False

    def tearDown(self):
        """Clean up test environment."""
        # Close any database connections
        if hasattr(self, "gdd_commands") and self.gdd_commands:
            if hasattr(self.gdd_commands, "controller") and self.gdd_commands.controller:
                if hasattr(self.gdd_commands.controller, "project_manager"):
                    del self.gdd_commands.controller.project_manager
                del self.gdd_commands.controller
            del self.gdd_commands

        # Force garbage collection to release file handles
        import gc

        gc.collect()

        # Clean up temp directory
        try:
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            # On Windows, sometimes files are still locked
            import time

            time.sleep(0.1)
            shutil.rmtree(self.temp_dir)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_create_gdd_command_new_session(self, mock_llm):
        """Test creating a new GDD session via CLI."""
        # Mock LLM responses
        mock_llm.invoke.return_value = Mock(content="1. What is your game concept?\n2. Who is the target audience?")

        with patch("builtins.input", side_effect=["quit"]):  # Immediately quit
            result = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result, 0)  # Success
        self.assertIsNotNone(self.gdd_commands.controller)
        self.assertIsNotNone(self.gdd_commands.controller.current_session)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_create_gdd_command_force_new(self, mock_llm):
        """Test creating GDD with force flag."""
        mock_llm.invoke.return_value = Mock(content="1. Test question?")

        # Create initial session
        self.gdd_commands._initialize_controller()
        self.gdd_commands.controller.create_new_session()
        original_session_id = self.gdd_commands.controller.current_session.session_id

        # Force create new session
        self.mock_args.force = True

        with patch("builtins.input", side_effect=["quit"]):
            result = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result, 0)
        # Should have created new session (different ID)
        self.assertNotEqual(self.gdd_commands.controller.current_session.session_id, original_session_id)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_resume_gdd_command_existing_session(self, mock_llm):
        """Test resuming an existing GDD session."""
        mock_llm.invoke.return_value = Mock(content="1. Continue with your game concept?")

        # Create initial session
        self.gdd_commands._initialize_controller()
        self.gdd_commands.controller.create_new_session()
        self.gdd_commands.controller.start_section(1)

        # Create new GDDCommands instance to simulate fresh CLI invocation
        new_gdd_commands = GDDCommands(str(self.project_root))

        with patch("builtins.input", side_effect=["quit"]):
            result = new_gdd_commands.resume_gdd(self.mock_args)

        self.assertEqual(result, 0)
        self.assertIsNotNone(new_gdd_commands.controller.current_session)

    def test_resume_gdd_command_no_session(self):
        """Test resuming when no session exists."""
        result = self.gdd_commands.resume_gdd(self.mock_args)

        self.assertEqual(result, 1)  # Error

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_status_gdd_command_with_session(self, mock_llm):
        """Test showing status when session exists."""
        mock_llm.invoke.return_value = Mock(content="Mock response")

        # Create session with some progress
        self.gdd_commands._initialize_controller()
        self.gdd_commands.controller.create_new_session()
        self.gdd_commands.controller.start_section(1)

        # Complete first section
        section = self.gdd_commands.controller.current_session.sections[1]
        section.status = SectionStatus.COMPLETED

        result = self.gdd_commands.status_gdd(self.mock_args)

        self.assertEqual(result, 0)

    def test_status_gdd_command_no_session(self):
        """Test showing status when no session exists."""
        result = self.gdd_commands.status_gdd(self.mock_args)

        self.assertEqual(result, 0)  # Should show "no session" message but not error

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_export_gdd_preview(self, mock_llm):
        """Test exporting GDD preview."""
        mock_llm.invoke.return_value = Mock(content="Mock response")

        # Create session with some progress
        self.gdd_commands._initialize_controller()
        self.gdd_commands.controller.create_new_session()

        self.mock_args.preview = True
        result = self.gdd_commands.export_gdd(self.mock_args)

        self.assertEqual(result, 0)

    def test_export_gdd_no_session(self):
        """Test exporting when no session exists."""
        result = self.gdd_commands.export_gdd(self.mock_args)

        self.assertEqual(result, 1)  # Error

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_interactive_session_help_command(self, mock_llm):
        """Test help command in interactive session."""
        mock_llm.invoke.return_value = Mock(content="1. Test question?")

        # Capture stdout to check help output
        captured_output = StringIO()

        with patch("builtins.input", side_effect=["help", "quit"]), patch("sys.stdout", captured_output):
            result = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result, 0)
        output = captured_output.getvalue()
        self.assertIn("Available Commands", output)
        self.assertIn("help", output)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_interactive_session_status_command(self, mock_llm):
        """Test status command in interactive session."""
        mock_llm.invoke.return_value = Mock(content="1. Test question?")

        with patch("builtins.input", side_effect=["status", "quit"]):
            result = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result, 0)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_interactive_session_section_jump(self, mock_llm):
        """Test jumping to specific section in interactive session."""
        mock_llm.invoke.return_value = Mock(content="1. Test question for section 3?")

        with patch("builtins.input", side_effect=["section 3", "quit"]):
            result = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result, 0)
        # Verify that section 3 was started
        self.assertEqual(self.gdd_commands.controller.current_session.current_section, 3)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_interactive_session_user_response_processing(self, mock_llm):
        """Test processing user responses in interactive session."""
        # Mock different LLM responses for different calls
        mock_responses = [
            Mock(content="1. What is your game concept?"),  # Initial questions
            Mock(content="COMPLETE: Yes\nREASON: All criteria satisfied"),  # Evaluation
            Mock(content="# Core Vision\nGame concept: Platformer game"),  # Structuring
        ]
        mock_llm.invoke.side_effect = mock_responses

        with patch(
            "builtins.input", side_effect=["My game is a platformer for teenagers", "quit"]  # User response  # Exit
        ):
            result = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result, 0)

        # Verify that user response was recorded
        section = self.gdd_commands.controller.current_session.sections[1]
        self.assertEqual(len(section.user_responses), 1)
        self.assertIn("platformer", section.user_responses[0])

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_interactive_session_section_completion_flow(self, mock_llm):
        """Test the flow when a section is completed."""
        # Mock responses for section completion
        mock_responses = [
            Mock(content="1. What is your game concept?"),  # Initial questions
            Mock(content="COMPLETE: Yes\nREASON: Section complete"),  # Evaluation
            Mock(content="# Core Vision\nCompleted content"),  # Structuring
        ]
        mock_llm.invoke.side_effect = mock_responses

        with patch(
            "builtins.input",
            side_effect=[
                "Detailed game concept response",  # Complete the section
                "y",  # Continue to next section
                "quit",  # Exit from section 2
            ],
        ):
            result = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result, 0)

        # Verify section 1 was completed and section 2 was started
        section1 = self.gdd_commands.controller.current_session.sections[1]
        section2 = self.gdd_commands.controller.current_session.sections[2]
        self.assertEqual(section1.status, SectionStatus.COMPLETED)
        self.assertEqual(section2.status, SectionStatus.IN_PROGRESS)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_handle_gdd_command_function(self, mock_llm):
        """Test the handle_gdd_command function directly."""
        mock_llm.invoke.return_value = Mock(content="1. Test question?")

        # Test create command
        args = Mock()
        args.gdd_command = "create"
        args.force = False

        with patch("builtins.input", side_effect=["quit"]):
            result = handle_gdd_command(args, str(self.project_root))

        self.assertEqual(result, 0)

    def test_handle_gdd_command_invalid(self):
        """Test handle_gdd_command with invalid command."""
        args = Mock()
        args.gdd_command = "invalid"

        result = handle_gdd_command(args, str(self.project_root))

        self.assertEqual(result, 1)

    def test_handle_gdd_command_no_command(self):
        """Test handle_gdd_command with no command specified."""
        args = Mock()
        args.gdd_command = None

        result = handle_gdd_command(args, str(self.project_root))

        self.assertEqual(result, 1)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_controller_initialization_failure(self, mock_llm):
        """Test handling of controller initialization failure."""
        # Create invalid project directory (no .antigine folder)
        invalid_dir = tempfile.mkdtemp()

        try:
            gdd_commands = GDDCommands(invalid_dir)
            result = gdd_commands.create_gdd(self.mock_args)

            self.assertEqual(result, 1)  # Should fail gracefully
        finally:
            shutil.rmtree(invalid_dir)

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_keyboard_interrupt_handling(self, mock_llm):
        """Test graceful handling of keyboard interrupt."""
        mock_llm.invoke.return_value = Mock(content="1. Test question?")

        with patch("builtins.input", side_effect=KeyboardInterrupt()):
            result = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result, 0)  # Should handle interrupt gracefully

    @patch("antigine.core.agents.gdd_creator.lite_model")
    def test_session_persistence_across_cli_invocations(self, mock_llm):
        """Test that sessions persist across different CLI invocations."""
        mock_llm.invoke.return_value = Mock(content="1. Test question?")

        # First invocation - create session
        with patch("builtins.input", side_effect=["My response", "quit"]):
            result1 = self.gdd_commands.create_gdd(self.mock_args)

        self.assertEqual(result1, 0)
        original_session_id = self.gdd_commands.controller.current_session.session_id

        # Second invocation - should resume same session
        new_gdd_commands = GDDCommands(str(self.project_root))
        with patch("builtins.input", side_effect=["quit"]):
            result2 = new_gdd_commands.resume_gdd(self.mock_args)

        self.assertEqual(result2, 0)
        self.assertEqual(new_gdd_commands.controller.current_session.session_id, original_session_id)


if __name__ == "__main__":
    unittest.main()
