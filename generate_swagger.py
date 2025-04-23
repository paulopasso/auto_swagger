#!/usr/bin/env python
import argparse
import os
import sys
from pathlib import Path
import json
from typing import List, Dict, Any

# Add the swagger_generator package to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from swagger_generator.config import Config
from swagger_generator.llm_handler import LLMHandler
from swagger_generator.file_handler import FileHandler
from swagger_generator.git_handler import GitHandler
from swagger_generator.models import Change

def find_api_files(repo_path: Path) -> List[Path]:
    """Find potential API files in the repository."""
    api_files = []
    for ext in ['.js', '.ts']:
        for file_path in repo_path.glob(f'**/*{ext}'):
            # Skip node_modules and other irrelevant directories
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue
                
            # Read the file content and look for API route patterns
            content = file_path.read_text()
            if any(pattern in content for pattern in ['app.get', 'app.post', 'router.get', 'router.post', 'app.use', 'express.Router']):
                api_files.append(file_path)
    
    return api_files

def extract_route_contexts(file_paths: List[Path]) -> List[Dict[str, Any]]:
    """Extract API route contexts from files."""
    contexts = []
    
    for file_path in file_paths:
        content = file_path.read_text()
        lines = content.split('\n')
        
        # Simple heuristic to find routes
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for route definitions
            if any(pattern in line for pattern in ['app.get', 'app.post', 'app.put', 'app.delete', 'router.get', 'router.post']):
                route_path = line.split("'")[1] if "'" in line else line.split('"')[1] if '"' in line else None
                
                if route_path:
                    # Get surrounding code for context
                    start_idx = max(0, i - 5)
                    end_idx = min(len(lines), i + 15)
                    code_context = '\n'.join(lines[start_idx:end_idx])
                    
                    # Extract method from the line
                    method = 'get' if '.get' in line else 'post' if '.post' in line else 'put' if '.put' in line else 'delete'
                    
                    # Convert Path to string for JSON serialization
                    contexts.append({
                        'codeContext': {
                            'filename': str(file_path),  # Convert Path to string
                            'code': code_context,
                            'line': {
                                'beginning': start_idx + 1  # 1-indexed for human readability
                            }
                        },
                        'routeInfo': {
                            'path': route_path,
                            'method': method
                        }
                    })
    
    return contexts

def main():
    parser = argparse.ArgumentParser(description='Generate Swagger documentation for an Express.js API')
    parser.add_argument('--repo', type=str, default='.', help='Path to the repository')
    parser.add_argument('--commit', action='store_true', help='Commit changes to git')
    args = parser.parse_args()
    
    repo_path = Path(args.repo).resolve()
    
    # Initialize configuration
    config = Config.create(str(repo_path))
    
    # Find API files
    print(f"Scanning repository at {repo_path}...")
    api_files = find_api_files(repo_path)
    print(f"Found {len(api_files)} potential API files:")
    for file in api_files:
        print(f"  - {file.relative_to(repo_path)}")
    
    # Extract route contexts
    contexts = extract_route_contexts(api_files)
    print(f"\nExtracted {len(contexts)} API routes for documentation")
    
    # Initialize handlers
    llm_handler = LLMHandler(config.llm)
    file_handler = FileHandler(repo_path)
    
    # Generate documentation
    print("\nGenerating Swagger documentation...")
    changes = llm_handler.generate_documentation(contexts)
    
    if not changes:
        print("\nFailed to generate documentation")
        return
    
    print(f"\nGenerated documentation for {len(changes)} routes")
    
    # Apply changes
    successful_changes = []
    for change in changes:
        print(f"\nApplying changes to {change.filepath} at line {change.start_line}:")
        print(f"  {change.description}")
        
        if file_handler.apply_changes(change):
            successful_changes.append(change)
            print("  ✅ Success")
        else:
            print("  ❌ Failed")
    
    # Commit changes if requested
    if args.commit and successful_changes:
        git_handler = GitHandler(repo_path, config.git)
        git_handler.setup_branch()
        git_handler.commit_changes(successful_changes)
        print(f"\nCommitted changes to branch '{config.git.branch_name}'")
    
    print("\nDone!")

if __name__ == '__main__':
    main() 