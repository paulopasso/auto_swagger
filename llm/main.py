from transformers import AutoTokenizer, AutoModelForCausalLM
from git import Repo
import json
from pydantic import BaseModel
from typing import List
import os
import torch

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
        "filename": "swagger-example/src/app.js",
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
    return f"""You are an expert in API documentation. Given the API context below, generate JSDoc Swagger documentation comments for the existing Express.js routes.

Rules:
1. ONLY output JSDoc comments starting with /** and ending with */
2. Include @swagger annotations for each endpoint
3. DO NOT include any actual route code or implementation
4. DO NOT suggest creating new files
5. DO NOT modify existing code
6. Each change should ONLY contain JSDoc documentation comments

The response MUST be a valid JSON object in this exact format:
{{
  "changes": [
    {{
      "start_line": number,      // Line number where the JSDoc comment should start
      "end_line": number,        // Line number where the existing route starts (exclusive)
      "filepath": string,        // Path to the file containing the route
      "code": string,           // ONLY the JSDoc Swagger documentation comment
      "description": string     // Brief description of the documentation added
    }}
  ]
}}

API Context:
{context}"""

def extract_json_from_response(response) -> Changes | None:
    try:
        # Get the generated text from the response
        text = response[0]['generated_text']
        
        print("\nDebug - Full response text:")
        print(text)
        
        # Find the JSON between markdown code blocks
        start_marker = "```json"
        if start_marker not in text:
            start_marker = "```"  # Fallback if json tag is not specified
            
        json_start = text.find(start_marker)
        if json_start == -1:
            # Fallback to looking for just a JSON object if no code blocks found
            json_start = text.find('{')
            if json_start == -1:
                raise ValueError("No JSON found in response")
            json_text = text[json_start:]
        else:
            # Extract text between ``` markers
            json_start = text.find('{', json_start)
            json_end = text.find('```', json_start)
            json_text = text[json_start:json_end].strip() if json_end != -1 else text[json_start:].strip()
        
        print("\nDebug - Extracted JSON text:")
        print(json_text)
        
        # Parse JSON and validate with Pydantic
        json_data = json.loads(json_text)
        
        print("\nDebug - Parsed JSON data:")
        print(json_data)
        
        return Changes(**json_data)
        
    except Exception as e:
        print(f"\nError extracting JSON from response: {e}")
        if 'text' in locals():
            print("\nRaw text that caused the error:")
            print(text)
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
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            "deepseek-ai/deepseek-coder-1.3b-instruct",  
            trust_remote_code=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            "deepseek-ai/deepseek-coder-1.3b-instruct",  
            trust_remote_code=True,
            torch_dtype=torch.bfloat16  
        )
        
        # Move to GPU if available
        device = torch.device("mps" if torch.mps.is_available() else "cpu")
        model = model.to(device)
        
        # Format as chat messages
        messages = [
            {'role': 'user', 'content': prompt}
        ]
        
        # Apply chat template and generate
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(device)
        
        outputs = model.generate(
            inputs,
            max_new_tokens=4096,
            do_sample=False,
            top_k=50,
            top_p=0.95,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id
        )
        
        # Get the generated text (exactly as in docs)
        generated_text = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        
        # Create response format matching pipeline output for compatibility
        response = [{"generated_text": generated_text}]
        print("\nRaw response:")
        print(response)
        
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

if __name__ == "__main__":
    main()