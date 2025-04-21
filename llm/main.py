from transformers import AutoTokenizer, AutoModelForCausalLM
from git import Repo
import json
from typing import List
import os
import torch
from context import get_context

system_prompt = """You are an expert in API documentation specializing in JSDoc Swagger comments. Your ONLY task is to GENERATE Swagger documentation, NOT create scripts or tools.

IMPORTANT: 
- DO NOT generate any JavaScript code or scripts
- DO NOT create tools or utilities
- ONLY generate Swagger documentation in the specified JSON format

Your output MUST be a single JSON object containing Swagger documentation comments like this:

{
  "changes": [
    {
      "filepath": "swagger-example/src/app.js",
      "code": "/**\\n * @swagger\\n * /api/users:\\n *   post:\\n *     tags:\\n *       - Users\\n *     summary: Create user\\n *     responses:\\n *       201:\\n *         description: Created\\n */",
      "description": "Documentation for create user endpoint"
    }
  ]
}
"""

class Change():
    def __init__(self, start_line: int, end_line: int, filepath: str, code: str, description: str):
        self.start_line = start_line
        self.end_line = end_line
        self.filepath = filepath
        self.code = code
        self.description = description

class Changes():
    def __init__(self, changes: List[Change]):
        self.changes = changes

def format_prompt(context):
    return f"""TASK: Generate Swagger documentation comments for the provided API routes.

DO NOT:
❌ Create JavaScript scripts or tools
❌ Write code to extract comments
❌ Generate anything other than Swagger documentation

DO:
✅ Generate a single JSON object with Swagger documentation
✅ Follow the exact format shown below
✅ Include all required Swagger elements (path, method, tags, etc.)

Required Format:
```json
{{
  "changes": [
    {{
      "filepath": "swagger-example/src/app.js",
      "code": "/**\\n * @swagger\\n * /api/users:\\n *   post:\\n *     tags:\\n *       - Users\\n *     summary: Create user\\n *     requestBody:\\n *       required: true\\n *       content:\\n *         application/json:\\n *           schema:\\n *             type: object\\n *             properties:\\n *               name:\\n *                 type: string\\n *     responses:\\n *       201:\\n *         description: Created\\n */",
      "description": "Documentation for create user endpoint"
    }},
    // ... and so on with several changes
  ]
}}
```

API Context:
{json.dumps(context, indent=2)}"""

def convert_to_changes(response, context) -> Changes | None:
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
        
        # Parse JSON
        json_data = json.loads(json_text)
        
        # Validate that we have the expected number of changes
        if len(json_data['changes']) != len(context):
            print(f"\nWarning: Number of changes ({len(json_data['changes'])}) does not match context length ({len(context)})")
            print("This could indicate an incomplete or incorrect response from the LLM")
            return None
        
        print("\nDebug - Sorted changes:")
        for idx, change in enumerate(json_data['changes']):
            print(f"\nChange {idx + 1}:")
            print(f"File: {change['filepath']}")
            print(f"Description: {change['description']}")
            print("Code to insert:")
            print(change['code'])
        
        # Keep track of line offsets for each file
        file_offsets = {}   # "filepath (str): offset (int)"
        
        # Process each change to add line numbers
        processed_changes = []
        for i, change_data in enumerate(json_data['changes']):
            # Get matching context entry directly using the same index
            matching_context = context[i]
            
            if matching_context['codeContext']['filename'] == change_data['filepath']:
                filepath = change_data['filepath']
                
                # Get current offset for this file
                current_offset = file_offsets.get(filepath, 0)
                
                # Get the original line where we want to insert
                original_line = matching_context['codeContext']['line']['beginning']
                
                # Calculate end_line (where the route begins) with current offset
                end_line = original_line + current_offset
                
                # Calculate number of lines in the new code
                code_lines = change_data['code'].count('\n') + 1
                
                # Calculate start_line
                start_line = end_line - code_lines
                
                print(f"\nDebug - Line number calculation for {change_data['filepath']}:")
                print(f"Original route start line: {matching_context['codeContext']['line']['beginning']}")
                print(f"Current offset: {current_offset}")
                print(f"End line (route start + offset): {end_line}")
                print(f"Number of lines in new code: {code_lines}")
                print(f"Start line (adjusted): {start_line}")
                
                # Create Change object
                change = Change(
                    start_line=start_line,
                    end_line=end_line,
                    filepath=filepath,
                    code=change_data['code'],
                    description=change_data['description']
                )
                processed_changes.append(change)
                
                # Update the offset for this file
                file_offsets[filepath] = current_offset + code_lines
                print(f"New offset for file: {file_offsets[change_data['filepath']]}")
            else:
                print(f"\nWarning: Context mismatch for file {change_data['filepath']}")
                print(f"Expected: {change_data['filepath']}")
                print(f"Got: {matching_context['codeContext']['filename']}")
                raise Exception(f"Context mismatch: LLM generated documentation for wrong file order")
        
        print("\nDebug - Final processed changes:")
        for idx, change in enumerate(processed_changes):
            print(f"\nProcessed Change {idx + 1}:")
            print(f"File: {change.filepath}")
            print(f"Start line: {change.start_line}")
            print(f"End line: {change.end_line}")
            print(f"Description: {change.description}")
            print("Code:")
            print(change.code)
        
        return Changes(changes=processed_changes)
        
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
        while len(lines) < change.end_line:
            lines.append('\n')
            
        # Determine the indentation of the target line if it exists
        target_indentation = ''
        if change.end_line < len(lines):
            target_line = lines[change.end_line]
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
        
        # Insert the new lines at the correct position
        # Split the file at the insertion point and combine with new lines
        lines = lines[:change.end_line] + new_code_lines + lines[change.end_line:]
        
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
            {'role': 'system', 'content': system_prompt}, 
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
                    max_new_tokens=8192,
                    do_sample=True,
                    temperature=0.2,
                    top_k=50,
                    top_p=0.95,
                    num_return_sequences=1,
                    eos_token_id=tokenizer.eos_token_id,
                )
                
                # Get the generated text
                generated_text = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
                
                # Create response format matching pipeline output for compatibility
                response = [{"generated_text": generated_text}]
                print(f"\nRaw response (Attempt {attempt}):")
                print(response)
                
                # Try to extract and validate JSON
                changes = convert_to_changes(response, context)
                
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