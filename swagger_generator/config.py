from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class LLMConfig:
    model_name: str = "deepseek-ai/deepseek-coder-1.3b-instruct"
    max_new_tokens: int = 8192
    temperature: float = 0.2
    top_k: int = 50
    top_p: float = 0.95
    max_retries: int = 3

@dataclass
class GitConfig:
    branch_name: str = "swagger-docs-update"
    commit_message: str = "Add Swagger documentation"

@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    git: GitConfig = field(default_factory=GitConfig)
    repo_path: Optional[Path] = None

    @classmethod
    def create(cls, repo_path: Optional[str] = None) -> 'Config':
        return cls(
            repo_path=Path(repo_path) if repo_path else None
        ) 