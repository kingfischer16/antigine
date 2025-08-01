"""
project_scaffolding.py
######################

Dynamic project scaffolding system that generates appropriate project structures,
starter files, and build configurations based on user-specified tech stacks.

This module works with the tech_stacks module to create language and library-specific
project layouts that follow best practices for the specified technology combination.
"""

from typing import Dict, List, Any
from pathlib import Path
from .tech_stacks import TechStackAnalysis, LibraryCategory, LibraryInfo


class ProjectScaffolder:
    """Generates project structure and files based on tech stack analysis."""

    def __init__(self) -> None:
        self.language_templates = self._initialize_language_templates()

    def scaffold_project(
        self, project_path: str, project_name: str, analysis: TechStackAnalysis
    ) -> Dict[str, List[str]]:
        """
        Generate complete project structure based on tech stack analysis.

        Args:
            project_path: Root directory for the project
            project_name: Name of the project
            analysis: Tech stack analysis from TechStackManager

        Returns:
            Dict with 'created_files' and 'created_folders' lists
        """
        project_root = Path(project_path)
        created: Dict[str, List[str]] = {"created_files": [], "created_folders": []}

        # Create directory structure
        folders = self._determine_folder_structure(analysis)
        for folder in folders:
            folder_path = project_root / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            created["created_folders"].append(str(folder_path))

        # Generate starter files
        starter_files = self._generate_starter_files(project_name, analysis)
        for file_path, content in starter_files.items():
            full_path = project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            created["created_files"].append(str(full_path))

        # Generate build system files
        build_files = self._generate_build_files(project_name, analysis)
        for file_path, content in build_files.items():
            full_path = project_root / file_path
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            created["created_files"].append(str(full_path))

        return created

    def _determine_folder_structure(self, analysis: TechStackAnalysis) -> List[str]:
        """Determine folder structure based on language and libraries."""
        folders = set()

        # Base language-specific folders
        base_folders = self.language_templates[analysis.language]["base_folders"]
        folders.update(base_folders)

        # Library-specific folders
        self._add_library_required_folders(folders, analysis)

        # Category-specific asset folders
        self._add_rendering_folders(folders, analysis)
        self._add_asset_folders(folders, analysis)
        self._add_audio_folders(folders, analysis)
        self._add_ui_folders(folders, analysis)

        # Framework-specific folders
        self._add_framework_folders(folders, analysis)

        # Remove empty strings and sort
        return sorted([f for f in folders if f])

    def _add_library_required_folders(self, folders: set[str], analysis: TechStackAnalysis) -> None:
        """Add folders required by specific libraries."""
        for library in analysis.libraries:
            if library.required_folders:
                folders.update(library.required_folders)

    def _add_rendering_folders(self, folders: set[str], analysis: TechStackAnalysis) -> None:
        """Add rendering-related asset folders."""
        categories = [lib.category for lib in analysis.libraries]
        if LibraryCategory.RENDERING in categories:
            folders.update(["assets/shaders", "assets/textures"])

    def _add_asset_folders(self, folders: set[str], analysis: TechStackAnalysis) -> None:
        """Add asset folders based on 2D/3D context."""
        categories = [lib.category for lib in analysis.libraries]
        lib_names = [lib.name for lib in analysis.libraries]

        if LibraryCategory.ASSETS not in categories:
            return

        # Always add textures (used by both 2D and 3D)
        folders.add("assets/textures")

        # Determine if this is a 3D-capable tech stack
        is_3d_context = self._is_3d_context(analysis)

        # Add 3D-specific folders
        if is_3d_context or "Assimp" in lib_names:
            folders.update(["assets/models", "assets/materials"])

        # Add 2D-specific folders
        if not is_3d_context or self._has_2d_frameworks(analysis):
            folders.update(["assets/sprites", "assets/images"])

    def _add_audio_folders(self, folders: set[str], analysis: TechStackAnalysis) -> None:
        """Add audio-related asset folders."""
        categories = [lib.category for lib in analysis.libraries]
        if LibraryCategory.AUDIO in categories:
            folders.update(["assets/audio", "assets/music"])

    def _add_ui_folders(self, folders: set[str], analysis: TechStackAnalysis) -> None:
        """Add UI-related asset folders."""
        categories = [lib.category for lib in analysis.libraries]
        if LibraryCategory.UI in categories:
            folders.add("assets/fonts")

    def _add_framework_folders(self, folders: set[str], analysis: TechStackAnalysis) -> None:
        """Add framework-specific asset folders."""
        lib_names = [lib.name for lib in analysis.libraries]
        if "Love2D" in lib_names or "Pygame" in lib_names:
            folders.update(["assets/sprites", "assets/images"])

    def _is_3d_context(self, analysis: TechStackAnalysis) -> bool:
        """Determine if the tech stack is 3D-capable."""
        return any(lib.name in ["OpenGL", "Vulkan", "Assimp", "Bullet"] for lib in analysis.libraries)

    def _has_2d_frameworks(self, analysis: TechStackAnalysis) -> bool:
        """Check if the tech stack includes 2D frameworks."""
        return any(lib.name in ["Love2D", "Pygame"] for lib in analysis.libraries)

    def _generate_starter_files(self, project_name: str, analysis: TechStackAnalysis) -> Dict[str, str]:
        """Generate starter code files based on tech stack."""
        files = {}

        # Get language-specific templates
        lang_templates = self.language_templates[analysis.language]

        # Generate main entry point
        main_file = lang_templates["main_file"]
        main_content = self._generate_main_file_content(project_name, analysis)
        files[main_file] = main_content

        # Generate library-specific files
        for library in analysis.libraries:
            if library.required_files:
                for required_file in library.required_files:
                    if required_file not in files:  # Don't overwrite main file
                        file_content = self._generate_library_file_content(required_file, library, analysis)
                        files[required_file] = file_content

        # Generate configuration files
        config_files = self._generate_config_files(project_name, analysis)
        files.update(config_files)

        return files

    def _generate_main_file_content(self, project_name: str, analysis: TechStackAnalysis) -> str:
        """Generate main entry point file content."""
        if analysis.language == "Lua":
            return self._generate_lua_main(project_name, analysis)
        elif analysis.language == "Python":
            return self._generate_python_main(project_name, analysis)
        elif analysis.language == "C++":
            return self._generate_cpp_main(project_name, analysis)
        else:
            return f"// {project_name} - Main entry point\n// TODO: Implement main function\n"

    def _generate_lua_main(self, project_name: str, analysis: TechStackAnalysis) -> str:
        """Generate Lua main.lua for Love2D."""
        return f"""-- {project_name}
-- Love2D Game Entry Point

function love.load()
    -- Initialize game state
    print("Welcome to {project_name}!")

    -- Set window title
    love.window.setTitle("{project_name}")
end

function love.update(dt)
    -- Update game logic
end

function love.draw()
    -- Render game
    love.graphics.print("Hello, {project_name}!", 400, 300)
end

function love.keypressed(key)
    -- Handle input
    if key == "escape" then
        love.event.quit()
    end
end
"""

    def _generate_python_main(self, project_name: str, analysis: TechStackAnalysis) -> str:
        """Generate Python main file."""
        if any(lib.name == "Pygame" for lib in analysis.libraries):
            return f'''#!/usr/bin/env python3
"""
{project_name}
Pygame Game Entry Point
"""

import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("{project_name}")
        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        # Update game logic
        pass

    def render(self):
        # Clear screen
        self.screen.fill((0, 0, 0))

        # Draw game objects
        font = pygame.font.Font(None, 36)
        text = font.render("Hello, {project_name}!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        # Update display
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
'''
        else:
            return f'''#!/usr/bin/env python3
"""
{project_name}
Python Game Entry Point
"""

def main():
    print("Welcome to {project_name}!")
    # TODO: Initialize your game here

if __name__ == "__main__":
    main()
'''

    def _generate_cpp_main(self, project_name: str, analysis: TechStackAnalysis) -> str:
        """Generate C++ main file based on libraries."""
        includes = []
        lib_names = [lib.name for lib in analysis.libraries]

        # Determine includes based on libraries
        if "SDL2" in lib_names:
            includes.extend(["#include <SDL.h>"])
        if "GLFW" in lib_names:
            includes.extend(["#include <GLFW/glfw3.h>"])
        if "OpenGL" in lib_names:
            includes.extend(["#include <GL/gl.h>"])
        if "GLM" in lib_names:
            includes.extend(["#include <glm/glm.hpp>", "#include <glm/gtc/matrix_transform.hpp>"])

        includes_str = "\n".join(includes) if includes else "#include <iostream>"

        if "SDL2" in lib_names:
            return f"""// {project_name}
// SDL2 + OpenGL Game Entry Point

{includes_str}
#include <iostream>

class Game {{
public:
    Game() : window(nullptr), renderer(nullptr), running(false) {{}}

    bool initialize() {{
        if (SDL_Init(SDL_INIT_VIDEO) < 0) {{
            std::cerr << "SDL could not initialize! SDL_Error: " << SDL_GetError() << std::endl;
            return false;
        }}

        window = SDL_CreateWindow("{project_name}",
                                SDL_WINDOWPOS_UNDEFINED,
                                SDL_WINDOWPOS_UNDEFINED,
                                800, 600,
                                SDL_WINDOW_SHOWN);

        if (window == nullptr) {{
            std::cerr << "Window could not be created! SDL_Error: " << SDL_GetError() << std::endl;
            return false;
        }}

        renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
        if (renderer == nullptr) {{
            std::cerr << "Renderer could not be created! SDL_Error: " << SDL_GetError() << std::endl;
            return false;
        }}

        running = true;
        return true;
    }}

    void run() {{
        SDL_Event e;

        while (running) {{
            while (SDL_PollEvent(&e) != 0) {{
                if (e.type == SDL_QUIT) {{
                    running = false;
                }}
            }}

            // Clear screen
            SDL_SetRenderDrawColor(renderer, 0x00, 0x00, 0x00, 0xFF);
            SDL_RenderClear(renderer);

            // TODO: Render game objects here

            // Update screen
            SDL_RenderPresent(renderer);
        }}
    }}

    void cleanup() {{
        SDL_DestroyRenderer(renderer);
        SDL_DestroyWindow(window);
        SDL_Quit();
    }}

private:
    SDL_Window* window;
    SDL_Renderer* renderer;
    bool running;
}};

int main(int argc, char* args[]) {{
    Game game;

    if (!game.initialize()) {{
        std::cerr << "Failed to initialize game!" << std::endl;
        return -1;
    }}

    std::cout << "Welcome to {project_name}!" << std::endl;
    game.run();
    game.cleanup();

    return 0;
}}
"""
        else:
            return f"""// {project_name}
// C++ Game Entry Point

{includes_str}

int main() {{
    std::cout << "Welcome to {project_name}!" << std::endl;
    // TODO: Initialize your game here
    return 0;
}}
"""

    def _generate_library_file_content(self, filename: str, library: LibraryInfo, analysis: TechStackAnalysis) -> str:
        """Generate content for library-specific files."""
        if filename == "conf.lua" and library.name == "Love2D":
            return """-- Love2D Configuration File

function love.conf(t)
    t.title = "Game Title"
    t.author = "Your Name"
    t.version = "11.4"

    t.window.width = 800
    t.window.height = 600
    t.window.resizable = false
    t.window.fullscreen = false
    t.window.vsync = true

    t.modules.audio = true
    t.modules.event = true
    t.modules.graphics = true
    t.modules.image = true
    t.modules.joystick = true
    t.modules.keyboard = true
    t.modules.math = true
    t.modules.mouse = true
    t.modules.physics = true
    t.modules.sound = true
    t.modules.system = true
    t.modules.timer = true
    t.modules.touch = true
    t.modules.video = true
    t.modules.window = true
    t.modules.thread = true
end
"""
        elif filename == "requirements.txt" and analysis.language == "Python":
            # Generate requirements.txt based on Python libraries
            requirements = []
            for lib in analysis.libraries:
                if "Python" in lib.languages:
                    if lib.name == "Pygame":
                        requirements.append("pygame>=2.0.0")
                    elif lib.name == "NumPy":
                        requirements.append("numpy>=1.21.0")

            return "\n".join(requirements) + "\n" if requirements else "# Add your Python dependencies here\n"

        return f"# {filename} - Generated by Antigine\n# TODO: Configure {library.name}\n"

    def _generate_config_files(self, project_name: str, analysis: TechStackAnalysis) -> Dict[str, str]:
        """Generate configuration files like .gitignore, README.md."""
        files = {}

        # Generate .gitignore
        files[".gitignore"] = self._generate_gitignore(analysis)

        # Generate README.md
        files["README.md"] = self._generate_readme(project_name, analysis)

        return files

    def _generate_build_files(self, project_name: str, analysis: TechStackAnalysis) -> Dict[str, str]:
        """Generate build system files (CMakeLists.txt, Makefile, etc.)."""
        files = {}

        if analysis.language == "C++":
            # Generate CMakeLists.txt
            files["CMakeLists.txt"] = self._generate_cmake(project_name, analysis)

        return files

    def _generate_cmake(self, project_name: str, analysis: TechStackAnalysis) -> str:
        """Generate CMakeLists.txt for C++ projects."""
        lib_names = [lib.name for lib in analysis.libraries]

        # Use build configuration if available, otherwise fall back to defaults
        if analysis.build_config:
            cmake_version = analysis.build_config.cmake_minimum_version
            cxx_standard = analysis.build_config.cmake_cxx_standard
            version_reason = analysis.build_config.cmake_version_reason
        else:
            cmake_version = "3.16"
            cxx_standard = "17"
            version_reason = "Default version for C++ game development"

        cmake_content = f"""# CMake version requirement: {version_reason}
cmake_minimum_required(VERSION {cmake_version})
project({project_name})

set(CMAKE_CXX_STANDARD {cxx_standard})
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
"""

        # Add find_package calls based on libraries
        if "SDL2" in lib_names:
            cmake_content += "find_package(SDL2 REQUIRED)\n"
        if "OpenGL" in lib_names:
            cmake_content += "find_package(OpenGL REQUIRED)\n"
        if "GLFW" in lib_names:
            cmake_content += "find_package(glfw3 REQUIRED)\n"
        if "Bullet" in lib_names:
            cmake_content += "find_package(Bullet REQUIRED)\n"
        if "Assimp" in lib_names:
            cmake_content += "find_package(assimp REQUIRED)\n"

        cmake_content += f"""
# Add executable
add_executable({project_name} src/main.cpp)

# Link libraries
target_link_libraries({project_name}
"""

        # Add target_link_libraries based on libraries
        if "SDL2" in lib_names:
            cmake_content += "    SDL2::SDL2\n"
        if "OpenGL" in lib_names:
            cmake_content += "    OpenGL::GL\n"
        if "GLFW" in lib_names:
            cmake_content += "    glfw\n"
        if "Bullet" in lib_names:
            cmake_content += "    ${BULLET_LIBRARIES}\n"
        if "Assimp" in lib_names:
            cmake_content += "    assimp\n"

        cmake_content += ")\n"

        return cmake_content

    def _generate_gitignore(self, analysis: TechStackAnalysis) -> str:
        """Generate .gitignore based on language and tech stack."""
        gitignore_content = "# Antigine Project\n.antigine/\n\n"

        if analysis.language == "C++":
            gitignore_content += """# C++ Build artifacts
build/
*.o
*.exe
*.dll
*.so
*.dylib

# IDE files
.vs/
.vscode/
*.vcxproj.user
*.sln.docstates

"""
        elif analysis.language == "Python":
            gitignore_content += """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

"""
        elif analysis.language == "Lua":
            gitignore_content += """# Lua
luac.out

# Love2D
*.love

"""

        gitignore_content += """# Assets (optional - comment out if you want to track assets)
# assets/

# Logs
*.log

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""

        return gitignore_content

    def _generate_readme(self, project_name: str, analysis: TechStackAnalysis) -> str:
        """Generate README.md file."""
        lib_list = ", ".join([lib.display_name for lib in analysis.libraries])

        readme_content = f"""# {project_name}

