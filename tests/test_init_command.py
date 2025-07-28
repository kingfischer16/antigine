"""
test_init_command.py
####################

Unit tests for the init command functionality, focusing on the new required
language and tech stack selection behavior.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from argparse import Namespace
from antigine.cli.commands.init import handle_init, _get_programming_language, _get_tech_stack


class TestInitHelperFunctions(unittest.TestCase):
    """Test cases for init command helper functions."""

    def test_get_programming_language_from_args(self):
        """Test that _get_programming_language returns language from args when provided."""
        args = Namespace(language="Python")
        result = _get_programming_language(args)
        self.assertEqual(result, "Python")

    @patch('antigine.cli.commands.init.prompt_for_choice')
    def test_get_programming_language_interactive(self, mock_prompt):
        """Test that _get_programming_language prompts when language not in args."""
        mock_prompt.return_value = "C++"
        args = Namespace()  # No language attribute
        
        result = _get_programming_language(args)
        
        self.assertEqual(result, "C++")
        mock_prompt.assert_called_once_with(
            "Select programming language",
            choices=["Lua", "Python", "C++", "C"],
            default=None
        )

    @patch('antigine.cli.commands.init.print_info')
    @patch('antigine.cli.commands.init.prompt_for_choice')
    def test_get_programming_language_displays_choices(self, mock_prompt, mock_print):
        """Test that _get_programming_language displays available choices."""
        mock_prompt.return_value = "Lua"
        args = Namespace()
        
        _get_programming_language(args)
        
        # Verify that choices are displayed
        mock_print.assert_any_call("Please select a programming language for your project:")
        mock_print.assert_any_call("  1. Lua")
        mock_print.assert_any_call("  2. Python")
        mock_print.assert_any_call("  3. C++")
        mock_print.assert_any_call("  4. C")

    def test_get_tech_stack_from_args(self):
        """Test that _get_tech_stack returns tech stack from args when provided."""
        args = Namespace(tech_stack="Love2D")
        result = _get_tech_stack(args, "Lua")
        self.assertEqual(result, "Love2D")

    @patch('antigine.cli.commands.init.prompt_for_input')
    @patch('antigine.cli.commands.init.tech_stack_manager')
    def test_get_tech_stack_interactive(self, mock_manager, mock_prompt):
        """Test that _get_tech_stack prompts when tech stack not in args."""
        # Mock the tech stack manager
        mock_manager.get_available_libraries.return_value = {
            "Love2D": MagicMock(description="2D game framework for Lua"),
            "Pygame": MagicMock(description="Cross-platform Python game library")
        }
        mock_prompt.return_value = "Love2D"
        args = Namespace()  # No tech_stack attribute
        
        result = _get_tech_stack(args, "Lua")
        
        self.assertEqual(result, "Love2D")
        mock_manager.get_available_libraries.assert_called_once_with("Lua")
        mock_prompt.assert_called_once_with("Enter tech stack for Lua", default=None)

    @patch('antigine.cli.commands.init.print_error')
    @patch('antigine.cli.commands.init.prompt_for_input')
    @patch('antigine.cli.commands.init.tech_stack_manager')
    def test_get_tech_stack_empty_input_raises_error(self, mock_manager, mock_prompt, mock_print_error):
        """Test that _get_tech_stack raises error when user provides empty input."""
        mock_manager.get_available_libraries.return_value = {}
        mock_prompt.return_value = ""  # Empty input
        args = Namespace()
        
        with self.assertRaises(ValueError) as context:
            _get_tech_stack(args, "Python")
        
        self.assertIn("Tech stack input is required", str(context.exception))
        mock_print_error.assert_called_once_with("Tech stack is required. Please specify at least one library.")

    @patch('antigine.cli.commands.init.print_info')
    @patch('antigine.cli.commands.init.prompt_for_input')
    @patch('antigine.cli.commands.init.tech_stack_manager')
    def test_get_tech_stack_displays_available_libraries(self, mock_manager, mock_prompt, mock_print):
        """Test that _get_tech_stack displays available libraries with descriptions."""
        mock_lib1 = MagicMock()
        mock_lib1.description = "2D game framework for Lua"
        mock_lib2 = MagicMock()
        mock_lib2.description = "Cross-platform Python game library"
        
        mock_manager.get_available_libraries.return_value = {
            "Love2D": mock_lib1,
            "Pygame": mock_lib2
        }
        mock_prompt.return_value = "Love2D"
        args = Namespace()
        
        _get_tech_stack(args, "Python")
        
        # Verify that libraries are displayed with descriptions
        mock_print.assert_any_call("Available libraries for Python:")
        mock_print.assert_any_call("  1. Love2D - 2D game framework for Lua")
        mock_print.assert_any_call("  2. Pygame - Cross-platform Python game library")
        
        # Verify usage instructions are displayed
        mock_print.assert_any_call("You can specify:")
        mock_print.assert_any_call("  - A single library (e.g., 'Love2D', 'Pygame', 'SDL2')")
        mock_print.assert_any_call("  - Multiple libraries separated by '+' (e.g., 'SDL2+OpenGL+GLM')")


class TestInitCommandIntegration(unittest.TestCase):
    """Integration tests for the init command with required language/tech stack selection."""

    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory and restore working directory."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('antigine.cli.commands.init.ProjectSetupManager')
    @patch('antigine.cli.commands.init.resolve_tech_stack_name')
    @patch('antigine.cli.commands.init._get_tech_stack')
    @patch('antigine.cli.commands.init._get_programming_language')
    @patch('antigine.cli.commands.init.detect_project_directory')
    def test_handle_init_with_command_line_args(self, mock_detect, mock_get_lang, mock_get_tech, mock_resolve, mock_manager):
        """Test handle_init with language and tech stack provided via command line."""
        # Setup mocks
        mock_detect.return_value = False
        mock_get_lang.return_value = "Python"
        mock_get_tech.return_value = "Pygame"
        mock_resolve.return_value = "Pygame"
        
        mock_setup_manager = MagicMock()
        mock_manager.return_value = mock_setup_manager
        
        # Create args with all required parameters
        args = Namespace(name="TestGame", language="Python", tech_stack="Pygame")
        
        result = handle_init(args)
        
        # Verify success
        self.assertEqual(result, 0)
        
        # Verify helper functions were called
        mock_get_lang.assert_called_once_with(args)
        mock_get_tech.assert_called_once_with(args, "Python")
        mock_resolve.assert_called_once_with("Pygame")
        
        # Verify project setup was called
        mock_manager.assert_called_once_with(self.temp_dir)
        mock_setup_manager.create_project_folders.assert_called_once()
        mock_setup_manager.edit_project_file.assert_any_call("project_name", "TestGame")
        mock_setup_manager.edit_project_file.assert_any_call("tech_stack", "Pygame")
        mock_setup_manager.create_empty_ledger.assert_called_once()

    @patch('antigine.cli.commands.init.ProjectSetupManager')
    @patch('antigine.cli.commands.init.resolve_tech_stack_name')
    @patch('antigine.cli.commands.init._get_tech_stack')
    @patch('antigine.cli.commands.init._get_programming_language')
    @patch('antigine.cli.commands.init.detect_project_directory')
    @patch('antigine.cli.commands.init.prompt_for_input')
    def test_handle_init_interactive_mode(self, mock_prompt_input, mock_detect, mock_get_lang, mock_get_tech, mock_resolve, mock_manager):
        """Test handle_init in interactive mode without command line args."""
        # Setup mocks
        mock_detect.return_value = False
        mock_prompt_input.return_value = "MyGame"  # Project name prompt
        mock_get_lang.return_value = "C++"
        mock_get_tech.return_value = "SDL2+OpenGL"
        mock_resolve.return_value = "SDL2+OpenGL"
        
        mock_setup_manager = MagicMock()
        mock_manager.return_value = mock_setup_manager
        
        # Create args without language or tech_stack, but with name
        args = Namespace(name="MyGame")
        
        result = handle_init(args)
        
        # Verify success
        self.assertEqual(result, 0)
        
        # Verify interactive prompts were used
        mock_prompt_input.assert_not_called()  # Name was provided in args
        mock_get_lang.assert_called_once_with(args)
        mock_get_tech.assert_called_once_with(args, "C++")

    @patch('antigine.cli.commands.init.detect_project_directory')
    def test_handle_init_existing_project_error(self, mock_detect):
        """Test handle_init returns error when project already exists."""
        mock_detect.return_value = True  # Project already exists
        
        args = Namespace(name="TestGame")
        result = handle_init(args)
        
        # Should return error code
        self.assertEqual(result, 1)

    @patch('antigine.cli.commands.init.ProjectSetupManager')
    @patch('antigine.cli.commands.init._get_tech_stack')
    @patch('antigine.cli.commands.init._get_programming_language')
    @patch('antigine.cli.commands.init.detect_project_directory')
    def test_handle_init_tech_stack_validation_error(self, mock_detect, mock_get_lang, mock_get_tech, mock_manager):
        """Test handle_init handles tech stack validation errors properly."""
        mock_detect.return_value = False
        mock_get_lang.return_value = "Python"
        mock_get_tech.side_effect = ValueError("Tech stack input is required")
        
        args = Namespace(name="TestGame")
        result = handle_init(args)
        
        # Should return error code
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()