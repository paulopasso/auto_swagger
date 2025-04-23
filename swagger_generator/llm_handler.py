import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from typing import List, Optional, Dict, Any
from .models import Change
from .config import LLMConfig
import json

load_dotenv()

class LLMHandler:
    """Handles all LLM operations for generating swagger documentation."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        
    def generate_documentation(self, context: List[Dict[str, Any]]) -> Optional[List[Change]]:
        """Generates swagger documentation for the given API contexts."""
        system_prompt = self._get_system_prompt()
        user_prompt = self._format_prompt(context)
        
        for attempt in range(self.config.max_retries):
            print(f"\nAttempt {attempt + 1} of {self.config.max_retries}")
            
            try:
                response = self._generate_response(system_prompt, user_prompt)
                changes = self._convert_to_changes(response, context)
                
                if changes is None:
                    print(f"\nInvalid changes format in attempt {attempt + 1} - conversion failed")
                elif len(changes) == 0:
                    print(f"\nInvalid changes format in attempt {attempt + 1} - empty list")
                    changes = None
                else:
                    print(f"\nSuccessfully generated and validated response on attempt {attempt + 1}")
                    return changes
                    
            except Exception as e:
                print(f"\nError in attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"Failed to generate valid response after {self.config.max_retries} attempts")
                
        return None
        
    def _generate_response(self, system_prompt: str, user_prompt: str) -> List[Dict[str, str]]:
        """Generates a response from the model."""
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        client = InferenceClient(
            provider="novita",
            api_key=os.getenv("API_KEY"),
        )

        completion = client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
        )

        generated_text = completion.choices[0].message.content
        
        return [{"generated_text": generated_text}]
        
    @staticmethod
    def _get_system_prompt() -> str:
        """Returns the system prompt for the model."""
        return """You are an expert in API documentation specializing in JSDoc Swagger comments. Your ONLY task is to GENERATE Swagger documentation, NOT create scripts or tools.

IMPORTANT: 
- DO NOT generate any JavaScript code or scripts
- DO NOT create tools or utilities
- ONLY generate Swagger documentation in the specified JSON format

Your output MUST be a single JSON object containing Swagger documentation comments like this:

```json
{{
  "changes": [
    {{
      "filepath": "<FILEPATH>",
      "code": "/**\\n * @swagger\\n * /api/users:\\n *   post:\\n *     tags:\\n *       - Users\\n *     summary: Create user\\n *     requestBody:\\n *       required: true\\n *       content:\\n *         application/json:\\n *           schema:\\n *             type: object\\n *             properties:\\n *               name:\\n *                 type: string\\n *     responses:\\n *       201:\\n *         description: Created\\n */",
      "description": "Documentation for create user endpoint"
    }},
    // ... and so on with several changes
  ]
}}
```
}"""


    @staticmethod
    def _format_prompt(context: List[Dict[str, Any]]) -> str:
        """Formats the user prompt with the given context."""
        return f"""TASK: Generate Swagger documentation comments for the provided API routes.

DO NOT:
❌ Create JavaScript scripts or tools
❌ Write code to extract comments
❌ Generate anything other than Swagger documentation

DO:
✅ Generate a single JSON object with Swagger documentation
✅ Follow the exact format shown below
✅ Include all required Swagger elements (path, method, tags, etc.)

API Context:
{json.dumps(context, indent=2)}"""

    def _convert_to_changes(self, response: List[Dict[str, str]], context: List[Dict[str, Any]]) -> Optional[List[Change]]:
        """Converts the model response to a list of changes."""
        try:
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
                return None
            
            # Keep track of line offsets for each file
            file_offsets = {}  # "filepath (str): offset (int)"
            
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
                    
                    # Calculate start_line with current offset
                    start_line = original_line + current_offset - 1
                    
                    # Calculate number of lines in the new code
                    code_lines = change_data['code'].count('\n') + 1
                    
                    # Create Change object
                    change = Change(
                        start_line=start_line,
                        filepath=filepath,
                        code=change_data['code'],
                        description=change_data['description']
                    )
                    processed_changes.append(change)
                    
                    # Update the offset for this file
                    file_offsets[filepath] = current_offset + code_lines
                else:
                    print(f"\nWarning: Context mismatch for file {change_data['filepath']}")
                    raise ValueError(f"Context mismatch: LLM generated documentation for wrong file order")
            
            return processed_changes
            
        except Exception as e:
            print(f"\nError extracting JSON from response: {e}")
            if 'text' in locals():
                print("\nRaw text that caused the error:")
                print(text)
            return None 