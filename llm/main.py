from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from git import Repo
import json
from pydantic import BaseModel
from typing import List
import os

class Change(BaseModel):
    start_line: int      
    end_line: int        
    filepath: str        
    code: str           
    description: str     

class Changes(BaseModel):
    changes: List[Change]

# FIXME: This will be removed integrated with paul's code
def get_context():
  return (
    """
    {
      "codeContext": {
        "filename": "src/app.js",
        "functionName": "CRUD Operations",
        "line": {
          "beginning": 30,
          "end": 140
        },
        "existingComments": "// User Routes, // Item Routes",
        "general_purpose": "This is a complete REST API for managing users and items with CRUD operations"
      },
      "apiDetails": {
        "users": {
          "endpoint": {
            "path": "/api/users",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "resourceType": "User"
          },
          "parameters": {
            "path": {
              "id": { 
                "type": "integer",
                "required": true,
                "description": "User ID for single-resource operations"
              }
            },
            "body": {
              "name": { "type": "string", "required": true },
              "email": { "type": "string", "required": true, "format": "email" }
            }
          },
          "responses": {
            "success": {
              "get_all": {
                "statusCode": 200,
                "description": "List of all users"
              },
              "get_one": {
                "statusCode": 200,
                "description": "Single user details"
              },
              "create": {
                "statusCode": 201,
                "description": "User created successfully"
              },
              "update": {
                "statusCode": 200,
                "description": "User updated successfully"
              },
              "delete": {
                "statusCode": 204,
                "description": "User deleted successfully"
              }
            }
          }
        },
        "items": {
          "endpoint": {
            "path": "/api/items",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "resourceType": "Item"
          },
          "parameters": {
            "path": {
              "id": { 
                "type": "integer",
                "required": true,
                "description": "Item ID for single-resource operations"
              }
            },
            "query": {
              "category": {
                "type": "string",
                "required": false,
                "description": "Filter items by category"
              }
            },
            "body": {
              "name": { "type": "string", "required": true },
              "description": { "type": "string", "required": true },
              "price": { "type": "number", "required": true },
              "category": { "type": "string", "required": false, "default": "uncategorized" }
            }
          },
          "responses": {
            "success": {
              "get_all": {
                "statusCode": 200,
                "description": "List of all items",
                "schema": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "id": { "type": "integer" },
                      "name": { "type": "string" },
                      "description": { "type": "string" },
                      "price": { "type": "number" },
                      "category": { "type": "string" },
                      "createdAt": { "type": "string", "format": "date-time" }
                    }
                  }
                }
              },
              "create": {
                "statusCode": 201,
                "description": "Item created successfully"
              },
              "update": {
                "statusCode": 200,
                "description": "Item updated successfully"
              },
              "delete": {
                "statusCode": 204,
                "description": "Item deleted successfully"
              }
            }
          }
        },
        "common": {
          "errors": [
            {
              "statusCode": 400,
              "description": "Invalid input parameters",
              "conditions": ["Missing required fields", "Invalid field formats"]
            },
            {
              "statusCode": 404,
              "description": "Resource not found",
              "conditions": ["ID does not exist"]
            }
          ],
          "validation": {
            "inputConstraints": [
              "All required fields must be provided for creation",
              "At least one field must be provided for updates",
              "IDs must be valid integers",
              "Email must be in valid format"
            ]
          }
        }
      }
    }
    """
  )

def format_prompt(context):
  return f"""Based on the following API context, propose changes to implement Swagger documentation.
Please respond ONLY with a JSON object in the following exact format, no other text:

{{
  "changes": [
    {{
      "start_line": number,      // The line number where changes should start
      "end_line": number,        // The line number where changes should end
      "filepath": string,        // The full path to the file being modified
      "code": string,           // The complete code snippet including the changes
      "description": string     // Brief description of what the change does
    }}
  ]
}}

For example:
{{
  "changes": [
    {{
      "start_line": 15,
      "end_line": 45,
      "filepath": "src/app.js",
      "code": "/**\\n * @swagger\\n * /api/users:\\n *   post:\\n *     summary: Create user\\n */\\napp.post('/api/users', ...)",
      "description": "Added Swagger documentation for user creation endpoint"
    }}
  ]
}}

Context:
{context}

JSON Response:
"""

