from pathlib import Path
from typing import List, Union
from .models import Change

class FileHandler:
    """Handles all file operations for the swagger documentation updates."""
    
    def __init__(self, repo_path: Union[str, Path]):
        """
        Initialize the FileHandler with the repository base path.
        
        Args:
            repo_path: The absolute path to the repository root
        """
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")
    
    def apply_changes(self, change: Change) -> bool:
        """
        Applies changes to a file at specific line numbers while preserving spacing and context.
        Handles both absolute and relative paths.
        
        Args:
            change: Change object containing the file modifications
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert the filepath to a Path object if it's a string
            change_path = Path(change.filepath)
            
            # If the path is relative, make it absolute using the repo path
            if not change_path.is_absolute():
                filepath = (self.repo_path / change_path).resolve()
            else:
                filepath = change_path.resolve()
            
            # Verify the file exists and is within the repository
            if not filepath.exists():
                raise FileNotFoundError(
                    f"The file specified does not exist: {filepath}"
                )
                
            if not str(filepath).startswith(str(self.repo_path)):
                raise ValueError(
                    f"File path {filepath} is outside the repository: {self.repo_path}"
                )
            
            # Read existing content
            lines = filepath.read_text().splitlines(keepends=True)
            
            # Process the new code lines
            new_code_lines = [
                f"{line}\n" if line.strip() else "\n"
                for line in change.code.split('\n')
            ]
            
            # Insert the new lines at the correct position
            lines = lines[:change.start_line] + new_code_lines + lines[change.start_line:]
            
            # Write back to file
            filepath.write_text("".join(lines))
            return True
            
        except Exception as e:
            print(f"Error applying changes to {change.filepath}: {e}")
            return False 