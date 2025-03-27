### Our process

The PURPOSE of doing these NLP techniques before hand is that it allows for better context understanding for the LLM and reduced toke usage from it. Furthermore, as it is more specific it allows for the responses to be higher quality. By having more fine grain control in this pipeline we also get more control in WHAT we can do with the response of the data. So then, we can put these changes automatically in the codebase.

1. Initial Code Processing

   - Git Diff Detection
     - Identify changed files
   - Code Extraction
     - Extract route handlers
     - Extract existing comments
   - Basic Preprocessing
     - Remove unnecessary whitespace
     - Normalize line endings

2. NLP Analysis Pipeline

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

3. Pattern Recognition

   - Transformer Model Analysis
     - CRUD patterns
     - Authentication flows
     - Error handling
     - Data validation
   - Context Understanding
     - Request/Response patterns
     - Parameter relationships

4. Documentation Analysis

   - Comment Classification
     - Parameter descriptions
     - Return values
     - Error documentation
   - Information Extraction
     - Parameter types
     - Validation rules
     - Response formats
   - Constraint Detection
     - Required fields
     - Validation rules

5. Structured Data Creation

   - Endpoint Information
     - Path
     - Method
     - Resource type
   - Parameters
     - Path parameters
     - Query parameters
     - Request body
   - Responses
     - Success scenarios
     - Error cases
   - Validation
     - Input constraints
     - Business rules

6. LLM Integration

   - Prompt Generation
     - Context building
     - Template selection
   - LLM Processing
     - Documentation generation
     - Validation rules
   - Output Formatting
     - OpenAPI specification
     - Swagger YAML

7. Code Update
   - Generate documentation
     - Update existing docs
     - Create new docs

### Future improvements

- Extend to multiple backend frameworks not just expressjs (which is the most popular)
- We could make a local cli version that works without making a github app
