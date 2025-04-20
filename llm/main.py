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
    return [
        # User Routes
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Create User",
                "line": {
                    "beginning": 39,
                    "end": 55
                },
                "general_purpose": "Create a new user with name and email"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users",
                        "methods": ["POST"],
                        "resourceType": "User"
                    },
                    "parameters": {
                        "body": {
                            "name": { "type": "string", "required": True },
                            "email": { "type": "string", "required": True, "format": "email" }
                        }
                    },
                    "responses": {
                        "success": {
                            "create": {
                                "statusCode": 201,
                                "description": "User created successfully"
                            }
                        },
                        "error": {
                            "400": {
                                "description": "Invalid input parameters",
                                "conditions": ["Missing required fields"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Get All Users",
                "line": {
                    "beginning": 57,
                    "end": 59
                },
                "general_purpose": "Retrieve all users"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users",
                        "methods": ["GET"],
                        "resourceType": "User"
                    },
                    "responses": {
                        "success": {
                            "get_all": {
                                "statusCode": 200,
                                "description": "List of all users"
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Get User by ID",
                "line": {
                    "beginning": 61,
                    "end": 68
                },
                "general_purpose": "Retrieve a specific user by their ID"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users/{id}",
                        "methods": ["GET"],
                        "resourceType": "User"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "User ID"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "get_one": {
                                "statusCode": 200,
                                "description": "Single user details"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "User not found",
                                "conditions": ["ID does not exist"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Update User",
                "line": {
                    "beginning": 70,
                    "end": 89
                },
                "general_purpose": "Update a user's information"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users/{id}",
                        "methods": ["PUT"],
                        "resourceType": "User"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "User ID"
                            }
                        },
                        "body": {
                            "name": { "type": "string", "required": False },
                            "email": { "type": "string", "required": False, "format": "email" }
                        }
                    },
                    "responses": {
                        "success": {
                            "update": {
                                "statusCode": 200,
                                "description": "User updated successfully"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "User not found",
                                "conditions": ["ID does not exist"]
                            },
                            "400": {
                                "description": "Invalid input parameters",
                                "conditions": ["At least one field must be provided"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Delete User",
                "line": {
                    "beginning": 91,
                    "end": 98
                },
                "general_purpose": "Delete a user by their ID"
            },
            "apiDetails": {
                "users": {
                    "endpoint": {
                        "path": "/api/users/{id}",
                        "methods": ["DELETE"],
                        "resourceType": "User"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "User ID"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "delete": {
                                "statusCode": 204,
                                "description": "User deleted successfully"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "User not found",
                                "conditions": ["ID does not exist"]
                            }
                        }
                    }
                }
            }
        },
        # Item Routes
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Create Item",
                "line": {
                    "beginning": 101,
                    "end": 118
                },
                "general_purpose": "Create a new item with name, description, price, and optional category"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items",
                        "methods": ["POST"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "body": {
                            "name": { "type": "string", "required": True },
                            "description": { "type": "string", "required": True },
                            "price": { "type": "number", "required": True },
                            "category": { "type": "string", "required": False, "default": "uncategorized" }
                        }
                    },
                    "responses": {
                        "success": {
                            "create": {
                                "statusCode": 201,
                                "description": "Item created successfully"
                            }
                        },
                        "error": {
                            "400": {
                                "description": "Invalid input parameters",
                                "conditions": ["Missing required fields"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Get All Items",
                "line": {
                    "beginning": 120,
                    "end": 129
                },
                "general_purpose": "Retrieve all items with optional category filter"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items",
                        "methods": ["GET"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "query": {
                            "category": {
                                "type": "string",
                                "required": False,
                                "description": "Filter items by category"
                            }
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
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Get Item by ID",
                "line": {
                    "beginning": 131,
                    "end": 138
                },
                "general_purpose": "Retrieve a specific item by its ID"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items/{id}",
                        "methods": ["GET"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "Item ID"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "get_one": {
                                "statusCode": 200,
                                "description": "Single item details"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "Item not found",
                                "conditions": ["ID does not exist"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Update Item",
                "line": {
                    "beginning": 140,
                    "end": 161
                },
                "general_purpose": "Update an item's information"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items/{id}",
                        "methods": ["PUT"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "Item ID"
                            }
                        },
                        "body": {
                            "name": { "type": "string", "required": False },
                            "description": { "type": "string", "required": False },
                            "price": { "type": "number", "required": False },
                            "category": { "type": "string", "required": False }
                        }
                    },
                    "responses": {
                        "success": {
                            "update": {
                                "statusCode": 200,
                                "description": "Item updated successfully"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "Item not found",
                                "conditions": ["ID does not exist"]
                            },
                            "400": {
                                "description": "Invalid input parameters",
                                "conditions": ["At least one field must be provided"]
                            }
                        }
                    }
                }
            }
        },
        {
            "codeContext": {
                "filename": "swagger-example/src/app.js",
                "functionName": "Delete Item",
                "line": {
                    "beginning": 163,
                    "end": 170
                },
                "general_purpose": "Delete an item by its ID"
            },
            "apiDetails": {
                "items": {
                    "endpoint": {
                        "path": "/api/items/{id}",
                        "methods": ["DELETE"],
                        "resourceType": "Item"
                    },
                    "parameters": {
                        "path": {
                            "id": { 
                                "type": "integer",
                                "required": True,
                                "description": "Item ID"
                            }
                        }
                    },
                    "responses": {
                        "success": {
                            "delete": {
                                "statusCode": 204,
                                "description": "Item deleted successfully"
                            }
                        },
                        "error": {
                            "404": {
                                "description": "Item not found",
                                "conditions": ["ID does not exist"]
                            }
                        }
                    }
                }
            }
        }
    ]

def format_prompt(context):
    return f"""Generate JSDoc Swagger documentation comments for each route in the API context below.

Expected JSON Structure:
{{
  "changes": [
    {{
      "start_line": number,      // Route's beginning line MINUS 1 (to insert before route)
      "end_line": number,        // Same as route's beginning line
      "filepath": string,        // Path to the file
      "code": string,           // JSDoc Swagger documentation comment
      "description": string     // Brief description of the documentation
    }}
  ]
}}

Example (for reference):
{{
  "changes": [
    {{ 
      "start_line": 37,          // Route starts at 38, so we use 37 to place comment before
      "end_line": 38,           // Route's original start line
      "filepath": "swagger-example/src/app.js",
      "code": "/**\\n * @swagger\\n * /api/users:\\n *   post:\\n *     summary: Create a new user\\n */",
      "description": "Post request for the users"
    }}
  ]
}}

API Context:
{json.dumps(context, indent=2)}"""

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
    Applies changes to a file at specific line numbers while preserving spacing and context.
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
        
        # If file is empty or doesn't exist, initialize with enough empty lines
        while len(lines) < change.start_line:
            lines.append('\n')
            
        # Determine the indentation of the target line if it exists
        target_indentation = ''
        if change.start_line < len(lines):
            target_line = lines[change.start_line]
            target_indentation = ' ' * (len(target_line) - len(target_line.lstrip()))
        
        # Process the new code lines with proper indentation
        new_code_lines = []
        for line in change.code.split('\n'):
            # Skip empty lines
            if not line.strip():
                new_code_lines.append('\n')
                continue
            # Add indentation to non-empty lines
            new_code_lines.append(f"{target_indentation}{line}\n")
        
        # For insertions (like JSDoc comments), we insert before the target line
        # This is determined by checking if start_line equals end_line
        if change.start_line == change.end_line:
            # This is an insertion case - insert without removing anything
            lines[change.start_line:change.start_line] = new_code_lines
        else:
            # This is a replacement case - replace the specified range
            lines[change.start_line:change.end_line] = new_code_lines
        
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
            {'role': 'system', 'content': '''You are an expert in API documentation specializing in JSDoc Swagger comments. Your task is to analyze API routes and generate precise documentation.

Rules:
1. Output ONLY a single JSON object with a "changes" array
2. NO explanatory text, numbered sections, or markdown
3. NO text outside the JSON object
4. Line number handling:
   - start_line: SUBTRACT 1 from the route's beginning line to place comment before route
   - end_line: use the route's beginning line (unchanged)
   Example: if route is at lines 38-53, use start_line: 37, end_line: 38
5. Each JSDoc comment must:
   - Start with /** and end with */
   - Include @swagger annotations
   - Document only the API, not implementation
6. Never suggest creating new files or modifying existing code'''}, 
            {'role': 'user', 'content': prompt}
        ]
        
        # Initialize variables for retry logic
        max_retries = 3
        attempt = 0
        changes = None
        
        while attempt < max_retries and changes is None:
            attempt += 1
            print(f"\nAttempt {attempt} of {max_retries}")
            
            try:
                # Apply chat template and generate
                inputs = tokenizer.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    return_tensors="pt"
                ).to(device)
                
                outputs = model.generate(
                    inputs,
                    max_new_tokens=4096,
                    do_sample=True,  # Use sampling after first attempt
                    temperature=0.2, 
                    top_k=50,
                    top_p=0.95,
                    num_return_sequences=1,
                    eos_token_id=tokenizer.eos_token_id
                )
                
                # Get the generated text
                generated_text = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
                
                # Create response format matching pipeline output for compatibility
                response = [{"generated_text": generated_text}]
                print(f"\nRaw response (Attempt {attempt}):")
                print(response)
                
                # Try to extract and validate JSON
                changes = extract_json_from_response(response)
                
                if changes and not isinstance(changes.changes, list):
                    print(f"\nInvalid changes format in attempt {attempt} - not a list")
                    changes = None
                elif changes and len(changes.changes) == 0:
                    print(f"\nInvalid changes format in attempt {attempt} - empty list")
                    changes = None
                elif changes:
                    print(f"\nSuccessfully generated and validated response on attempt {attempt}")
                    break
                
            except Exception as e:
                print(f"\nError in attempt {attempt}: {e}")
                if attempt == max_retries:
                    raise Exception(f"Failed to generate valid response after {max_retries} attempts")
                continue
        
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
            
            # Sort changes by line number to apply them in order
            sorted_changes = sorted(changes.changes, key=lambda x: x.start_line)
            
            # Apply changes
            for change in sorted_changes:
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
            print(f"\nFailed to generate valid response after {max_retries} attempts")
            
    except Exception as e:
        print(f"\nError during execution: {e}")

if __name__ == "__main__":
    main()