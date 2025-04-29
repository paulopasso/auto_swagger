from dataclasses import dataclass

@dataclass
class Change:
    """Represents a change to be made to a file."""
    start_line: int
    filepath: str
    code: str
    description: str