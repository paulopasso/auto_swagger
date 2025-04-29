from pathlib import Path
from typing import List, Set

from git import Repo

from .generator_config import GitConfig
from .models import Change


class GitHandler:
    """Handles git-related operations for tracking and managing changes."""

    def __init__(self, repo_path: Path, config: GitConfig):
        """Initialize GitHandler with repository path and configuration.

        Args:
            repo_path: Path to the git repository
            config: GitConfig object containing configuration settings
        """
        self.repo = Repo(repo_path)
        self.config = config

    def setup_branch(self) -> None:
        """Sets up the git branch for changes."""
        if self.config.branch_name in self.repo.heads:
            branch = self.repo.heads[self.config.branch_name]
        else:
            branch = self.repo.create_head(self.config.branch_name)
        branch.checkout()

    def get_unmerged_files(self, branch_name: str | None = None) -> Set[str]:
        """Get files that have been changed in specified branch but not merged to main.

        Args:
            branch_name: Optional branch name to check. If None, uses current branch.

        Returns:
            Set of file paths that have been modified but not merged
        """
        print("\nDebug: Starting unmerged files check")

        # Get the main/master branch
        main_branch = (
            self.repo.heads["main"]
            if "main" in self.repo.heads
            else self.repo.heads["master"]
        )
        print(f"Debug: Main branch: {main_branch.name}")

        # Get the branch to check
        if branch_name:
            if branch_name not in self.repo.heads:
                raise ValueError(f"Branch '{branch_name}' not found")
            current = self.repo.heads[branch_name]
            if current != self.repo.active_branch:
                print(
                    f"Debug: Checking branch '{branch_name}' (different from current branch)"
                )
        else:
            current = self.repo.active_branch
        print(f"Debug: Checking branch: {current.name}")

        # Find the merge-base
        merge_base = self.repo.merge_base(current, main_branch)
        print(f"Debug: Merge base found: {bool(merge_base)}")

        if not merge_base:
            print("Debug: No merge base found, returning empty set")
            return set()

        base_commit = merge_base[0]
        print(f"Debug: Base commit hash: {base_commit.hexsha[:8]}")

        # Get diffs between merge-base and current branch
        diffs = self.repo.git.diff(
            "--name-only", base_commit.hexsha, current.commit.hexsha
        ).split("\n")

        changed_files: Set[str] = set(f for f in diffs if f.strip())
        print(f"Debug: Found {len(changed_files)} changed files")

        return changed_files

    def commit_changes(self, successful_changes: List[Change]) -> None:
        """Commits the successful changes to the repository."""
        if not successful_changes:
            return

        self.repo.index.add([change.filepath for change in successful_changes])
        commit_message = f"{self.config.commit_message}\n\n" + "\n".join(
            f"- {change.description}" for change in successful_changes
        )
        self.repo.index.commit(commit_message)
        print("\nChanges committed successfully!")
