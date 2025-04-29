import argparse
from auto_swagger.parser.parser import ApiDocParser
from pathlib import Path

from auto_swagger.swagger_generator.generator_config import Config
from auto_swagger.swagger_generator.file_handler import FileHandler
from auto_swagger.swagger_generator.git_handler import GitHandler
from auto_swagger.swagger_generator.llm_handler import LLMHandler
from auto_swagger.swagger_generator.models import Change


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Swagger documentation for API endpoints."
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        help="Path to the repository root",
        default=str(Path.cwd()),
    )
    parser.add_argument(
        "--branch",
        type=str,
        help="Branch to check for unmerged changes (defaults to current branch)",
        default=None,
    )
    return parser.parse_args()


def process_changes(changes: list[Change], git_handler: GitHandler) -> None:
    """Process and commit the generated changes."""
    if not changes:
        return

    print("\nProposed changes:")
    for change in changes:
        print(f"\nFile: {change.filepath}")
        print(f"Start line: {change.start_line}")
        print(f"Description: {change.description}")
        print("Code:")
        print(change.code)

    successful_changes = []
    file_handler = FileHandler(str(git_handler.repo.working_dir))

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


def parse_files_with_context(file_paths: list[str], repo_path: str) -> list:
    """Parse files with repository context for proper relative paths.
    
    Args:
        file_paths: List of absolute file paths to parse
        repo_path: Path to the repository root
        
    Returns:
        list: Flattened list of API documentation objects, matching context.py format
    """
    all_routes = []
    for filepath in file_paths:
        if ApiDocParser.is_api_file(filepath):
            try:
                # Create parser with repo context for proper relative paths
                parser = ApiDocParser(filepath, repo_root=repo_path)
                docs = parser.extract_api_info()
                if docs:  # Only include if API docs were found
                    # Append each route to the flattened list
                    all_routes.extend(docs)
            except Exception as e:
                print(f"Error parsing {filepath}: {str(e)}")
    return all_routes


def main():
    try:
        # Parse command line arguments
        args = parse_args()
        print(f"\nRepository path: {args.repo_path}")
        print(f"Branch to check: {args.branch or 'current branch'}")

        # Initialize configuration
        config = Config.create(args.repo_path)

        # Create handlers
        git_handler = GitHandler(config.repo_path, config.git)
        llm_handler = LLMHandler(config.llm)

        # Setup git branch (only if we're using the current branch)
        if not args.branch:
            print("\nSetting up git branch...")
            git_handler.setup_branch()
            print(f"Current branch: {git_handler.repo.active_branch.name}")

        # Get changed files from git
        print("\nChecking for unmerged files...")
        changed_files = git_handler.get_unmerged_files(args.branch)
        print(f"Found {len(changed_files)} unmerged files:")
        for file in changed_files:
            print(f"- {file}")
            # Add file existence check
            file_path = Path(args.repo_path) / file
            if not file_path.exists():
                print(f"  WARNING: File not found at {file_path}")
            else:
                print(f"  File exists at {file_path}")

        if not changed_files:
            print("No files to process. Exiting.")
            return

        # Parse changed files for API documentation
        print("\nParsing files for API documentation...")
        full_paths = [str(Path(args.repo_path) / f) for f in changed_files]
        print("Files to parse:")
        for path in full_paths:
            print(f"- {path}")

        # Use parse_files_with_context to get flattened array of routes
        api_context = parse_files_with_context(full_paths, args.repo_path)
        print(f"\nFound {len(api_context)} API routes to document")

        # Generate documentation using LLM
        changes = llm_handler.generate_documentation(api_context)

        # Process and commit changes
        process_changes(changes, git_handler)

    except Exception as e:
        print(f"\nError during execution: {e}")
        raise


if __name__ == "__main__":
    main() 