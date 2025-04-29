# Auto Swagger Documentation Generator

A sophisticated tool that automatically generates Swagger/OpenAPI documentation for Express.js APIs using advanced NLP techniques and LLMs.

## Overview

This project combines Natural Language Processing (NLP) techniques with Large Language Models (LLMs) to automatically generate high-quality API documentation. By preprocessing code with NLP before sending it to LLMs, we achieve:

- Better context understanding
- Reduced token usage
- More specific and higher quality responses
- Fine-grained control over the documentation pipeline
- Automated code base updates

## Features

- Automatic API route detection
- Intelligent parameter inference
- Response schema generation
- Validation rules detection
- Swagger/OpenAPI compliant output
- Support for Express.js routes
- Automated documentation insertion

## Architecture

### 1. Initial Code Processing

- Git Diff Detection
  - Identify changed files
- Code Extraction
  - Extract route handlers
  - Extract existing comments
- Basic Preprocessing
  - Remove unnecessary whitespace
  - Normalize line endings

### 2. NLP Analysis Pipeline

- CodeBERT Processing
  - Generate code embeddings
  - Semantic code understanding
- Token Classification
  - CRUD operation detection
  - API endpoint classification
- Named Entity Recognition (NER)
  - Route paths
  - HTTP methods
  - Variable names
  - Function names
  - Status codes
- Semantic Role Labeling
  - Action identification
  - Resource detection
  - Parameter role assignment

### 3. Pattern Recognition & Documentation Analysis

- Transformer Model Analysis
  - CRUD patterns
  - Authentication flows
  - Error handling
  - Data validation
- Information Extraction
  - Parameter types
  - Validation rules
  - Response formats
- Constraint Detection
  - Required fields
  - Validation rules

### 4. LLM Integration & Code Update

- Prompt Generation
- Documentation Generation
- Code Base Updates

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auto_swagger.git
cd auto_swagger
```

2. Install UV if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create a virtual environment and install dependencies:
```bash
uv venv
```

4. Run the auto-swagger tool:
```bash
# Run the main documentation generator
uv run auto-swagger --repo-path path/to/express/app

# Run the fine-tuning tool (if needed)
uv run finetune
```

## Project Structure

```
auto_swagger/
├── src/
│   └── auto_swagger/         # Source code
│       ├── config/          # Configuration management
│       ├── finetune/        # Model fine-tuning utilities
│       ├── parser/          # Code parsing and analysis
│       └── swagger_generator/ # Documentation generation
├── data/                    # Project data
│   ├── jsdocs_finetune.jsonl # Fine-tuning dataset
│   └── swagger_docs/        # Generated documentation
├── pyproject.toml          # Project configuration
└── README.md
```

## Configuration

The project uses a config to change the model you want:

```python
@dataclass
class LLMConfig:
    model_name: str = "deepseek-ai/deepseek-coder-1.3b-instruct"
    max_new_tokens: int = 8192
    temperature: float = 0.2
    top_k: int = 50
    top_p: float = 0.95
    max_retries: int = 3
```

## Future Improvements

- Support for additional backend frameworks beyond Express.js
- Local CLI version without GitHub app dependency
- Enhanced pattern recognition
- Additional documentation formats
- Real-time documentation updates