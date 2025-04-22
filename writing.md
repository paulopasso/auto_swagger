### Our preprocessing steps

From our code snippets from before we need to be able to accomplish the following:

1. Look at git diff for the new changes made to the project
2. Look at the Existing documentation using regex for the specific language like jsdoc in our case
3. Process our code to generate embeddings to enable semantic code understanding using codeBert
5. Utilise token classiciation with CodeBert to understand CRUD operation detection and API endpoint classification
6. NER for key parts of what constitutes an API: Route paths, HTTP methods, path variable, query params, function names, status codes
7. Pattern recognition for the types of routes we are making like if it is a CRUD pattern, auth flow, error handling, data validation
8. Structure our data for the prompt
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
9. Send our prompt to the LLM and ask for the specific output
  - Comments in the specific integration used (like jsdoc)
  - Comments made in a separate commit for diffs

# Preprocessing for API Documentation: A Pragmatic NLP Approach

Automating API documentation through targeted NLP techniques offers a powerful solution to the persistent challenge of maintaining up-to-date technical documentation. By focusing on efficient preprocessing steps, we can extract the essential information from code changes without requiring the computational overhead of full semantic understanding. This essay examines a streamlined approach to preprocessing code for API documentation generation.

## Change Detection and Context Gathering

The preprocessing pipeline begins with git diff analysis to isolate recent code changes. This targeted approach ensures we focus documentation efforts only on modified components, significantly reducing the processing scope compared to analyzing the entire codebase. By examining line-by-line changes, we can identify new or modified API endpoints, parameter changes, and response modifications.

Complementing this change detection, regex pattern matching extracts existing documentation conventions like JSDoc comments. This step serves two purposes: preserving documentation continuity by understanding the established style, and identifying gaps where documentation is missing or incomplete. Regular expressions tailored to the specific documentation format can efficiently extract method descriptions, parameter annotations, return value documentation, and other structured elements.

## Token Classification and Entity Recognition

Token classification forms the backbone of our preprocessing approach. Without delving into complex semantic analysis, we can train lightweight classifiers to categorize code elements into API-relevant components. This classification identifies HTTP method declarations, route definitions, middleware functions, and handler implementations. For JavaScript/Node.js applications, this might involve recognizing patterns like `app.get('/path', handler)` or Express router configurations.

Named Entity Recognition (NER) extends this classification to extract specific entities crucial for documentation:
- Route paths (e.g., `/api/users/:id`)
- HTTP methods (GET, POST, PUT, DELETE)
- Path variables (parameters embedded in URLs)
- Query parameters (optional URL parameters)
- Function names (handler functions for routes)
- Status codes (response codes in error handling)

These entities provide the raw material for comprehensive documentation. By training NER models on API code examples, we can achieve high accuracy in extracting these elements even when they appear in varied contexts or coding styles.

## Pattern Recognition for API Structures

Beyond individual entities, pattern recognition identifies common API structures that follow established conventions. This recognition includes:
- CRUD operations (Create, Read, Update, Delete endpoints for resources)
- Authentication flows (login, token validation, refresh mechanisms)
- Error handling patterns (try/catch blocks, error middleware)
- Data validation approaches (schema validation, input sanitization)

By recognizing these patterns, we can apply template-based documentation that captures the standard behaviors associated with each pattern. For instance, a recognized user creation endpoint might automatically receive documentation about required fields, password handling, and duplicate user checks based on the identified pattern.

## Data Structuring for Effective Prompting

The extracted information must be organized systematically before prompting a language model. Our structured format includes:
- **Endpoint Information**: Path, method, and resource type
- **Parameters**: Path parameters, query parameters, and request body structure
- **Responses**: Success scenarios with response schemas and error cases with status codes
- **Validation**: Input constraints and business rules

This structured approach ensures the language model receives complete context about the API endpoint without extraneous information. The organization mirrors standard API documentation formats, making it easier for the model to generate appropriate documentation.

## Prompt Construction and Output Formatting

The final preprocessing step involves constructing effective prompts for the language model. These prompts combine the structured API information with explicit instructions about documentation format. For JSDoc comments, the prompt specifies the required syntax for method descriptions, parameter annotations, return values, and examples. For separate documentation files, the prompt might request markdown formatting with appropriate headers, code examples, and response schemas.

Here's an example of the structured data that would be sent to the language model after preprocessing:

```javascript
const promptData = {
  "codeContext": {
    "filename": "src/routes/users.js",
    "functionName": "createUser",
    "existingComments": "// Creates a new user in the database"
  },
  "apiDetails": {
    "endpoint": {
      "path": "/api/users",
      "method": "POST",
      "resourceType": "User"
    },
    "parameters": {
      "body": {
        "username": { "type": "string", "required": true },
        "email": { "type": "string", "required": true },
        "password": { "type": "string", "required": true },
        "role": { "type": "string", "enum": ["user", "admin"], "default": "user" }
      }
    },
    "responses": {
      "success": {
        "statusCode": 201,
        "description": "User created successfully",
        "schema": {
          "type": "object",
          "properties": {
            "id": { "type": "string", "description": "Unique identifier for the user" },
            "username": { "type": "string", "description": "User's chosen username" },
            "email": { "type": "string", "format": "email", "description": "User's email address" },
            "role": { "type": "string", "enum": ["user", "admin"], "description": "User's role in the system" },
            "createdAt": { "type": "string", "format": "date-time", "description": "Timestamp when user was created" }
          },
          "required": ["id", "username", "email", "role", "createdAt"]
        }
      },
      "errors": [
        {
          "statusCode": 400,
          "description": "Invalid input parameters",
          "conditions": ["Missing required fields", "Invalid email format"]
        },
        {
          "statusCode": 409,
          "description": "Conflict",
          "conditions": ["Username already exists", "Email already registered"]
        }
      ]
    },
    "validation": {
      "inputConstraints": [
        "Username must be 3-20 characters",
        "Email must be valid format",
        "Password must be at least 8 characters"
      ],
      "businessRules": [
        "Users with admin role require approval",
        "Passwords are hashed before storage"
      ]
    },
    "detectedPattern": "USER_CREATION"
  },
  "requestedFormat": {
    "style": "JSDoc",
    "includeSchemas": true,
    "includeErrorCases": true
  }
}
```

By constraining the output format through explicit instructions, we ensure the generated documentation integrates seamlessly with existing documentation systems. This approach leverages the language model's natural language capabilities while preventing stylistic inconsistencies that might arise from unconstrained generation.

## Conclusion

This preprocessing pipeline demonstrates how targeted NLP techniques can extract the essential information needed for API documentation without requiring complex semantic understanding of code. By focusing on change detection, token classification, entity recognition, pattern matching, and structured data organization, we create a robust foundation for generating accurate and useful API documentation.

The approach balances efficiency with effectiveness, recognizing that the primary goal is practical assistance in documentation rather than perfect automation. Through these preprocessing techniques, development teams can significantly reduce the documentation burden while maintaining high-quality API references that support effective integration and use.