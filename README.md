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

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```


4. Command line usage:
```bash
python -m main --repo-path path/to/express/app
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