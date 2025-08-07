"""
test_feature_request_agent.py
##############################

Unit tests for FeatureRequestAgent utility methods that can be tested without external dependencies.
Tests core string processing and prompt building functions.
"""

import unittest
from antigine.core.agents.feature_request_agent import FeatureRequestAgent


class TestFeatureRequestAgent(unittest.TestCase):
    """Test cases for FeatureRequestAgent utility methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create agent instance for testing utility methods
        # Use dummy paths since we're not testing LangGraph workflow
        self.agent = FeatureRequestAgent("/tmp/dummy", "/tmp/dummy.db")
    
    def test_clean_json_response_plain_json(self):
        """Test JSON response cleaning with plain JSON."""
        response = '{"is_complete": true, "confidence_score": 0.8}'
        
        cleaned = self.agent._clean_json_response(response)
        
        self.assertEqual(cleaned, '{"is_complete": true, "confidence_score": 0.8}')
    
    def test_clean_json_response_with_markdown(self):
        """Test JSON response cleaning with markdown formatting."""
        response = '```json\n{"is_complete": false, "issues": ["missing details"]}\n```'
        
        cleaned = self.agent._clean_json_response(response)
        
        self.assertEqual(cleaned, '{"is_complete": false, "issues": ["missing details"]}')
    
    def test_clean_json_response_with_whitespace(self):
        """Test JSON response cleaning with extra whitespace."""
        response = '  \n```json\n  {"confidence_score": 0.9}  \n```  \n'
        
        cleaned = self.agent._clean_json_response(response)
        
        self.assertEqual(cleaned, '{"confidence_score": 0.9}')
    
    def test_clean_json_response_only_start_markdown(self):
        """Test JSON response cleaning with only start markdown."""
        response = '```json\n{"is_complete": true}'
        
        cleaned = self.agent._clean_json_response(response)
        
        self.assertEqual(cleaned, '{"is_complete": true}')
    
    def test_clean_json_response_only_end_markdown(self):
        """Test JSON response cleaning with only end markdown."""
        response = '{"confidence_score": 0.7}\n```'
        
        cleaned = self.agent._clean_json_response(response)
        
        self.assertEqual(cleaned, '{"confidence_score": 0.7}')
    
    def test_build_validation_prompt_basic(self):
        """Test validation prompt building with basic inputs."""
        title = "Add player movement"
        description = "Implement WASD movement controls for the player character"
        feature_type = "new_feature"
        gdd_context = ""
        
        prompt = self.agent._build_validation_prompt(title, description, feature_type, gdd_context)
        
        # Check key components are present
        self.assertIn("senior game developer", prompt)
        self.assertIn("FEATURE TYPE: new_feature", prompt)
        self.assertIn("FEATURE TITLE: Add player movement", prompt)
        self.assertIn("WASD movement controls", prompt)
        self.assertIn("JSON format", prompt)
        self.assertIn("is_complete", prompt)
        self.assertIn("confidence_score", prompt)
    
    def test_build_validation_prompt_with_gdd(self):
        """Test validation prompt building with GDD context."""
        title = "Add combat system"
        description = "Create turn-based combat mechanics"
        feature_type = "new_feature"
        gdd_context = "This is a turn-based RPG with fantasy elements..."
        
        prompt = self.agent._build_validation_prompt(title, description, feature_type, gdd_context)
        
        # Check GDD context is included
        self.assertIn("GAME DESIGN DOCUMENT CONTEXT:", prompt)
        self.assertIn("turn-based RPG with fantasy", prompt)
        self.assertIn("Create turn-based combat", prompt)
    
    def test_build_validation_prompt_different_feature_types(self):
        """Test validation prompt building with different feature types."""
        base_title = "Test feature"
        base_description = "Test description"
        gdd_context = ""
        
        for feature_type in ["bug_fix", "enhancement", "refactor"]:
            prompt = self.agent._build_validation_prompt(
                base_title, base_description, feature_type, gdd_context
            )
            
            self.assertIn(f"FEATURE TYPE: {feature_type}", prompt)
            self.assertIn("Functional requirements clarity", prompt)
            self.assertIn("Technical constraints mentioned", prompt)


class TestSemanticSearchRelationshipClassification(unittest.TestCase):
    """Test cases for semantic search relationship classification."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use dummy project root since we're not testing ChromaDB functionality
        from antigine.core.semantic_search import SemanticSearchEngine
        self.engine = SemanticSearchEngine("/tmp/dummy")
    
    def test_classify_relationship_high_similarity_duplicate(self):
        """Test relationship classification for high similarity features."""
        text1 = "Add player movement controls"
        text2 = "Implement player movement system"
        similarity_score = 0.95
        
        relationship = self.engine._classify_relationship(text1, text2, similarity_score)
        
        self.assertEqual(relationship, "duplicate")
    
    def test_classify_relationship_enhancement_keywords(self):
        """Test relationship classification with enhancement keywords."""
        text1 = "Improve player movement with better physics"
        text2 = "Enhance movement system with advanced controls"
        similarity_score = 0.85
        
        relationship = self.engine._classify_relationship(text1, text2, similarity_score)
        
        self.assertEqual(relationship, "builds_on")
    
    def test_classify_relationship_fix_keywords(self):
        """Test relationship classification with fix keywords."""
        text1 = "Fix player movement bug where character gets stuck"
        text2 = "Player movement system implementation"
        similarity_score = 0.75
        
        relationship = self.engine._classify_relationship(text1, text2, similarity_score)
        
        self.assertEqual(relationship, "fixes")
    
    def test_classify_relationship_moderate_similarity(self):
        """Test relationship classification with moderate similarity."""
        text1 = "Add player jump ability"
        text2 = "Implement player movement controls"
        similarity_score = 0.82
        
        relationship = self.engine._classify_relationship(text1, text2, similarity_score)
        
        self.assertEqual(relationship, "builds_on")
    
    def test_classify_relationship_low_similarity(self):
        """Test relationship classification with low similarity."""
        text1 = "Add sound effects"
        text2 = "Implement player movement"
        similarity_score = 0.3
        
        relationship = self.engine._classify_relationship(text1, text2, similarity_score)
        
        self.assertIsNone(relationship)
    
    def test_classify_relationship_edge_cases(self):
        """Test relationship classification edge cases."""
        text1 = "Test feature"
        text2 = "Another feature"
        
        # Test boundary conditions
        self.assertEqual(
            self.engine._classify_relationship(text1, text2, 0.9), 
            "duplicate"
        )
        
        self.assertEqual(
            self.engine._classify_relationship(text1, text2, 0.8), 
            "builds_on"
        )
        
        self.assertIsNone(
            self.engine._classify_relationship(text1, text2, 0.7)
        )


if __name__ == '__main__':
    unittest.main()