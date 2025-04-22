import argparse
from pathlib import Path
from typing import Optional
from swagger_generator.config import Config
from swagger_generator.models import Change
from swagger_generator.git_handler import GitHandler
from swagger_generator.file_handler import FileHandler
from swagger_generator.llm_handler import LLMHandler
#FIXME: Remove this line hardcoded for testing
from context import get_context

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate Swagger documentation for API endpoints.')
    parser.add_argument(
        '--repo-path',
        type=str,
        help='Path to the repository root',
        default=str(Path.cwd())
    )
    return parser.parse_args()

def process_changes(changes: list[Change], git_handler: GitHandler) -> None:
    """Process and commit the generated changes."""
    if not changes:
        return
    
    # Sort changes by filepath and line number
        
    print("\nProposed changes:")
    for change in changes:
        print(f"\nFile: {change.filepath}")
        print(f"Start line: {change.start_line}")
        print(f"Description: {change.description}")
        print("Code:")
        print(change.code)
    
    successful_changes = []
    file_handler = FileHandler(git_handler.repo.working_dir)
    
    # Apply changes
    for change in changes:
        print(f"\nApplying changes to: {change.filepath}")
        print(f"Start line: {change.start_line}")
        print(f"Description: {change.description}")
        
        if file_handler.apply_changes(change):
            successful_changes.append(change)
            print("✓ Changes applied successfully")
        else:
            print("✗ Failed to apply changes")
    
    # Commit successful changes
    if successful_changes:
        git_handler.commit_changes(successful_changes)

def main():
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Initialize configuration
        config = Config.create(args.repo_path)
        
        # Create handlers
        git_handler = GitHandler(config.repo_path, config.git)
        llm_handler = LLMHandler(config.llm)
        
        # Setup git branch
        git_handler.setup_branch()
        
        # Get API context
        context = get_context()
        
        # Generate documentation
        changes = llm_handler.generate_documentation(context)
        
        # Process and commit changes
        process_changes(changes, git_handler)
        
    except Exception as e:
        print(f"\nError during execution: {e}")
        raise

if __name__ == "__main__":
    main()