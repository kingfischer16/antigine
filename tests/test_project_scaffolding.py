"""
test_project_scaffolding.py
###########################

Unit tests for project scaffolding functionality.
Tests folder structure generation and file content creation logic.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from antigine.core.project_scaffolding import ProjectScaffolder
from antigine.core.tech_stacks import TechStackManager


class TestProjectScaffolder(unittest.TestCase):
    """Test cases for ProjectScaffolder functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.scaffolder = ProjectScaffolder()
        self.tech_stack_manager = TechStackManager()

    def test_determine_folder_structure_love2d(self):
        """Test folder structure for Love2D projects."""
        analysis = self.tech_stack_manager.parse_tech_stack("Love2D", "Lua")
        folders = self.scaffolder._determine_folder_structure(analysis)

        # Love2D should have 2D-specific folders
        self.assertIn("assets/sprites", folders)
        self.assertIn("assets/images", folders)
        self.assertIn("assets/audio", folders)
        self.assertIn("src", folders)

        # Should NOT have 3D-specific folders
        self.assertNotIn("assets/models", folders)
        self.assertNotIn("assets/materials", folders)
        self.assertNotIn("assets/shaders", folders)

    def test_determine_folder_structure_pygame(self):
        """Test folder structure for Pygame projects."""
        analysis = self.tech_stack_manager.parse_tech_stack("Pygame", "Python")
        folders = self.scaffolder._determine_folder_structure(analysis)

        # Pygame should have 2D-specific folders
        self.assertIn("assets/sprites", folders)
        self.assertIn("assets/images", folders)
        self.assertIn("src", folders)

        # Should NOT have 3D-specific folders
        self.assertNotIn("assets/models", folders)
        self.assertNotIn("assets/materials", folders)

    def test_determine_folder_structure_3d_stack(self):
        """Test folder structure for 3D tech stacks."""
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2+OpenGL+GLM+Assimp", "C++")
        folders = self.scaffolder._determine_folder_structure(analysis)

        # 3D stack should have 3D-specific folders
        self.assertIn("assets/models", folders)
        self.assertIn("assets/materials", folders)
        self.assertIn("assets/textures", folders)
        self.assertIn("assets/shaders", folders)
        self.assertIn("src", folders)
        self.assertIn("include", folders)

        # Should also have general asset folders
        self.assertIn("assets/textures", folders)

    def test_determine_folder_structure_mixed_2d_3d(self):
        """Test folder structure for mixed 2D/3D stacks."""
        # SDL2 + OpenGL could be used for 2D or 3D
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2+OpenGL", "C++")
        folders = self.scaffolder._determine_folder_structure(analysis)

        # Should have both 2D and 3D folders since OpenGL can do both
        self.assertIn("assets/textures", folders)
        self.assertIn("assets/shaders", folders)  # OpenGL always needs shaders
        self.assertIn("src", folders)
        self.assertIn("include", folders)

    def test_determine_folder_structure_no_duplicates(self):
        """Test that folder structure has no duplicates."""
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2+OpenGL+Assimp+stb_image", "C++")
        folders = self.scaffolder._determine_folder_structure(analysis)

        # Check no duplicates
        self.assertEqual(len(folders), len(set(folders)))

        # Check folders are sorted
        self.assertEqual(folders, sorted(folders))

    def test_generate_main_file_content_love2d(self):
        """Test main file generation for Love2D."""
        analysis = self.tech_stack_manager.parse_tech_stack("Love2D", "Lua")
        content = self.scaffolder._generate_main_file_content("TestGame", analysis)

        # Should contain Love2D-specific functions
        self.assertIn("function love.load()", content)
        self.assertIn("function love.update(dt)", content)
        self.assertIn("function love.draw()", content)
        self.assertIn("function love.keypressed(key)", content)

        # Should contain project name
        self.assertIn("TestGame", content)

    def test_generate_main_file_content_pygame(self):
        """Test main file generation for Pygame."""
        analysis = self.tech_stack_manager.parse_tech_stack("Pygame", "Python")
        content = self.scaffolder._generate_main_file_content("TestGame", analysis)

        # Should contain Pygame-specific imports and patterns
        self.assertIn("import pygame", content)
        self.assertIn("pygame.init()", content)
        self.assertIn("class Game:", content)
        self.assertIn("def run(self):", content)

        # Should contain project name
        self.assertIn("TestGame", content)

    def test_generate_main_file_content_sdl2(self):
        """Test main file generation for SDL2."""
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2", "C++")
        content = self.scaffolder._generate_main_file_content("TestGame", analysis)

        # Should contain SDL2-specific patterns
        self.assertIn("#include <SDL.h>", content)
        self.assertIn("SDL_Init", content)
        self.assertIn("SDL_CreateWindow", content)
        self.assertIn("class Game", content)

        # Should contain project name
        self.assertIn("TestGame", content)

    def test_generate_cmake_content(self):
        """Test CMakeLists.txt generation for C++ projects."""
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2+OpenGL+GLM", "C++")
        cmake_content = self.scaffolder._generate_cmake("TestGame", analysis)

        # Should contain basic CMake structure
        self.assertIn("cmake_minimum_required", cmake_content)
        self.assertIn("project(TestGame)", cmake_content)
        self.assertIn("set(CMAKE_CXX_STANDARD", cmake_content)

        # Should contain find_package calls for libraries
        self.assertIn("find_package(SDL2 REQUIRED)", cmake_content)
        self.assertIn("find_package(OpenGL REQUIRED)", cmake_content)

        # Should contain target configuration
        self.assertIn("add_executable(TestGame", cmake_content)
        self.assertIn("target_link_libraries(TestGame", cmake_content)

    def test_generate_gitignore_cpp(self):
        """Test .gitignore generation for C++ projects."""
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2+OpenGL", "C++")
        gitignore_content = self.scaffolder._generate_gitignore(analysis)

        # Should contain C++-specific patterns
        self.assertIn("build/", gitignore_content)
        self.assertIn("*.o", gitignore_content)
        self.assertIn("*.exe", gitignore_content)
        self.assertIn(".vs/", gitignore_content)

        # Should contain general patterns
        self.assertIn(".antigine/", gitignore_content)
        self.assertIn(".DS_Store", gitignore_content)

    def test_generate_gitignore_python(self):
        """Test .gitignore generation for Python projects."""
        analysis = self.tech_stack_manager.parse_tech_stack("Pygame", "Python")
        gitignore_content = self.scaffolder._generate_gitignore(analysis)

        # Should contain Python-specific patterns
        self.assertIn("__pycache__/", gitignore_content)
        self.assertIn("*.py[cod]", gitignore_content)
        self.assertIn("venv/", gitignore_content)
        self.assertIn("*.egg-info/", gitignore_content)

        # Should contain general patterns
        self.assertIn(".antigine/", gitignore_content)

    def test_generate_readme_content(self):
        """Test README.md generation."""
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2+OpenGL+GLM", "C++")
        readme_content = self.scaffolder._generate_readme("TestGame", analysis)

        # Should contain project information
        self.assertIn("# TestGame", readme_content)
        self.assertIn("C++", readme_content)
        self.assertIn("SDL2", readme_content)
        self.assertIn("OpenGL", readme_content)
        self.assertIn("GLM", readme_content)

        # Should contain documentation links
        self.assertIn("## Tech Stack", readme_content)
        self.assertIn("### Library Documentation", readme_content)

        # Should contain build instructions
        self.assertIn("cmake", readme_content)
        self.assertIn("make", readme_content)

        # Should credit Antigine
        self.assertIn("Antigine", readme_content)

    def test_generate_config_files(self):
        """Test generation of configuration files."""
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2+OpenGL", "C++")
        config_files = self.scaffolder._generate_config_files("TestGame", analysis)

        # Should generate .gitignore and README.md
        self.assertIn(".gitignore", config_files)
        self.assertIn("README.md", config_files)

        # Files should have content
        self.assertGreater(len(config_files[".gitignore"]), 0)
        self.assertGreater(len(config_files["README.md"]), 0)

    def test_generate_library_file_content_love2d_conf(self):
        """Test conf.lua generation for Love2D."""
        love2d_lib = self.tech_stack_manager.library_db["Love2D"]
        analysis = self.tech_stack_manager.parse_tech_stack("Love2D", "Lua")

        content = self.scaffolder._generate_library_file_content("conf.lua", love2d_lib, analysis)

        # Should contain Love2D configuration structure
        self.assertIn("function love.conf(t)", content)
        self.assertIn("t.title", content)
        self.assertIn("t.window.width", content)
        self.assertIn("t.window.height", content)
        self.assertIn("t.modules.", content)

    def test_generate_library_file_content_requirements_txt(self):
        """Test requirements.txt generation for Python."""
        pygame_lib = self.tech_stack_manager.library_db["Pygame"]
        analysis = self.tech_stack_manager.parse_tech_stack("Pygame+NumPy", "Python")

        content = self.scaffolder._generate_library_file_content("requirements.txt", pygame_lib, analysis)

        # Should contain Python package requirements
        self.assertIn("pygame", content.lower())

    def test_language_templates_structure(self):
        """Test that language templates have required structure."""
        templates = self.scaffolder.language_templates

        for language, template in templates.items():
            with self.subTest(language=language):
                self.assertIn("main_file", template)
                self.assertIn("base_folders", template)
                self.assertIsInstance(template["base_folders"], list)
                self.assertGreater(len(template["base_folders"]), 0)


