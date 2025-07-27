"""
test_tech_stacks.py
##################

Unit tests for tech stack parsing and validation functionality.
Tests the core logic of TechStackManager without side effects.
"""

import unittest
from antigine.core.tech_stacks import TechStackManager, LibraryCategory


class TestTechStackManager(unittest.TestCase):
    """Test cases for TechStackManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TechStackManager()
    
    def test_parse_single_library_valid(self):
        """Test parsing a single valid library."""
        analysis = self.manager.parse_tech_stack("Love2D", "Lua")
        
        self.assertEqual(analysis.language, "Lua")
        self.assertEqual(len(analysis.libraries), 1)
        self.assertEqual(analysis.libraries[0].name, "Love2D")
        self.assertIn("Love2D", analysis.documentation_urls)
        self.assertEqual(len(analysis.unsupported_libraries), 0)
    
    def test_parse_multiple_libraries_valid(self):
        """Test parsing multiple valid libraries."""
        analysis = self.manager.parse_tech_stack("SDL2+OpenGL+GLM", "C++")
        
        self.assertEqual(analysis.language, "C++")
        self.assertEqual(len(analysis.libraries), 3)
        
        lib_names = [lib.name for lib in analysis.libraries]
        self.assertIn("SDL2", lib_names)
        self.assertIn("OpenGL", lib_names)
        self.assertIn("GLM", lib_names)
        
        # Check documentation URLs are present
        self.assertIn("SDL2", analysis.documentation_urls)
        self.assertIn("OpenGL", analysis.documentation_urls)
        self.assertIn("GLM", analysis.documentation_urls)
        
        self.assertEqual(len(analysis.unsupported_libraries), 0)
    
    def test_parse_unknown_library(self):
        """Test parsing with unknown library."""
        analysis = self.manager.parse_tech_stack("SDL2+UnknownLib+GLM", "C++")
        
        self.assertEqual(len(analysis.libraries), 2)  # SDL2 and GLM
        self.assertEqual(len(analysis.unsupported_libraries), 1)
        self.assertIn("UnknownLib (unknown library)", analysis.unsupported_libraries[0])
    
    def test_parse_language_incompatible(self):
        """Test parsing with language-incompatible library."""
        analysis = self.manager.parse_tech_stack("Love2D+GLM", "C++")
        
        # GLM should be accepted (C++ compatible)
        # Love2D should be rejected (Lua only)
        self.assertEqual(len(analysis.libraries), 1)
        self.assertEqual(analysis.libraries[0].name, "GLM")
        
        self.assertEqual(len(analysis.unsupported_libraries), 1)
        self.assertIn("Love2D", analysis.unsupported_libraries[0])
        self.assertIn("not compatible with C++", analysis.unsupported_libraries[0])
    
    def test_parse_conflicting_libraries(self):
        """Test parsing with conflicting libraries."""
        analysis = self.manager.parse_tech_stack("OpenGL+Vulkan", "C++")
        
        # Both should be parsed as valid libraries
        self.assertEqual(len(analysis.libraries), 2)
        
        # But conflicts should be detected
        self.assertGreater(len(analysis.conflicts), 0)
        self.assertTrue(any("OpenGL" in conflict and "Vulkan" in conflict 
                          for conflict in analysis.conflicts))
    
    def test_parse_empty_tech_stack(self):
        """Test parsing empty tech stack."""
        analysis = self.manager.parse_tech_stack("", "C++")
        
        self.assertEqual(len(analysis.libraries), 0)
        self.assertEqual(len(analysis.unsupported_libraries), 1)  # Empty string counts as unknown
    
    def test_parse_whitespace_handling(self):
        """Test parsing with extra whitespace."""
        analysis = self.manager.parse_tech_stack(" SDL2 + OpenGL + GLM ", "C++")
        
        self.assertEqual(len(analysis.libraries), 3)
        lib_names = [lib.name for lib in analysis.libraries]
        self.assertIn("SDL2", lib_names)
        self.assertIn("OpenGL", lib_names)
        self.assertIn("GLM", lib_names)
    
    def test_get_available_libraries_all(self):
        """Test getting all available libraries."""
        libraries = self.manager.get_available_libraries()
        
        self.assertIsInstance(libraries, dict)
        self.assertGreater(len(libraries), 0)
        
        # Check some expected libraries are present
        self.assertIn("Love2D", libraries)
        self.assertIn("SDL2", libraries)
        self.assertIn("OpenGL", libraries)
    
    def test_get_available_libraries_by_language(self):
        """Test getting libraries filtered by language."""
        cpp_libraries = self.manager.get_available_libraries("C++")
        lua_libraries = self.manager.get_available_libraries("Lua")
        
        # C++ should have many libraries
        self.assertGreater(len(cpp_libraries), 3)
        self.assertIn("SDL2", cpp_libraries)
        self.assertIn("OpenGL", cpp_libraries)
        
        # Lua should have fewer libraries
        self.assertGreaterEqual(len(lua_libraries), 1)
        self.assertIn("Love2D", lua_libraries)
        
        # Love2D should not be in C++ libraries
        self.assertNotIn("Love2D", cpp_libraries)
    
    def test_search_libraries_by_category(self):
        """Test searching libraries by category."""
        frameworks = self.manager.search_libraries(category=LibraryCategory.FRAMEWORK)
        rendering = self.manager.search_libraries(category=LibraryCategory.RENDERING)
        
        # Framework category should include Love2D, Pygame
        framework_names = list(frameworks.keys())
        self.assertIn("Love2D", framework_names)
        self.assertIn("Pygame", framework_names)
        
        # Rendering category should include OpenGL, Vulkan
        rendering_names = list(rendering.keys())
        self.assertIn("OpenGL", rendering_names)
    
    def test_search_libraries_by_search_term(self):
        """Test searching libraries by search term."""
        opengl_results = self.manager.search_libraries(search_term="OpenGL")
        
        # Should find OpenGL and GLM (OpenGL Mathematics)
        result_names = list(opengl_results.keys())
        self.assertIn("OpenGL", result_names)
        self.assertIn("GLM", result_names)  # Contains "OpenGL" in description
    
    def test_search_libraries_combined_filters(self):
        """Test searching with multiple filters."""
        cpp_frameworks = self.manager.search_libraries(
            language="C++", 
            category=LibraryCategory.FRAMEWORK
        )
        
        # Should be empty or very few since most C++ libs aren't full frameworks
        # This tests the filtering logic works correctly
        for lib_info in cpp_frameworks.values():
            self.assertIn("C++", lib_info.languages)
            self.assertEqual(lib_info.category, LibraryCategory.FRAMEWORK)
    
    def test_generate_warnings_missing_windowing(self):
        """Test warning generation for missing windowing library."""
        analysis = self.manager.parse_tech_stack("OpenGL", "C++")
        
        # Should warn about missing windowing library
        self.assertGreater(len(analysis.warnings), 0)
        self.assertTrue(any("windowing" in warning.lower() for warning in analysis.warnings))
    
    def test_generate_warnings_missing_math(self):
        """Test warning generation for missing math library."""
        analysis = self.manager.parse_tech_stack("Bullet", "C++")
        
        # Should warn about missing math library for physics
        self.assertGreater(len(analysis.warnings), 0)
        self.assertTrue(any("math" in warning.lower() for warning in analysis.warnings))
    
    def test_suggestions_for_rendering_stack(self):
        """Test suggestions for rendering-heavy stacks."""
        analysis = self.manager.parse_tech_stack("SDL2+OpenGL", "C++")
        
        # Should suggest asset loading libraries
        self.assertGreater(len(analysis.suggested_additions), 0)
        suggestions_text = " ".join(analysis.suggested_additions).lower()
        self.assertTrue("assimp" in suggestions_text or "stb_image" in suggestions_text)


class TestLibraryDatabase(unittest.TestCase):
    """Test cases for the library database content."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TechStackManager()
        self.db = self.manager.library_db
    
    def test_all_libraries_have_required_fields(self):
        """Test that all libraries have required metadata fields."""
        for lib_name, lib_info in self.db.items():
            with self.subTest(library=lib_name):
                # Required fields
                self.assertIsNotNone(lib_info.name)
                self.assertIsNotNone(lib_info.display_name)
                self.assertIsNotNone(lib_info.description)
                self.assertIsNotNone(lib_info.category)
                self.assertIsInstance(lib_info.languages, list)
                self.assertGreater(len(lib_info.languages), 0)
                
                # Documentation URLs
                self.assertIsNotNone(lib_info.documentation_url)
                self.assertIsNotNone(lib_info.api_reference_url)
                self.assertIsNotNone(lib_info.examples_url)
                
                # URLs should be valid format (basic check)
                self.assertTrue(lib_info.documentation_url.startswith(("http://", "https://")))
                self.assertTrue(lib_info.api_reference_url.startswith(("http://", "https://")))
                self.assertTrue(lib_info.examples_url.startswith(("http://", "https://")))
    
    def test_known_libraries_present(self):
        """Test that expected libraries are present in database."""
        expected_libraries = [
            "Love2D", "Pygame", "SDL2", "GLFW", "OpenGL", "Vulkan",
            "GLM", "NumPy", "Bullet", "Box2D", "Assimp", "stb_image", "Dear ImGui"
        ]
        
        for lib_name in expected_libraries:
            with self.subTest(library=lib_name):
                self.assertIn(lib_name, self.db, f"Library {lib_name} not found in database")
    
    def test_language_consistency(self):
        """Test that language assignments are consistent."""
        # Check specific known language assignments
        self.assertIn("Lua", self.db["Love2D"].languages)
        self.assertIn("Python", self.db["Pygame"].languages)
        self.assertIn("C++", self.db["SDL2"].languages)
        self.assertIn("C++", self.db["OpenGL"].languages)
        self.assertIn("C++", self.db["GLM"].languages)
    
    def test_category_assignments(self):
        """Test that category assignments are logical."""
        self.assertEqual(self.db["Love2D"].category, LibraryCategory.FRAMEWORK)
        self.assertEqual(self.db["Pygame"].category, LibraryCategory.FRAMEWORK)
        self.assertEqual(self.db["SDL2"].category, LibraryCategory.WINDOWING)
        self.assertEqual(self.db["OpenGL"].category, LibraryCategory.RENDERING)
        self.assertEqual(self.db["GLM"].category, LibraryCategory.MATH)
        self.assertEqual(self.db["Bullet"].category, LibraryCategory.PHYSICS)
        self.assertEqual(self.db["Assimp"].category, LibraryCategory.ASSETS)


if __name__ == "__main__":
    unittest.main()