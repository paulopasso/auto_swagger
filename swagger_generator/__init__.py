"""
Swagger documentation generator package.

This package provides functionality to automatically generate Swagger documentation
for API endpoints using LLM-powered code analysis.
"""

from .config import Config, LLMConfig, GitConfig
from .models import Change
from .git_handler import GitHandler
from .file_handler import FileHandler
from .llm_handler import LLMHandler

__version__ = "0.1.0"
__all__ = [
    "Config",
    "LLMConfig",
    "GitConfig",
    "Change",
    "CodeContext",
    "APIContext",
    "GitHandler",
    "FileHandler",
    "LLMHandler",
] 