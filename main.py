import argparse
import json
from datetime import datetime
from parser.parser import ApiDocParser
from pathlib import Path
from typing import Set

from swagger_generator.config import Config
from swagger_generator.file_handler import FileHandler
from swagger_generator.git_handler import GitHandler
from swagger_generator.llm_handler import LLMHandler
from swagger_generator.models import Change


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


def save_parser_output(
    api_context: dict, changed_files: Set[str], repo_path: str
) -> None:
    """Save parser output to a JSON file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Add more debug information
    output = {
        "timestamp": timestamp,
        "changed_files": list(changed_files),
        "repo_path": str(repo_path),
        "file_details": [
            {
                "file": file,
                "full_path": str(Path(repo_path) / file),
                "exists": Path(repo_path).joinpath(file).exists(),
            }
            for file in changed_files
        ],
        "parser_output": api_context,
        "parser_output_type": str(type(api_context)),
    }

    output_dir = Path("debug_output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"parser_output_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nParser output saved to: {output_file}")

    # Print summary of saved data
    print("\nOutput Summary:")
    print(f"- Number of changed files: {len(changed_files)}")
    print(f"- Parser output type: {type(api_context)}")
    print(
        f"- Parser output keys: {list(api_context.keys()) if isinstance(api_context, dict) else 'N/A'}"
    )


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

        api_context = ApiDocParser.parse_files(full_paths)  # Use full paths
        print("\nParser output summary:")
        print(
            f"Context keys: {list(api_context.keys()) if api_context else 'Empty context'}"
        )

        # Enhanced parser output saving
        save_parser_output(api_context, changed_files, args.repo_path)

        # Generate documentation using LLM
        changes = llm_handler.generate_documentation(api_context)

        # Process and commit changes
        process_changes(changes, git_handler)

    except Exception as e:
        print(f"\nError during execution: {e}")
        raise


if __name__ == "__main__":
    main()
