"""
tech_stacks.py
##############

Flexible library-based tech stack system for Antigine. This module provides
a comprehensive database of individual libraries and frameworks, allowing users
to specify arbitrary combinations of technologies for their game projects.

The system supports dynamic parsing of user-specified tech stacks like:
- "Love2D" (single framework)
- "SDL2+OpenGL+GLM+Assimp" (multiple libraries)
- "Pygame+NumPy+Pillow" (Python libraries)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class LibraryCategory(Enum):
    """Categories for organizing libraries by their primary function."""

    FRAMEWORK = "Framework"  # Complete game frameworks (Love2D, Pygame)
    WINDOWING = "Windowing"  # Window/input management (SDL2, GLFW)
    RENDERING = "Rendering"  # Graphics APIs (OpenGL, Vulkan, DirectX)
    MATH = "Math"  # Mathematics libraries (GLM, NumPy)
    PHYSICS = "Physics"  # Physics engines (Bullet, Box2D)
    AUDIO = "Audio"  # Audio systems (OpenAL, FMOD)
    NETWORKING = "Networking"  # Network libraries (ENet, RakNet)
    ASSETS = "Assets"  # Asset loading (Assimp, stb_image)
    UI = "UI"  # User interface (Dear ImGui, CEGUI)
    UTILITY = "Utility"  # General utilities (spdlog, JSON)
    BUILD = "Build"  # Build systems (CMake, Make)


@dataclass
class LibraryInfo:
    """Complete metadata for a single library or framework."""

    name: str
    display_name: str
    description: str
    category: LibraryCategory
    languages: List[str]

    # Documentation
    documentation_url: str
    api_reference_url: str
    examples_url: str
    repository_url: Optional[str] = None

    # Integration info
    dependencies: Optional[List[str]] = None  # Other libraries this depends on
    conflicts: Optional[List[str]] = None  # Libraries incompatible with this one

    # Installation
    install_instructions: Optional[Dict[str, str]] = None  # Platform-specific install commands

    # Project setup
    required_files: Optional[List[str]] = None  # Files this library typically needs
    required_folders: Optional[List[str]] = None  # Folders this library typically needs

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []
        if self.conflicts is None:
            self.conflicts = []
        if self.install_instructions is None:
            self.install_instructions = {}
        if self.required_files is None:
            self.required_files = []
        if self.required_folders is None:
            self.required_folders = []


# Comprehensive Library Database
LIBRARY_DATABASE: Dict[str, LibraryInfo] = {
    # === 2D FRAMEWORKS ===
    "Love2D": LibraryInfo(
        name="Love2D",
        display_name="LÖVE 2D",
        description="2D game framework for Lua with built-in physics, audio, and graphics",
        category=LibraryCategory.FRAMEWORK,
        languages=["Lua"],
        documentation_url="https://love2d.org/wiki/Main_Page",
        api_reference_url="https://love2d.org/wiki/love",
        examples_url="https://love2d.org/wiki/Category:Games",
        repository_url="https://github.com/love2d/love",
        install_instructions={
            "windows": "Download from https://love2d.org/",
            "ubuntu": "sudo apt install love",
            "macos": "brew install love",
        },
        required_files=["main.lua", "conf.lua"],
        required_folders=["assets/sprites", "assets/images", "assets/audio", "src"],
    ),
    "Pygame": LibraryInfo(
        name="Pygame",
        display_name="Pygame",
        description="Cross-platform set of Python modules for writing video games",
        category=LibraryCategory.FRAMEWORK,
        languages=["Python"],
        documentation_url="https://www.pygame.org/docs/",
        api_reference_url="https://www.pygame.org/docs/ref/",
        examples_url="https://github.com/pygame/pygame/tree/main/examples",
        repository_url="https://github.com/pygame/pygame",
        install_instructions={"all": "pip install pygame"},
        required_files=["main.py", "requirements.txt"],
        required_folders=["src", "assets/sprites", "assets/images", "assets/sounds"],
    ),
    # === WINDOWING/INPUT ===
    "SDL2": LibraryInfo(
        name="SDL2",
        display_name="Simple DirectMedia Layer 2",
        description="Cross-platform library for window management, input, and multimedia",
        category=LibraryCategory.WINDOWING,
        languages=["C++", "C"],
        documentation_url="https://wiki.libsdl.org/",
        api_reference_url="https://wiki.libsdl.org/CategoryAPI",
        examples_url="https://github.com/libsdl-org/SDL/tree/main/test",
        repository_url="https://github.com/libsdl-org/SDL",
        install_instructions={
            "ubuntu": "sudo apt install libsdl2-dev",
            "windows": "vcpkg install sdl2",
            "macos": "brew install sdl2",
        },
        required_folders=["src", "include"],
    ),
    "GLFW": LibraryInfo(
        name="GLFW",
        display_name="GLFW",
        description="Multi-platform library for OpenGL, OpenGL ES and Vulkan development",
        category=LibraryCategory.WINDOWING,
        languages=["C++", "C"],
        documentation_url="https://www.glfw.org/documentation.html",
        api_reference_url="https://www.glfw.org/docs/latest/",
        examples_url="https://github.com/glfw/glfw/tree/master/examples",
        repository_url="https://github.com/glfw/glfw",
        install_instructions={
            "ubuntu": "sudo apt install libglfw3-dev",
            "windows": "vcpkg install glfw3",
            "macos": "brew install glfw",
        },
    ),
    # === RENDERING ===
    "OpenGL": LibraryInfo(
        name="OpenGL",
        display_name="OpenGL",
        description="Cross-platform graphics rendering API",
        category=LibraryCategory.RENDERING,
        languages=["C++", "C"],
        documentation_url="https://docs.gl/",
        api_reference_url="https://registry.khronos.org/OpenGL/",
        examples_url="https://learnopengl.com/",
        dependencies=["GLFW"],  # Usually needs a windowing library
        required_folders=["assets/shaders"],
    ),
    "Vulkan": LibraryInfo(
        name="Vulkan",
        display_name="Vulkan API",
        description="Low-overhead, cross-platform 3D graphics and compute API",
        category=LibraryCategory.RENDERING,
        languages=["C++", "C"],
        documentation_url="https://vulkan.lunarg.com/doc/sdk",
        api_reference_url="https://registry.khronos.org/vulkan/",
        examples_url="https://vulkan-tutorial.com/",
        conflicts=["OpenGL"],  # Typically don't use both
        required_folders=["assets/shaders"],
    ),
    # === MATH ===
    "GLM": LibraryInfo(
        name="GLM",
        display_name="OpenGL Mathematics",
        description="Header-only C++ mathematics library for graphics software",
        category=LibraryCategory.MATH,
        languages=["C++"],
        documentation_url="https://glm.g-truc.net/0.9.9/index.html",
        api_reference_url="https://glm.g-truc.net/0.9.9/api/index.html",
        examples_url="https://github.com/g-truc/glm/tree/master/test",
        repository_url="https://github.com/g-truc/glm",
        install_instructions={
            "ubuntu": "sudo apt install libglm-dev",
            "windows": "vcpkg install glm",
            "macos": "brew install glm",
        },
    ),
    "NumPy": LibraryInfo(
        name="NumPy",
        display_name="NumPy",
        description="Fundamental package for scientific computing with Python",
        category=LibraryCategory.MATH,
        languages=["Python"],
        documentation_url="https://numpy.org/doc/",
        api_reference_url="https://numpy.org/doc/stable/reference/",
        examples_url="https://numpy.org/numpy-tutorials/",
        repository_url="https://github.com/numpy/numpy",
        install_instructions={"all": "pip install numpy"},
    ),
    # === PHYSICS ===
    "Bullet": LibraryInfo(
        name="Bullet",
        display_name="Bullet Physics",
        description="3D collision detection and rigid body dynamics library",
        category=LibraryCategory.PHYSICS,
        languages=["C++"],
        documentation_url="https://pybullet.org/wordpress/",
        api_reference_url="https://bulletphysics.org/Bullet/BulletFull/",
        examples_url="https://github.com/bulletphysics/bullet3/tree/master/examples",
        repository_url="https://github.com/bulletphysics/bullet3",
        install_instructions={
            "ubuntu": "sudo apt install libbullet-dev",
            "windows": "vcpkg install bullet3",
            "macos": "brew install bullet",
        },
    ),
    "Box2D": LibraryInfo(
        name="Box2D",
        display_name="Box2D",
        description="2D physics engine for games",
        category=LibraryCategory.PHYSICS,
        languages=["C++"],
        documentation_url="https://box2d.org/documentation/",
        api_reference_url="https://box2d.org/documentation/",
        examples_url="https://github.com/erincatto/box2d/tree/main/samples",
        repository_url="https://github.com/erincatto/box2d",
        conflicts=["Bullet"],  # Usually don't need both 2D and 3D physics
        install_instructions={
            "ubuntu": "sudo apt install libbox2d-dev",
            "windows": "vcpkg install box2d",
            "macos": "brew install box2d",
        },
    ),
    # === ASSETS ===
    "Assimp": LibraryInfo(
        name="Assimp",
        display_name="Open Asset Import Library",
        description="Library to import and export various 3D-model-formats",
        category=LibraryCategory.ASSETS,
        languages=["C++"],
        documentation_url="https://assimp-docs.readthedocs.io/",
        api_reference_url="https://assimp-docs.readthedocs.io/en/v5.1.0/",
        examples_url="https://github.com/assimp/assimp/tree/master/samples",
        repository_url="https://github.com/assimp/assimp",
        install_instructions={
            "ubuntu": "sudo apt install libassimp-dev",
            "windows": "vcpkg install assimp",
            "macos": "brew install assimp",
        },
        required_folders=["assets/models"],
    ),
    "stb_image": LibraryInfo(
        name="stb_image",
        display_name="stb_image",
        description="Single-file public domain image loader",
        category=LibraryCategory.ASSETS,
        languages=["C++", "C"],
        documentation_url="https://github.com/nothings/stb",
        api_reference_url="https://github.com/nothings/stb/blob/master/stb_image.h",
        examples_url="https://github.com/nothings/stb/tree/master/tests",
        repository_url="https://github.com/nothings/stb",
        required_folders=["assets/textures"],
    ),
    # === UI ===
    "Dear ImGui": LibraryInfo(
        name="Dear ImGui",
        display_name="Dear ImGui",
        description="Bloat-free graphical user interface library for C++",
        category=LibraryCategory.UI,
        languages=["C++"],
        documentation_url="https://github.com/ocornut/imgui/blob/master/docs/README.md",
        api_reference_url="https://github.com/ocornut/imgui/blob/master/imgui.h",
        examples_url="https://github.com/ocornut/imgui/tree/master/examples",
        repository_url="https://github.com/ocornut/imgui",
        install_instructions={
            "windows": "vcpkg install imgui",
            "ubuntu": "Build from source - see documentation",
            "macos": "Build from source - see documentation",
        },
    ),
}


@dataclass
class BuildSystemConfig:
    """Configuration for build system generation."""

    # CMake settings
    cmake_minimum_version: str = "3.16"  # Default minimum version
    cmake_cxx_standard: str = "17"  # C++ standard version
    cmake_c_standard: str = "11"  # C standard version

    # Documentation for version choices
    cmake_version_reason: str = "3.16 supports modern CMake features and is widely available"


@dataclass
class TechStackAnalysis:
    """Result of analyzing a user-specified tech stack."""

    language: str
    libraries: List[LibraryInfo]
    documentation_urls: Dict[str, str]
    api_reference_urls: Dict[str, str]
    example_urls: Dict[str, str]
    unsupported_libraries: List[str]
    conflicts: List[str]
    warnings: List[str]
    suggested_additions: List[str]
    build_config: Optional[BuildSystemConfig] = None


class TechStackManager:
    """Manager for parsing and validating user-specified tech stacks."""

    def __init__(self) -> None:
        self.library_db = LIBRARY_DATABASE

    def parse_tech_stack(self, tech_stack_input: str, language: str) -> TechStackAnalysis:
        """
        Parse user input like "SDL2+OpenGL+GLM" into analyzed tech stack information.

        Args:
            tech_stack_input: User-specified tech stack (e.g., "SDL2+OpenGL+GLM")
                             Must be a non-empty string with at least one valid library name.
                             Handles edge cases like leading/trailing '+', consecutive '+',
                             and whitespace around library names.
            language: Programming language (e.g., "C++")

        Returns:
            TechStackAnalysis with validation results and metadata

        Raises:
            ValueError: If tech_stack_input is None, empty, whitespace-only,
                       contains only '+' characters, or has no valid library names
            TypeError: If tech_stack_input is not a string
        """
        # Input validation
        if not tech_stack_input:
            raise ValueError("Tech stack input cannot be None or empty")

        if not isinstance(tech_stack_input, str):
            raise TypeError(
                f"Tech stack input must be a string (e.g., 'SDL2+OpenGL+GLM'), got {type(tech_stack_input)}"
            )

        # Normalize input by stripping whitespace
        tech_stack_input = tech_stack_input.strip()

        if not tech_stack_input:
            raise ValueError("Tech stack input cannot be empty or contain only whitespace")

        # Check for edge cases with only delimiters
        if all(char == "+" for char in tech_stack_input):
            raise ValueError("Tech stack input cannot contain only delimiter characters ('+')")

        # Parse library names - filter out empty strings after splitting and stripping
        library_names = [lib.strip() for lib in tech_stack_input.split("+") if lib.strip()]

        # Final validation - ensure we have at least one valid library name
        if not library_names:
            raise ValueError("No valid library names found in tech stack input")

        # Initialize analysis result
        analysis = TechStackAnalysis(
            language=language,
            libraries=[],
            documentation_urls={},
            api_reference_urls={},
            example_urls={},
            unsupported_libraries=[],
            conflicts=[],
            warnings=[],
            suggested_additions=[],
            build_config=None,
        )

        # Process each library
        found_libraries = []
        for lib_name in library_names:
            if lib_name in self.library_db:
                lib_info = self.library_db[lib_name]

                # Check language compatibility
                if language in lib_info.languages:
                    found_libraries.append(lib_info)
                    analysis.libraries.append(lib_info)
                    analysis.documentation_urls[lib_name] = lib_info.documentation_url
                    analysis.api_reference_urls[lib_name] = lib_info.api_reference_url
                    analysis.example_urls[lib_name] = lib_info.examples_url
                else:
                    analysis.unsupported_libraries.append(
                        f"{lib_name} (not compatible with {language}, supports: {', '.join(lib_info.languages)})"
                    )
            else:
                analysis.unsupported_libraries.append(f"{lib_name} (unknown library)")

        # Check for conflicts
        analysis.conflicts = self._find_conflicts(found_libraries)

        # Generate warnings and suggestions
        analysis.warnings = self._generate_warnings(found_libraries, language)
        analysis.suggested_additions = self._suggest_additions(found_libraries, language)

        # Generate build system configuration
        analysis.build_config = self._generate_build_config(found_libraries, language)

        return analysis

    def _find_conflicts(self, libraries: List[LibraryInfo]) -> List[str]:
        """Find conflicting libraries in the tech stack."""
        conflicts = []
        lib_names = [lib.name for lib in libraries]

        for lib in libraries:
            if lib.conflicts:
                for conflict in lib.conflicts:
                    if conflict in lib_names:
                        conflicts.append(f"{lib.name} conflicts with {conflict}")

        return conflicts

    def _generate_warnings(self, libraries: List[LibraryInfo], language: str) -> List[str]:
        """Generate warnings about the tech stack composition."""
        warnings = []
        categories = [lib.category for lib in libraries]

        # Check for missing essential components
        if LibraryCategory.RENDERING in categories and LibraryCategory.WINDOWING not in categories:
            warnings.append("Rendering library found but no windowing library - consider adding SDL2 or GLFW")

        if LibraryCategory.PHYSICS in categories and LibraryCategory.MATH not in categories:
            if language == "C++":
                warnings.append("Physics library found but no math library - consider adding GLM")
            elif language == "Python":
                warnings.append("Physics library found but no math library - consider adding NumPy")

        return warnings

    def _suggest_additions(self, libraries: List[LibraryInfo], language: str) -> List[str]:
        """Suggest additional libraries that might be useful."""
        suggestions = []
        categories = [lib.category for lib in libraries]

        # Suggest common additions based on what's already included
        if LibraryCategory.RENDERING in categories:
            if LibraryCategory.ASSETS not in categories:
                if language == "C++":
                    suggestions.append("Consider adding Assimp for 3D model loading")
                    suggestions.append("Consider adding stb_image for texture loading")

        if len(libraries) > 2 and LibraryCategory.UI not in categories:
            if language == "C++":
                suggestions.append("Consider adding Dear ImGui for debug UI")

        return suggestions

    def get_available_libraries(self, language: Optional[str] = None) -> Dict[str, LibraryInfo]:
        """Get all available libraries, optionally filtered by language."""
        if language is None:
            return self.library_db

        return {name: info for name, info in self.library_db.items() if language in info.languages}

    def search_libraries(
        self,
        language: Optional[str] = None,
        category: Optional[LibraryCategory] = None,
        search_term: Optional[str] = None,
    ) -> Dict[str, LibraryInfo]:
        """Search libraries by various criteria."""
        results = self.library_db.copy()

        if language:
            results = {name: info for name, info in results.items() if language in info.languages}

        if category:
            results = {name: info for name, info in results.items() if info.category == category}

        if search_term:
            search_lower = search_term.lower()
            results = {
                name: info
                for name, info in results.items()
                if (
                    search_lower in name.lower()
                    or search_lower in info.display_name.lower()
                    or search_lower in info.description.lower()
                )
            }

        return results

    def _generate_build_config(self, libraries: List[LibraryInfo], language: str) -> Optional[BuildSystemConfig]:
        """Generate build system configuration based on tech stack and language."""
        if language not in ["C++", "C"]:
            return None  # Only generate build config for C/C++ projects

        config = BuildSystemConfig()
        lib_names = [lib.name for lib in libraries]

        # Adjust CMake version based on library requirements
        if "Vulkan" in lib_names:
            # Vulkan requires newer CMake for proper FindVulkan module
            config.cmake_minimum_version = "3.21"
            config.cmake_version_reason = "3.21 required for modern Vulkan support and FindVulkan module"
        elif any(lib in lib_names for lib in ["Assimp", "Bullet", "Dear ImGui"]):
            # Complex libraries benefit from newer CMake features
            config.cmake_minimum_version = "3.18"
            config.cmake_version_reason = "3.18 provides better support for modern C++ libraries and find modules"
        elif any(lib in lib_names for lib in ["SDL2", "GLFW", "OpenGL"]):
            # Standard game development libraries work well with 3.16+
            config.cmake_minimum_version = "3.16"
            config.cmake_version_reason = "3.16 supports modern CMake features and is widely available"
        else:
            # Default for simple projects
            config.cmake_minimum_version = "3.14"
            config.cmake_version_reason = "3.14 provides good C++17 support and is available on most systems"

        # Adjust C++ standard based on libraries
        if any(lib in lib_names for lib in ["Vulkan", "Dear ImGui", "Assimp"]):
            # Modern libraries often require C++17 or newer features
            config.cmake_cxx_standard = "17"
        elif any(lib in lib_names for lib in ["SDL2", "OpenGL", "GLFW"]):
            # Game development libraries typically work well with C++17
            config.cmake_cxx_standard = "17"
        else:
            # Conservative default
            config.cmake_cxx_standard = "14"

        return config

    def create_custom_build_config(
        self,
        cmake_version: str = "3.16",
        cxx_standard: str = "17",
        c_standard: str = "11",
        reason: str = "Custom configuration",
    ) -> BuildSystemConfig:
        """Create a custom build configuration with specified settings.

        This allows users to override the automatic CMake version selection
        for projects with specific requirements.

        Args:
            cmake_version: Minimum CMake version (e.g., "3.16", "3.21")
            cxx_standard: C++ standard version (e.g., "14", "17", "20")
            c_standard: C standard version (e.g., "11", "17")
            reason: Documentation explaining why these versions were chosen

        Returns:
            BuildSystemConfig with custom settings
        """
        return BuildSystemConfig(
            cmake_minimum_version=cmake_version,
            cmake_cxx_standard=cxx_standard,
            cmake_c_standard=c_standard,
            cmake_version_reason=reason,
        )


def get_default_tech_stack(language: str) -> str:
    """Get the default tech stack for a given language.

    Args:
        language: Programming language (e.g., "Lua", "Python", "C++")

    Returns:
        Default tech stack name that exists in the library database

    Raises:
        ValueError: If no default is available for the language
    """
    if language in DEFAULT_TECH_STACKS:
        return DEFAULT_TECH_STACKS[language]
    else:
        raise ValueError(f"No default tech stack configured for language: {language}")


def resolve_tech_stack_name(tech_stack_input: str) -> str:
    """Resolve tech stack names, handling aliases and case variations.

    Args:
        tech_stack_input: User input that might use aliases or incorrect case

    Returns:
        Properly formatted tech stack name for use with library database
    """
    # Handle direct aliases
    if tech_stack_input in TECH_STACK_ALIASES:
        return TECH_STACK_ALIASES[tech_stack_input]

    # Handle multi-library tech stacks with aliases
    if "+" in tech_stack_input:
        parts = [part.strip() for part in tech_stack_input.split("+")]
        resolved_parts = []
        for part in parts:
            if part in TECH_STACK_ALIASES:
                resolved_parts.append(TECH_STACK_ALIASES[part])
            else:
                resolved_parts.append(part)
        return "+".join(resolved_parts)

    # Return as-is if no alias found
    return tech_stack_input


# Configuration constants
DEFAULT_TECH_STACKS = {
    "Lua": "Love2D",  # Default for Lua projects
    "Python": "Pygame",  # Default for Python projects
    "C++": "SDL2+OpenGL",  # Default for C++ projects
    "C": "SDL2",  # Default for C projects
}

# Backwards compatibility and common aliases
TECH_STACK_ALIASES = {
    "love2d": "Love2D",  # Canonical name for Love2D
    "pygame": "Pygame",  # Canonical name for Pygame
    "sdl2": "SDL2",  # Canonical name for SDL2
    "opengl": "OpenGL",  # Canonical name for OpenGL
}


# Global instance for use throughout the application
tech_stack_manager = TechStackManager()