class TestProjectScaffolderIntegration(unittest.TestCase):
    """Integration tests for project scaffolding with temporary directories."""

    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.scaffolder = ProjectScaffolder()
        self.tech_stack_manager = TechStackManager()
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test_project"

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scaffold_project_love2d_creates_files(self):
        """Test that scaffolding actually creates files and folders."""
        analysis = self.tech_stack_manager.parse_tech_stack("Love2D", "Lua")

        result = self.scaffolder.scaffold_project(str(self.project_path), "TestGame", analysis)

        # Check that folders were created
        self.assertGreater(len(result["created_folders"]), 0)

        # Check for the presence of key folders (use flexible path matching)
        self.assertTrue(any("sprites" in folder for folder in result["created_folders"]))
        self.assertTrue(any("images" in folder for folder in result["created_folders"]))
        self.assertTrue(any("audio" in folder for folder in result["created_folders"]))

        # Check that files were created
        self.assertGreater(len(result["created_files"]), 0)
        self.assertTrue(any("main.lua" in file for file in result["created_files"]))
        self.assertTrue(any("README.md" in file for file in result["created_files"]))

        # Verify files actually exist
        main_lua_path = self.project_path / "main.lua"
        self.assertTrue(main_lua_path.exists())

        # Verify file content
        with open(main_lua_path, "r") as f:
            content = f.read()
            self.assertIn("TestGame", content)
            self.assertIn("love.load", content)

    def test_scaffold_project_cpp_creates_cmake(self):
        """Test that C++ projects create CMakeLists.txt."""
        analysis = self.tech_stack_manager.parse_tech_stack("SDL2+OpenGL", "C++")

        self.scaffolder.scaffold_project(str(self.project_path), "TestGame", analysis)

        # Check CMakeLists.txt was created
        cmake_path = self.project_path / "CMakeLists.txt"
        self.assertTrue(cmake_path.exists())

        # Verify CMakeLists.txt content
        with open(cmake_path, "r") as f:
            content = f.read()
            self.assertIn("project(TestGame)", content)
            self.assertIn("find_package(SDL2", content)


if __name__ == "__main__":
    unittest.main()
