"""
setup_wizard.py
###############

Interactive setup wizard for guiding users through tech stack selection
and project configuration. This provides a user-friendly way to discover
and configure appropriate technology combinations for game development.
"""

from typing import List, Tuple
from .tech_stacks import TechStackManager, LibraryCategory, LibraryInfo
from ..cli.utils.validation import prompt_for_input, prompt_for_choice, confirm_action
from ..cli.utils.output import print_info, print_success, print_warning


class SetupWizard:
    """Interactive wizard for tech stack selection and project setup."""

    def __init__(self) -> None:
        self.tech_stack_manager = TechStackManager()

    def run_interactive_setup(self) -> Tuple[str, str, str]:
        """
        Run the complete interactive setup wizard.

        Returns:
            Tuple of (project_name, language, tech_stack_string)
        """
        print_info("Welcome to the Antigine Interactive Setup Wizard!")
        print_info("This wizard will help you configure your game project.")
        print("")

        # Step 1: Project name
        project_name = self._get_project_name()

        # Step 2: Language selection
        language = self._select_language()

        # Step 3: Tech stack selection
        tech_stack = self._select_tech_stack(language)

        # Step 4: Review and confirm
        if self._confirm_setup(project_name, language, tech_stack):
            return project_name, language, tech_stack
        else:
            print_info("Setup cancelled. You can run 'antigine init' again to restart.")
            raise KeyboardInterrupt("Setup cancelled by user")

    def _get_project_name(self) -> str:
        """Get project name from user."""
        print_info("Step 1: Project Information")

        project_name = prompt_for_input("Enter your project name", required=True)

        return project_name

    def _select_language(self) -> str:
        """Interactive language selection."""
        print_info("\nStep 2: Programming Language")
        print_info("Choose the programming language for your game:")

        # Get available languages from the library database
        available_languages = set()
        for lib_info in self.tech_stack_manager.library_db.values():
            available_languages.update(lib_info.languages)

        languages = sorted(list(available_languages))

        # Add descriptions for languages
        language_descriptions = {
            "C++": "High performance, widely used for 3D games",
            "Python": "Beginner-friendly, great for 2D games and prototyping",
            "Lua": "Lightweight scripting, popular with Love2D framework",
            "C": "Low-level control, maximum performance",
            "Rust": "Modern systems language with memory safety",
        }

        print("")
        for i, lang in enumerate(languages, 1):
            desc = language_descriptions.get(lang, "")
            if desc:
                print(f"  {i}. {lang} - {desc}")
            else:
                print(f"  {i}. {lang}")

        selected_language = prompt_for_choice("Select your programming language", languages)

        return selected_language

    def _select_tech_stack(self, language: str) -> str:
        """Interactive tech stack selection based on language."""
        print_info(f"\nStep 3: Tech Stack Selection ({language})")

        # Show different paths based on user preference
        approach = prompt_for_choice(
            "How would you like to choose your tech stack?",
            [
                "Guided selection (recommended for beginners)",
                "Browse by category",
                "Manual specification (advanced users)",
            ],
        )

        if "Guided" in approach:
            return self._guided_tech_stack_selection(language)
        elif "Browse" in approach:
            return self._category_based_selection(language)
        else:
            return self._manual_tech_stack_specification(language)

    def _guided_tech_stack_selection(self, language: str) -> str:
        """Guided tech stack selection with questions."""
        print_info("\nGuided Tech Stack Selection")
        print_info("Answer a few questions to get personalized recommendations.")

        # Question 1: Game type
        game_type = prompt_for_choice("\nWhat type of game are you making?", ["2D Game", "3D Game", "Not sure yet"])

        # Question 2: Experience level
        experience = prompt_for_choice(
            "\nWhat's your experience level with game development?", ["Beginner", "Intermediate", "Advanced"]
        )

        # Question 3: Project scope
        scope = prompt_for_choice(
            "\nWhat's the scope of your project?",
            ["Small prototype/learning project", "Medium indie game", "Large/commercial project"],
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(language, game_type, experience, scope)

        print_info("\nBased on your answers, here are our recommendations:")
        for i, (tech_stack, reason) in enumerate(recommendations, 1):
            print(f"\n  {i}. {tech_stack}")
            print(f"     {reason}")

        if recommendations:
            choice = prompt_for_choice(
                "\nSelect a recommended tech stack or choose 'Custom' to specify your own",
                [rec[0] for rec in recommendations] + ["Custom"],
            )

            if choice == "Custom":
                return self._manual_tech_stack_specification(language)
            else:
                return choice
        else:
            print_warning("No specific recommendations available. Falling back to manual selection.")
            return self._manual_tech_stack_specification(language)

    def _category_based_selection(self, language: str) -> str:
        """Browse libraries by category and build tech stack."""
        print_info("\\nCategory-Based Selection")
        print_info("Browse available libraries by category and build your tech stack.")

        selected_libraries: List[str] = []
        categories = list(LibraryCategory)

        while True:
            print_info(f"\\nCurrently selected: {'+'.join(selected_libraries) if selected_libraries else 'None'}")

            action = prompt_for_choice(
                "What would you like to do?", ["Browse a category", "Finish selection", "Start over"]
            )

            if action == "Finish selection":
                if selected_libraries:
                    break
                else:
                    print_warning("Please select at least one library.")
                    continue
            elif action == "Start over":
                selected_libraries = []
                continue
            else:  # Browse a category
                category = prompt_for_choice("\\nSelect a category to browse", [cat.value for cat in categories])

                # Find the enum value
                selected_category = next(cat for cat in categories if cat.value == category)

                # Get libraries in this category for the language
                category_libs = self.tech_stack_manager.search_libraries(language=language, category=selected_category)

                if not category_libs:
                    print_warning(f"No {category} libraries available for {language}")
                    continue

                # Show libraries in category
                lib_names = list(category_libs.keys())
                print_info(f"\\nAvailable {category} libraries for {language}:")
                for i, lib_name in enumerate(lib_names, 1):
                    lib_info = category_libs[lib_name]
                    print(f"  {i}. {lib_name} - {lib_info.description}")

                lib_choice = prompt_for_choice(
                    f"\\nSelect a {category} library (or skip)", lib_names + ["Skip this category"]
                )

                if lib_choice != "Skip this category" and lib_choice not in selected_libraries:
                    selected_libraries.append(lib_choice)
                    print_success(f"Added {lib_choice} to your tech stack!")

        return "+".join(selected_libraries)

    def _manual_tech_stack_specification(self, language: str) -> str:
        """Manual tech stack specification with validation."""
        print_info("\\nManual Tech Stack Specification")
        print_info("Enter your tech stack as library names separated by '+' characters.")
        print_info("Example: SDL2+OpenGL+GLM+Assimp")

        # Show available libraries for reference
        available_libs = self.tech_stack_manager.get_available_libraries(language)
        lib_names = sorted(available_libs.keys())

        print_info(f"\\nAvailable libraries for {language}:")
        for i, lib_name in enumerate(lib_names):
            lib_info = available_libs[lib_name]
            print(f"  {lib_name} ({lib_info.category.value}) - {lib_info.description}")
            if i >= 9:  # Limit display to avoid overwhelming
                remaining = len(lib_names) - 10
                print(f"  ... and {remaining} more libraries")
                break

        while True:
            tech_stack = prompt_for_input("\\nEnter your tech stack", required=True)

            # Validate the tech stack
            analysis = self.tech_stack_manager.parse_tech_stack(tech_stack, language)

            if analysis.unsupported_libraries:
                print_warning("\\nIssues found:")
                for issue in analysis.unsupported_libraries:
                    print(f"  - {issue}")

                if confirm_action("\\nWould you like to try again?", default=True):
                    continue
                else:
                    print_info("Proceeding with partial tech stack...")
                    break

            if analysis.conflicts:
                print_warning("\\nConflicts detected:")
                for conflict in analysis.conflicts:
                    print(f"  - {conflict}")

                if not confirm_action("\\nProceed anyway?", default=False):
                    continue

            if analysis.warnings:
                print_info("\\nRecommendations:")
                for warning in analysis.warnings:
                    print(f"  - {warning}")

            break

        return tech_stack

    def _generate_recommendations(
        self, language: str, game_type: str, experience: str, scope: str
    ) -> List[Tuple[str, str]]:
        """Generate tech stack recommendations based on user answers."""
        recommendations = []

        if language == "Lua":
            recommendations.append(
                ("Love2D", "Perfect for 2D games in Lua, beginner-friendly with great documentation")
            )

        elif language == "Python":
            recommendations.append(
                ("Pygame", "Excellent for learning game development, great for 2D games and prototypes")
            )

            if "3D" in game_type:
                recommendations.append(("Pygame+NumPy", "Pygame with NumPy for better math operations in 3D"))

        elif language == "C++":
            if experience == "Beginner":
                if "2D" in game_type:
                    recommendations.append(
                        ("SDL2+OpenGL", "Good starting point for 2D/3D graphics with moderate complexity")
                    )
                else:
                    recommendations.append(
                        ("SDL2+OpenGL+GLM", "Complete 3D starter stack with windowing, rendering, and math")
                    )
            else:  # Intermediate/Advanced
                if "3D" in game_type:
                    recommendations.append(
                        ("SDL2+OpenGL+GLM+Assimp+stb_image", "Full 3D game development stack with asset loading")
                    )

                    if scope == "Large/commercial project":
                        recommendations.append(
                            (
                                "SDL2+OpenGL+GLM+Assimp+stb_image+Bullet+Dear ImGui",
                                "Professional 3D game development with physics and debug UI",
                            )
                        )

                if "2D" in game_type:
                    recommendations.append(("SDL2+OpenGL+GLM+stb_image", "Modern 2D development with OpenGL rendering"))

        return recommendations

    def _confirm_setup(self, project_name: str, language: str, tech_stack: str) -> bool:
        """Final confirmation of setup choices."""
        print_info("\\nStep 4: Review Your Choices")
        print(f"  Project Name: {project_name}")
        print(f"  Language: {language}")
        print(f"  Tech Stack: {tech_stack}")

        # Analyze the final tech stack to show what will be included
        analysis = self.tech_stack_manager.parse_tech_stack(tech_stack, language)

        if analysis.libraries:
            print("\\n  Selected Libraries:")
            for lib in analysis.libraries:
                print(f"    - {lib.display_name} ({lib.category.value})")

        if analysis.warnings:
            print("\\n  Recommendations:")
            for warning in analysis.warnings:
                print(f"    - {warning}")

        print("")
        return confirm_action("Create project with these settings?", default=True)


# Global instance
setup_wizard = SetupWizard()
