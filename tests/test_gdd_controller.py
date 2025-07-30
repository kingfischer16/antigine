"""
test_gdd_controller.py
######################

Unit tests for the atomic Flash Lite-based GDD Controller.
Tests deterministic state management, atomic LLM operations, and process control.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from antigine.core.agents.gdd_creator import GDDController, SectionStatus, SectionData, GDDSession


class TestGDDController(unittest.TestCase):
    """Test cases for GDDController class."""
    
    def setUp(self):
        """Set up test environment with temporary project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create .antigine folder to simulate valid project
        self.antigine_folder = self.project_root / ".antigine"
        self.antigine_folder.mkdir()
        
        # Create basic project config for ProjectLedgerManager
        config_file = self.antigine_folder / "project.json"
        config_data = {
            "tech_stack": "Love2D",
            "project_language": "Lua",
            "project_name": "TestGame"
        }
        config_file.write_text(json.dumps(config_data), encoding='utf-8')
        
        # Initialize database schema for ProjectLedgerManager
        from antigine.core.database import initialize_database
        db_path = self.antigine_folder / "ledger.db"
        initialize_database(str(db_path))
        
        # Mock the LLM to avoid actual API calls
        with patch('antigine.core.agents.gdd_creator.lite_model') as mock_llm:
            mock_llm.invoke.return_value = Mock(content="Mocked LLM response")
            self.controller = GDDController(str(self.project_root))
            self.mock_llm = mock_llm
    
    def tearDown(self):
        """Clean up test environment."""
        # Close any database connections
        if hasattr(self, 'controller') and self.controller:
            if hasattr(self.controller, 'project_manager'):
                del self.controller.project_manager
            del self.controller
        
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
    
    def test_init_controller(self):
        """Test GDDController initialization."""
        self.assertEqual(self.controller.project_root, self.project_root)
        self.assertEqual(self.controller.tech_stack, "Love2D")
        self.assertEqual(self.controller.language, "Lua")
        self.assertIsNone(self.controller.current_session)
        self.assertTrue(self.controller.session_folder.exists())
    
    def test_sections_definition(self):
        """Test that all 8 sections are properly defined."""
        self.assertEqual(len(self.controller.SECTIONS_DEFINITION), 8)
        
        # Check that each section has required fields
        for num, section_def in self.controller.SECTIONS_DEFINITION.items():
            self.assertIn("name", section_def)
            self.assertIn("description", section_def)
            self.assertIn("criteria", section_def)
            self.assertIsInstance(section_def["criteria"], list)
            self.assertGreater(len(section_def["criteria"]), 0)
    
    def test_create_new_session(self):
        """Test creating a new GDD session."""
        success, message = self.controller.create_new_session()
        
        self.assertTrue(success)
        self.assertIn("New GDD session created", message)
        self.assertIsNotNone(self.controller.current_session)
        self.assertEqual(self.controller.current_session.current_section, 1)
        self.assertEqual(len(self.controller.current_session.sections), 8)
        
        # Check that session file was created
        self.assertTrue(self.controller.current_session_file.exists())
    
    def test_load_existing_session(self):
        """Test loading an existing session."""
        # First create a session
        self.controller.create_new_session()
        original_session_id = self.controller.current_session.session_id
        
        # Clear current session and reload
        self.controller.current_session = None
        success, message = self.controller.load_existing_session()
        
        self.assertTrue(success)
        self.assertIn("Session loaded", message)
        self.assertEqual(self.controller.current_session.session_id, original_session_id)
    
    def test_load_nonexistent_session(self):
        """Test loading when no session exists."""
        success, message = self.controller.load_existing_session()
        
        self.assertFalse(success)
        self.assertIn("No existing session found", message)
    
    @patch('antigine.core.agents.gdd_creator.lite_model')
    def test_generate_questions(self, mock_llm):
        """Test atomic question generation operation."""
        # Mock LLM response with formatted questions
        mock_response = Mock()
        mock_response.content = """1. What is the main concept of your game?
2. Who is your target audience?
3. What makes your game unique?"""
        mock_llm.invoke.return_value = mock_response
        
        questions = self.controller._generate_questions(1, "Test context")
        
        self.assertEqual(len(questions), 3)
        self.assertIn("main concept", questions[0])
        self.assertIn("target audience", questions[1])
        self.assertIn("unique", questions[2])
        
        # Verify LLM was called with proper prompt
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        self.assertIn("Core Vision", call_args)
        self.assertIn("Love2D/Lua", call_args)
    
    @patch('antigine.core.agents.gdd_creator.lite_model')
    def test_evaluate_response_completeness_complete(self, mock_llm):
        """Test response evaluation when complete."""
        # Mock LLM response indicating completion
        mock_response = Mock()
        mock_response.content = """COMPLETE: Yes
REASON: All criteria have been adequately addressed."""
        mock_llm.invoke.return_value = mock_response
        
        is_complete, reason = self.controller._evaluate_response_completeness(
            1, "My game is a platformer for teenagers...", []
        )
        
        self.assertTrue(is_complete)
        self.assertIn("adequately addressed", reason)
    
    @patch('antigine.core.agents.gdd_creator.lite_model')
    def test_evaluate_response_completeness_incomplete(self, mock_llm):
        """Test response evaluation when incomplete."""
        # Mock LLM response indicating incompleteness
        mock_response = Mock()
        mock_response.content = """COMPLETE: No
REASON: Missing target audience definition."""
        mock_llm.invoke.return_value = mock_response
        
        is_complete, reason = self.controller._evaluate_response_completeness(
            1, "My game is a platformer...", []
        )
        
        self.assertFalse(is_complete)
        self.assertIn("Missing target audience", reason)
    
    @patch('antigine.core.agents.gdd_creator.lite_model')
    def test_structure_section_content(self, mock_llm):
        """Test atomic content structuring operation."""
        # Mock LLM response with structured content
        mock_response = Mock()
        mock_response.content = """# Core Vision

## Game Concept
A 2D platformer for teenagers...

## Target Audience
13-19 year olds who enjoy challenging games..."""
        mock_llm.invoke.return_value = mock_response
        
        user_responses = ["My game is a platformer", "Target audience is teenagers"]
        structured = self.controller._structure_section_content(1, user_responses)
        
        self.assertIn("raw_content", structured)
        self.assertIn("user_responses", structured)
        self.assertIn("structured_at", structured)
        self.assertEqual(structured["user_responses"], user_responses)
        self.assertIn("Game Concept", structured["raw_content"])
    
    def test_start_section(self):
        """Test starting a specific section."""
        # Create session first
        self.controller.create_new_session()
        
        with patch.object(self.controller, '_generate_questions') as mock_gen_q:
            mock_gen_q.return_value = ["Question 1", "Question 2"]
            
            success, message, questions = self.controller.start_section(1)
            
            self.assertTrue(success)
            self.assertIn("Started section 1", message)
            self.assertEqual(len(questions), 2)
            
            # Check that section status was updated
            section = self.controller.current_session.sections[1]
            self.assertEqual(section.status, SectionStatus.IN_PROGRESS)
            self.assertIsNotNone(section.started_at)
    
    def test_start_invalid_section(self):
        """Test starting an invalid section number."""
        self.controller.create_new_session()
        
        success, message, questions = self.controller.start_section(10)
        
        self.assertFalse(success)
        self.assertIn("Invalid section number", message)
        self.assertEqual(questions, [])
    
    def test_start_completed_section(self):
        """Test starting an already completed section."""
        self.controller.create_new_session()
        
        # Mark section as completed
        section = self.controller.current_session.sections[1]
        section.status = SectionStatus.COMPLETED
        
        success, message, questions = self.controller.start_section(1)
        
        self.assertFalse(success)
        self.assertIn("already completed", message)
        self.assertEqual(questions, [])
    
    def test_process_user_response_section_complete(self):
        """Test processing user response that completes a section."""
        self.controller.create_new_session()
        self.controller.start_section(1)
        
        with patch.object(self.controller, '_evaluate_response_completeness') as mock_eval, \
             patch.object(self.controller, '_structure_section_content') as mock_struct:
            
            mock_eval.return_value = (True, "Section is complete")
            mock_struct.return_value = {"raw_content": "Structured content"}
            
            success, feedback, next_questions = self.controller.process_user_response("Detailed response")
            
            self.assertTrue(success)
            self.assertIn("Section 1 completed", feedback)
            self.assertIsNone(next_questions)
            
            # Check that section was marked as completed
            section = self.controller.current_session.sections[1]
            self.assertEqual(section.status, SectionStatus.COMPLETED)
            self.assertIsNotNone(section.completed_at)
    
    def test_process_user_response_needs_more_info(self):
        """Test processing user response that needs more information."""
        self.controller.create_new_session()
        self.controller.start_section(1)
        
        with patch.object(self.controller, '_evaluate_response_completeness') as mock_eval, \
             patch.object(self.controller, '_generate_questions') as mock_gen_q:
            
            mock_eval.return_value = (False, "Need more details about target audience")
            mock_gen_q.return_value = ["Follow-up question 1", "Follow-up question 2"]
            
            success, feedback, next_questions = self.controller.process_user_response("Brief response")
            
            self.assertTrue(success)  
            self.assertIn("Need more details", feedback)
            self.assertEqual(len(next_questions), 2)
            
            # Check that section is still in progress
            section = self.controller.current_session.sections[1]
            self.assertEqual(section.status, SectionStatus.IN_PROGRESS)
    
    def test_all_sections_completed(self):
        """Test checking if all sections are completed."""
        self.controller.create_new_session()
        
        # Initially, no sections are completed
        self.assertFalse(self.controller._all_sections_completed())
        
        # Mark all sections as completed
        for section in self.controller.current_session.sections.values():
            section.status = SectionStatus.COMPLETED
        
        self.assertTrue(self.controller._all_sections_completed())
    
    def test_build_context_summary(self):
        """Test building context summary from completed sections."""
        self.controller.create_new_session()
        
        # Add some game context
        self.controller.current_session.game_context = {
            "core_vision": "A platformer game for teenagers"
        }
        
        # Mark first section as completed
        self.controller.current_session.sections[1].status = SectionStatus.COMPLETED
        self.controller.current_session.current_section = 2
        
        context = self.controller._build_context_summary()
        
        self.assertIn("GAME CONTEXT", context)
        self.assertIn("core_vision", context)
        self.assertIn("COMPLETED SECTIONS", context)
        self.assertIn("Section 1", context)
    
    def test_update_game_context(self):
        """Test updating game context with section content."""
        self.controller.create_new_session()
        
        structured_content = {
            "raw_content": "This is a detailed core vision for the game that explains the main concept and design pillars in great detail for testing purposes."
        }
        
        self.controller._update_game_context(1, structured_content)
        
        self.assertIn("core_vision", self.controller.current_session.game_context)
        # Should be truncated to 200 characters + "..."
        self.assertTrue(len(self.controller.current_session.game_context["core_vision"]) <= 203)
    
    def test_get_session_status(self):
        """Test getting session status information."""
        self.controller.create_new_session()
        
        # Mark one section as completed
        self.controller.current_session.sections[1].status = SectionStatus.COMPLETED
        
        status = self.controller.get_session_status()
        
        self.assertIn("session_id", status)
        self.assertIn("current_section", status)
        self.assertIn("completed_sections", status)
        self.assertIn("total_sections", status)
        self.assertIn("completion_percentage", status)
        self.assertEqual(status["completed_sections"], 1)
        self.assertEqual(status["total_sections"], 8)
        self.assertEqual(status["completion_percentage"], 12.5)
    
    def test_get_current_section_info(self):
        """Test getting current section information."""
        self.controller.create_new_session()
        self.controller.start_section(1)
        
        info = self.controller.get_current_section_info()
        
        self.assertEqual(info["section_number"], 1)
        self.assertEqual(info["name"], "Core Vision")
        self.assertIn("description", info)
        self.assertIn("criteria", info)
        self.assertEqual(info["status"], "in_progress")
    
    def test_get_next_section_preview(self):
        """Test getting next section preview."""
        self.controller.create_new_session()
        
        preview = self.controller.get_next_section_preview()
        
        self.assertEqual(preview["section_number"], 2)
        self.assertEqual(preview["name"], "MDA Breakdown")
        self.assertIn("description", preview)
    
    def test_get_next_section_preview_final_section(self):
        """Test getting next section preview when on final section."""
        self.controller.create_new_session()
        self.controller.current_session.current_section = 8
        
        preview = self.controller.get_next_section_preview()
        
        self.assertIsNone(preview)
    
    def test_generate_final_gdd_not_complete(self):
        """Test generating final GDD when not complete."""
        self.controller.create_new_session()
        
        success, message = self.controller.generate_final_gdd()
        
        self.assertFalse(success)
        self.assertIn("not completed yet", message)
    
    @patch('antigine.core.agents.gdd_creator.GDDManager')
    def test_generate_final_gdd_complete(self, mock_gdd_manager_class):
        """Test generating final GDD when complete."""
        # Setup mocks
        mock_gdd_manager = Mock()
        mock_gdd_manager.create_gdd.return_value = (True, "GDD saved successfully")
        mock_gdd_manager_class.return_value = mock_gdd_manager
        
        self.controller.create_new_session()
        
        # Mark session as completed and add content to sections
        self.controller.current_session.is_completed = True
        for section in self.controller.current_session.sections.values():
            section.status = SectionStatus.COMPLETED
            section.structured_content = {"raw_content": f"Content for {section.name}"}
        
        success, message = self.controller.generate_final_gdd()
        
        self.assertTrue(success)
        self.assertIn("Final GDD generated successfully", message)
        
        # Verify GDD Manager was called
        mock_gdd_manager.create_gdd.assert_called_once()
        call_args = mock_gdd_manager.create_gdd.call_args[0][0]
        self.assertIn("# Game Design Document", call_args)
        self.assertIn("Core Vision", call_args)
    
    def test_session_persistence(self):
        """Test that sessions are properly saved and loaded."""
        # Create and modify session
        self.controller.create_new_session()
        original_session_id = self.controller.current_session.session_id
        
        # Start a section and add some data
        self.controller.start_section(1)
        section = self.controller.current_session.sections[1]
        section.user_responses.append("Test response")
        self.controller._save_session()
        
        # Create new controller and load session
        with patch('antigine.core.agents.gdd_creator.lite_model'):
            new_controller = GDDController(str(self.project_root))
            success, message = new_controller.load_existing_session()
        
        self.assertTrue(success)
        self.assertEqual(new_controller.current_session.session_id, original_session_id)
        self.assertEqual(len(new_controller.current_session.sections[1].user_responses), 1)
        self.assertEqual(new_controller.current_session.sections[1].user_responses[0], "Test response")
    
    def test_section_data_structure(self):
        """Test that SectionData structure is properly maintained."""
        self.controller.create_new_session()
        section = self.controller.current_session.sections[1]
        
        # Test all required fields exist
        self.assertEqual(section.number, 1)
        self.assertEqual(section.name, "Core Vision")
        self.assertIsInstance(section.criteria, list)
        self.assertEqual(section.status, SectionStatus.NOT_STARTED)
        self.assertIsInstance(section.questions_asked, list)
        self.assertIsInstance(section.user_responses, list)
        self.assertIsInstance(section.structured_content, dict)
    
    def test_error_handling_llm_failure(self):
        """Test error handling when LLM calls fail."""
        self.controller.create_new_session()
        
        with patch.object(self.controller, '_generate_questions') as mock_gen_q:
            mock_gen_q.side_effect = Exception("LLM API error")
            
            # Should fall back gracefully
            questions = self.controller._generate_questions(1)
            self.assertEqual(len(questions), 1)
            self.assertIn("key aspects", questions[0])


if __name__ == '__main__':
    unittest.main()