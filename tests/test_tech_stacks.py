"""
test_tech_stacks.py
##################

Unit tests for tech stack parsing and validation functionality.
Tests the core logic of TechStackManager without side effects.
"""

import unittest
from antigine.core.tech_stacks import (
    TechStackManager, 
    LibraryCategory, 
    get_default_tech_stack, 
    resolve_tech_stack_name
)


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
        self.assertTrue(any("OpenGL" in conflict and "Vulkan" in conflict for conflict in analysis.conflicts))

    def test_parse_empty_tech_stack(self):
        """Test parsing empty tech stack raises appropriate error."""
        with self.assertRaises(ValueError) as context:
            self.manager.parse_tech_stack("", "C++")
        self.assertIn("cannot be None or empty", str(context.exception))

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
        cpp_frameworks = self.manager.search_libraries(language="C++", category=LibraryCategory.FRAMEWORK)

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
            "Love2D",
            "Pygame",
            "SDL2",
            "GLFW",
            "OpenGL",
            "Vulkan",
            "GLM",
            "NumPy",
            "Bullet",
            "Box2D",
            "Assimp",
            "stb_image",
            "Dear ImGui",
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

    def test_input_validation_none_or_empty(self):
        """Test input validation for None or empty strings."""
        with self.assertRaises(ValueError) as context:
            self.manager.parse_tech_stack("", "C++")
        self.assertIn("cannot be None or empty", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.manager.parse_tech_stack(None, "C++")
        self.assertIn("cannot be None or empty", str(context.exception))

    def test_input_validation_wrong_type(self):
        """Test input validation for non-string types."""
        with self.assertRaises(TypeError) as context:
            self.manager.parse_tech_stack(123, "C++")
        self.assertIn("must be a string", str(context.exception))

        with self.assertRaises(TypeError) as context:
            self.manager.parse_tech_stack(["SDL2"], "C++")
        self.assertIn("must be a string", str(context.exception))

    def test_input_validation_whitespace_only(self):
        """Test input validation for whitespace-only strings."""
        with self.assertRaises(ValueError) as context:
            self.manager.parse_tech_stack("   ", "C++")
        self.assertIn("cannot be empty or contain only whitespace", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.manager.parse_tech_stack("\t\n", "C++")
        self.assertIn("cannot be empty or contain only whitespace", str(context.exception))

    def test_input_validation_only_delimiters(self):
        """Test input validation for strings with only delimiter characters."""
        with self.assertRaises(ValueError) as context:
            self.manager.parse_tech_stack("+++", "C++")
        self.assertIn("cannot contain only delimiter characters", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.manager.parse_tech_stack("+", "C++")
        self.assertIn("cannot contain only delimiter characters", str(context.exception))

    def test_input_validation_no_valid_libraries(self):
        """Test input validation when no valid library names can be extracted."""
        with self.assertRaises(ValueError) as context:
            self.manager.parse_tech_stack("+ + +", "C++")
        self.assertIn("No valid library names found", str(context.exception))

    def test_input_validation_edge_cases_success(self):
        """Test that edge cases with valid content still work."""
        # Leading/trailing delimiters should be handled
        analysis = self.manager.parse_tech_stack("+SDL2+", "C++")
        self.assertEqual(len(analysis.libraries), 1)
        self.assertEqual(analysis.libraries[0].name, "SDL2")

        # Multiple consecutive delimiters should be handled
        analysis = self.manager.parse_tech_stack("SDL2++OpenGL", "C++")
        self.assertEqual(len(analysis.libraries), 2)
        self.assertEqual(analysis.libraries[0].name, "SDL2")
        self.assertEqual(analysis.libraries[1].name, "OpenGL")

        # Whitespace around library names should be handled
        analysis = self.manager.parse_tech_stack(" SDL2 + OpenGL ", "C++")
        self.assertEqual(len(analysis.libraries), 2)
        self.assertEqual(analysis.libraries[0].name, "SDL2")
        self.assertEqual(analysis.libraries[1].name, "OpenGL")

    def test_build_config_generation_cpp(self):
        """Test build configuration generation for C++ projects."""
        # Test default configuration
        analysis = self.manager.parse_tech_stack("SDL2+OpenGL", "C++")
        self.assertIsNotNone(analysis.build_config)
        self.assertEqual(analysis.build_config.cmake_minimum_version, "3.16")
        self.assertEqual(analysis.build_config.cmake_cxx_standard, "17")
        self.assertIn("widely available", analysis.build_config.cmake_version_reason)

    def test_build_config_generation_vulkan(self):
        """Test build configuration for Vulkan projects requires newer CMake."""
        analysis = self.manager.parse_tech_stack("Vulkan", "C++")
        self.assertIsNotNone(analysis.build_config)
        self.assertEqual(analysis.build_config.cmake_minimum_version, "3.21")
        self.assertIn("Vulkan support", analysis.build_config.cmake_version_reason)

    def test_build_config_generation_complex_libs(self):
        """Test build configuration for complex libraries."""
        analysis = self.manager.parse_tech_stack("SDL2+OpenGL+Assimp+Bullet", "C++")
        self.assertIsNotNone(analysis.build_config)
        self.assertEqual(analysis.build_config.cmake_minimum_version, "3.18")
        self.assertIn("modern C++ libraries", analysis.build_config.cmake_version_reason)

    def test_build_config_generation_python(self):
        """Test that build configuration is not generated for Python projects."""
        analysis = self.manager.parse_tech_stack("Pygame", "Python")
        self.assertIsNone(analysis.build_config)


class TestTechStackAliases(unittest.TestCase):
    """Tests for tech stack aliases and default configurations."""

    def test_get_default_tech_stack(self):
        """Test getting default tech stacks for different languages."""
        self.assertEqual(get_default_tech_stack("Lua"), "Love2D")
        self.assertEqual(get_default_tech_stack("Python"), "Pygame")
        self.assertEqual(get_default_tech_stack("C++"), "SDL2+OpenGL")
        self.assertEqual(get_default_tech_stack("C"), "SDL2")

    def test_get_default_tech_stack_unknown_language(self):
        """Test that unknown languages raise appropriate error."""
        with self.assertRaises(ValueError) as context:
            get_default_tech_stack("Unknown")
        self.assertIn("No default tech stack configured", str(context.exception))

    def test_resolve_tech_stack_name_single_alias(self):
        """Test resolving single tech stack aliases."""
        self.assertEqual(resolve_tech_stack_name("love2d"), "Love2D")
        self.assertEqual(resolve_tech_stack_name("pygame"), "Pygame")
        self.assertEqual(resolve_tech_stack_name("sdl2"), "SDL2")
        self.assertEqual(resolve_tech_stack_name("opengl"), "OpenGL")

    def test_resolve_tech_stack_name_multi_library(self):
        """Test resolving multi-library tech stacks with aliases."""
        # Test combination with aliases
        result = resolve_tech_stack_name("sdl2+opengl")
        self.assertEqual(result, "SDL2+OpenGL")

        # Test mixed case with whitespace
        result = resolve_tech_stack_name("sdl2 + opengl")
        self.assertEqual(result, "SDL2+OpenGL")

    def test_resolve_tech_stack_name_no_alias(self):
        """Test that unknown names are returned as-is."""
        self.assertEqual(resolve_tech_stack_name("CustomLib"), "CustomLib")
        self.assertEqual(resolve_tech_stack_name("SDL2+CustomLib"), "SDL2+CustomLib")


if __name__ == "__main__":
    unittest.main()
