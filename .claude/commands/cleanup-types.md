# Cleanup Loose Types

Please help improve type safety in our code by finding and fixing loose type declarations.

First, analyze our project to understand what needs attention. Please look for:
 - Loose or generic type declarations
 - Missing type annotations where the project language supports them
 - Overly permissive types that could be more specific
 - Type assertions that might hide issues
 - Functions without proper type signatures

If available, please use mypy to look for and type annotation issues. This usually captures all of them. For each typing issue found:
 1. Show the current code with context
 2. Analyze how the value is actually used
 3. Suggest a more specific type based on usage patterns
 4. Explain why the suggested type is better
 5. Apply the change after user confirmation

Your approach to cleaning up type hints must prioritize:
- **Safety**: Never break existing functionality
- **Clarity**: Make types self-documenting
- **Maintainability**: Use types that prevent future bugs
- **Project conventions**: Follow your existing type patterns

This helps catch bugs at compile-time rather than runtime, making your code more robust and easier to maintain.