def extract_json_from_response(response) -> Changes | None:
  try:
    # Get the generated text from the response
    text = response[0]['generated_text']
    
    # Find the start of the JSON (after our prompt)
    json_start = text.find('{\n')
    if json_start == -1:
      json_start = text.find('{')
    
    if json_start == -1:
      raise ValueError("No JSON found in response")
      
    json_text = text[json_start:]
    
    # Parse JSON and validate with Pydantic
    json_data = json.loads(json_text)
    return Changes(**json_data)
    
  except Exception as e:
    print(f"Error extracting JSON from response: {e}")
    print("Raw response:", text)
    return None

def apply_file_changes(change: Change) -> bool:
    """
    Applies changes to a file at specific line numbers.
    Returns True if successful, False otherwise.
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(change.filepath), exist_ok=True)
        
        # Read existing content or create empty list if file doesn't exist
        lines = []
        if os.path.exists(change.filepath):
            with open(change.filepath, 'r') as f:
                lines = f.readlines()
        
        # Convert the new code to lines
        new_code_lines = change.code.split('\n')
        
        # Ensure lists are long enough
        while len(lines) < change.end_line:
            lines.append('\n')
            
        # Replace the specified lines
        lines[change.start_line - 1:change.end_line] = [line + '\n' for line in new_code_lines]
        
        # Write back to file
        with open(change.filepath, 'w') as f:
            f.writelines(lines)
            
        return True
        
    except Exception as e:
        print(f"Error applying changes to {change.filepath}: {e}")
        return False

def main():
    # Create the context for prompt
    context = get_context()
    
    # Define prompt with explicit JSON structure request
    prompt = format_prompt(context)
    
    print("The current prompt we are using:")
    print(prompt)
    
    # Initialize the pipeline with better parameters for JSON generation
    pipe = pipeline(
        "text-generation",
        model="deepseek-ai/deepseek-coder-1.3b-base",
        max_new_tokens=2048,
        num_return_sequences=1,
        do_sample=True,        # Enable sampling
        temperature=0.7,       # Lower temperature for more focused outputs
        top_p=0.95,           # Nucleus sampling parameter
        top_k=50,             # Top-k sampling parameter
        repetition_penalty=1.1 # Prevent repetitive text
    )
    
    # Generate with error handling
    try:
        response = pipe(prompt)
        changes = extract_json_from_response(response)
        
        if changes:
            print("\nProposed changes:")
            print(changes)
            successful_changes = []
            
            # Create git branch first
            repo = Repo("/Users/danielkumlin/Desktop/University/nlp/project/auto_swagger")
            branch_name = 'swagger-docs-update'
            if branch_name in repo.heads:
                branch = repo.heads[branch_name]
            else:
                branch = repo.create_head(branch_name)
            branch.checkout()
            
            # Apply changes
            for change in changes.changes:
                print(f"\nApplying changes to: {change.filepath}")
                print(f"Lines {change.start_line}-{change.end_line}")
                print(f"Description: {change.description}")
                
                if apply_file_changes(change):
                    successful_changes.append(change)
                    print("✓ Changes applied successfully")
                else:
                    print("✗ Failed to apply changes")
            
            # Commit changes if any were successful
            if successful_changes:
                repo.index.add([change.filepath for change in successful_changes])
                repo.index.commit("Add Swagger documentation\n\n" + 
                                "\n".join(f"- {change.description}" for change in successful_changes))
                print("\nChanges committed successfully!")
            
        else:
            print("Failed to generate valid JSON response")
            
    except Exception as e:
        print(f"Error during execution: {e}")