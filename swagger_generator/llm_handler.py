import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from typing import List, Optional, Dict, Any
from .models import Change
from .config import LLMConfig
import json
import threading
import time
    
STOP_TOKEN = "<|endofjsdoc|>"

class LLMHandler:
    """Handles all LLM operations for generating swagger documentation."""

    def __init__(self, config: LLMConfig):
        self.config = config

        # 1) Load the tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.model_name,
            trust_remote_code=True
        )
        
        # Add special tokens
        special_tokens_dict = {'additional_special_tokens': [STOP_TOKEN]}
        self.tokenizer.add_special_tokens(special_tokens_dict)
        self.tokenizer.pad_token = "[PAD]"
        self.tokenizer.padding_side = "left"
        
        # 2) Configure low-resource options for model loading
        print(f"Loading model on {self._get_device()} with optimizations...")
        
        # Let's use 8-bit quantization if on CUDA to save memory
        use_8bit = torch.cuda.is_available()
        
        # Load the base causal LM with memory optimizations
        base_model = AutoModelForCausalLM.from_pretrained(
            config.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16,  # Use float16 instead of bfloat16
            load_in_8bit=use_8bit,     # Use 8-bit quantization when possible
            device_map="auto",         # Let the system decide on device mapping
            low_cpu_mem_usage=True     # Optimize for low CPU memory
        )
        
        # Resize embeddings to handle new tokens
        base_model.resize_token_embeddings(len(self.tokenizer))
        base_model.config.pad_token_id = self.tokenizer.pad_token_id
        
        # 3) Apply the LoRA adapter with proper device mapping
        self.model = PeftModel.from_pretrained(
            base_model,
            config.lora_adapter_id,
            torch_dtype=torch.float16,
            device_map="auto",  # Let the system decide device mapping
        )
        
        # Enable gradient checkpointing to save memory
        if hasattr(self.model, "enable_gradient_checkpointing"):
            self.model.enable_gradient_checkpointing()
    
    @staticmethod
    def _get_device() -> torch.device:
        """Determines the appropriate device for model execution."""
        return torch.device("mps" if torch.mps.is_available() else "cpu")
        
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
        """Generates a response from the model with timeout support."""
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        # Apply chat template with proper attention mask
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self._get_device())
        
        # Create proper attention mask
        attention_mask = torch.ones_like(inputs).to(self._get_device())
        
        # Create a result container and done flag for the thread
        result_container = {"outputs": None, "error": None}
        done_flag = threading.Event()
        timeout_seconds = 2000  # 3 minutes timeout
        
        def generate_with_timeout():
            try:
                print("Attempting generation with reduced parameters...")
                # Reduce max_new_tokens to avoid excessively long generation
                reduced_tokens = min(self.config.max_new_tokens, 2048)
                print(f"Using max_new_tokens={reduced_tokens} (reduced from {self.config.max_new_tokens})")
                
                # Start a progress indicator
                start_time = time.time()
                
                # First try with deterministic generation (no sampling) and reduced tokens
                result_container["outputs"] = self.model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_new_tokens=reduced_tokens,
                    do_sample=False,  # Deterministic generation
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True,
                )
                
                print(f"Generation completed in {time.time() - start_time:.2f} seconds")
                
            except Exception as e:
                result_container["error"] = e
                print(f"Generation failed with error: {e}")
            finally:
                done_flag.set()
        
        # Start generation in a separate thread
        print("Starting generation in background thread...")
        generation_thread = threading.Thread(target=generate_with_timeout)
        generation_thread.daemon = True
        generation_thread.start()
        
        # Monitor progress and check for timeout
        start_time = time.time()
        progress_interval = 10  # seconds
        next_progress = start_time + progress_interval
        
        while not done_flag.is_set():
            time.sleep(1)
            current_time = time.time()
            
            # Print progress updates
            if current_time >= next_progress:
                elapsed = current_time - start_time
                print(f"Still generating... ({elapsed:.0f} seconds elapsed)")
                next_progress = current_time + progress_interval
            
            # Check for timeout
            if current_time - start_time > timeout_seconds:
                print(f"Generation timed out after {timeout_seconds} seconds")
                # We can't actually stop the thread, but we can proceed with a fallback
                break
        
        # Check results
        if not done_flag.is_set() or result_container["error"] is not None:
            # Either timed out or had an error
            error_msg = str(result_container["error"]) if result_container["error"] else "Generation timed out"
            print(f"Using fallback response due to: {error_msg}")
            
            # Create a simple fallback response
            return [{"generated_text": f"""```json
{{
  "changes": [
    {{
      "filepath": "Unable to generate documentation",
      "code": "/**\\n * @swagger\\n * /api/error:\\n *   get:\\n *     description: Error during generation - {error_msg[:100]}\\n */",
      "description": "Generation failed or timed out"
    }}
  ]
}}```"""
            }]
        
        # Process successful generation
        outputs = result_container["outputs"]
        
        try:
            generated_text = self.tokenizer.decode(
                outputs[0][len(inputs[0]):],
                skip_special_tokens=True
            )
            return [{"generated_text": generated_text}]
        except Exception as e:
            print(f"Error decoding generated text: {e}")
            return [{"generated_text": "Error decoding model output"}]
        
    @staticmethod
    def _get_system_prompt() -> str:
        """Returns the system prompt for the model."""
        return """You are an expert in API documentation specializing in JSDoc Swagger comments. Your ONLY task is to GENERATE Swagger documentation, NOT create scripts or tools.

IMPORTANT: 
- DO NOT generate any JavaScript code or scripts
- DO NOT create tools or utilities
- ONLY generate Swagger documentation in the specified JSON format
- ALWAYS quote error descriptions that contain colons to avoid YAML parsing errors
- For error descriptions like "error: Not found", wrap them in single quotes like 'error: Not found'

Your output MUST be a single JSON object containing Swagger documentation comments like this:

```json
{{
  "changes": [
    {{
      "filepath": "<FILEPATH>",
      "code": "/**\\n * @swagger\\n * /api/users:\\n *   post:\\n *     tags:\\n *       - Users\\n *     summary: Create user\\n *     requestBody:\\n *       required: true\\n *       content:\\n *         application/json:\\n *           schema:\\n *             type: object\\n *             properties:\\n *               name:\\n *                 type: string\\n *     responses:\\n *       201:\\n *         description: Created\\n *       400:\\n *         description: 'Bad request: Invalid input'\\n */",
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