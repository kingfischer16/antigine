# Fix Broken Imports

Please help fix import statements that broke after moving, editing, or renaming files.

First, analyze the project structure and identify any broken imports. Do this by:

1. **Detecting the project type** from file patterns and configurations
2. **Identify import/include patterns** specific to the project language
3. **Check which imports are broken** by verifying if referenced files exist
4. **Find where files were moved** by searching for matching filenames

Based on what you find, you should:
- Detect the import patterns used in the project
- Handle the specific syntax for the project language
- Preserve the existing code style and formatting

For each broken import, please:
1. Show the broken import with its location
2. Search for the moved/renamed file
3. Check for ambiguous matches

**For ambiguous cases:**
- List all possible options
- Show the context
- Ask which file is the correct target
- Never guess when unsure

**Error handling:**
- Report why the import cannot be resolved
- Continue with other fixable imports
- Suggest manual fixes if needed

After fixing imports:
- Verify the syntax is correct
- Ensure no new conflicts were introduced
- Report summary of changes made

This ensures your code continues to work after file reorganization with safety and clarity.