A {analysis.language} game project built with {lib_list}.

## Tech Stack

**Language:** {analysis.language}
**Libraries:** {lib_list}

### Library Documentation
"""

        for lib_name, url in analysis.documentation_urls.items():
            readme_content += f"- [{lib_name}]({url})\n"

        readme_content += f"""
## Getting Started

### Prerequisites

Make sure you have {analysis.language} installed on your system.

"""

        # Add build instructions based on language
        if analysis.language == "C++":
            readme_content += (
                """### Building

```bash
mkdir build
cd build
cmake ..
make
```

### Running

```bash
./"""
                + project_name
                + """
```
"""
            )
        elif analysis.language == "Python":
            readme_content += """### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Running

```bash
python main.py
```
"""
        elif analysis.language == "Lua":
            readme_content += """### Running

Make sure you have Love2D installed, then:

```bash
love .
```
"""

        readme_content += """
## Project Structure

Generated by [Antigine](https://github.com/kingfischer16/antigine) - The Agentic Anti-Engine Game Development Tool.
"""

        return readme_content

    def _initialize_language_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize base templates for different languages."""
        return {
            "C++": {"main_file": "src/main.cpp", "base_folders": ["src", "include", "assets", "build", "docs"]},
            "Python": {"main_file": "main.py", "base_folders": ["src", "assets", "tests"]},
            "Lua": {"main_file": "main.lua", "base_folders": ["src", "assets"]},
            "C": {"main_file": "src/main.c", "base_folders": ["src", "include", "assets", "build"]},
            "Rust": {"main_file": "src/main.rs", "base_folders": ["src", "assets", "tests"]},
        }


# Global instance for use throughout the application
project_scaffolder = ProjectScaffolder()
