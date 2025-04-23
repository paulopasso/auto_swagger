from git import Repo
from pathlib import Path
from typing import List
from .models import Change
from .config import GitConfig

class GitHandler:
    """Handles all git-related operations for the swagger documentation updates."""
    
    def __init__(self, repo_path: Path, config: GitConfig):
        self.repo = Repo(str(repo_path))
        self.config = config
        
    def setup_branch(self) -> None:
        """Sets up the git branch for changes."""
        if self.config.branch_name in self.repo.heads:
            branch = self.repo.heads[self.config.branch_name]
        else:
            branch = self.repo.create_head(self.config.branch_name)
        branch.checkout()
        
    def commit_changes(self, successful_changes: List[Change]) -> None:
        """Commits the successful changes to the repository."""
        if not successful_changes:
            return
            
        # Convert Path objects to strings if needed
        file_paths = [str(change.filepath) for change in successful_changes]
        self.repo.index.add(file_paths)
        
        commit_message = f"{self.config.commit_message}\n\n" + \
                        "\n".join(f"- {change.description}" for change in successful_changes)
        self.repo.index.commit(commit_message)
        print("\nChanges committed successfully!") 