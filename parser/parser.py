import json
import re
import os
import spacy  # Example if using spaCy for NER

class ApiDocParser:
    def __init__(self, js_filepath):
        self.filepath = js_filepath
        self.filename = os.path.basename(js_filepath)
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.code = f.read()
        # Load spaCy model if present
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None 
    def _read_file(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _find_route_definitions(self):
        """Find Express-style routes: app.METHOD('path', handler)"""
        routes = []
        pattern = re.compile(
            r"(?:app|router)\."
            r"(?P<method>get|post|put|delete|patch)\s*"
            r"\(\s*"
            r"['\"`](?P<path>[^'\"`]+)['\"`]\s*,\s*"
            r"(?P<handler>[^)]+)"
            r"\)",
            re.IGNORECASE
        )

        for m in pattern.finditer(self.code):
            routes.append({
                'method': m.group('method'),
                'path': m.group('path'),
                'handler_text': m.group('handler').strip(),
                'handler_start': m.start('handler'),
                'line': self.code.count('\n', 0, m.start()) + 1
            })

        return routes


    def _extract_function_body(self, pos):
        code = self.code
        i = code.find('{', pos)
        if i < 0:
            return ''
        depth = 0
        for j in range(i, len(code)):
            if code[j] == '{': depth += 1
            elif code[j] == '}': depth -= 1
            if depth == 0:
                return code[i+1:j]
        return ''

    def _extract_parameters(self, handler_body, path):
        """Extract parameters from handler body."""
        parameters = {"path": {}, "query": {}, "body": {}}
        
        # Find req.params.X
        path_params = re.findall(r'req\.params\.(\w+)', handler_body)
        # Extract path params from route path like "/users/:id"
        path_param_names = re.findall(r':(\w+)', path)
        # Combine both sources of path params
        all_path_params = set(path_params + path_param_names)
        
        # Find req.query.X
        query_params = re.findall(r'req\.query\.(\w+)', handler_body)
        
        # Find req.body.X
        body_params = re.findall(r'req\.body\.(\w+)', handler_body)
        
        # Process path parameters
        for param in all_path_params:
            param_type = self._infer_parameter_type(param)
            param_info = {
                "type": param_type,
                "required": True,  # Path params are always required
                "description": self._generate_description(param)
            }
            param_format = self._infer_parameter_format(param, param_type)
            if param_format:
                param_info["format"] = param_format
            
            parameters["path"][param] = param_info
            
        # Process query parameters
        for param in query_params:
            param_type = self._infer_parameter_type(param)
            is_required = self._check_if_required(param, handler_body, "query")
            default_value = self._find_default_value(param, handler_body, "query")
            
            param_info = {
                "type": param_type,
                "required": is_required,
                "description": self._generate_description(param)
            }
            
            param_format = self._infer_parameter_format(param, param_type)
            if param_format:
                param_info["format"] = param_format
            if default_value is not None:
                param_info["default"] = default_value
                
            parameters["query"][param] = param_info
            
        # Process body parameters
        for param in body_params:
            param_type = self._infer_parameter_type(param)
            is_required = self._check_if_required(param, handler_body, "body")
            default_value = self._find_default_value(param, handler_body, "body")
            
            param_info = {
                "type": param_type,
                "required": is_required,
                "description": self._generate_description(param)
            }
            
            param_format = self._infer_parameter_format(param, param_type)
            if param_format:
                param_info["format"] = param_format
            if default_value is not None:
                param_info["default"] = default_value
                
            parameters["body"][param] = param_info
            
        return parameters

    def _infer_parameter_type(self, param_name):
        """Infer parameter type based on name."""
        name_lower = param_name.lower()
        if 'id' in name_lower or 'count' in name_lower or 'num' in name_lower: 
            return "number | string"
        if 'is' in name_lower or 'has' in name_lower or name_lower.startswith('enable'): 
            return "boolean"
        if 'email' in name_lower: 
            return "string"
        if 'password' in name_lower: 
            return "string"
        if 'date' in name_lower or 'time' in name_lower or 'stamp' in name_lower: 
            return "string"
        if 'limit' in name_lower or 'offset' in name_lower or 'page' in name_lower: 
            return "number"
        return "any"

    def _infer_parameter_format(self, param_name, param_type):
        """Infer parameter format based on name and type."""
        name_lower = param_name.lower()
        if param_type == "string":
            if 'email' in name_lower: return "email"
            if 'password' in name_lower: return "password"
            if 'date' in name_lower or 'time' in name_lower or 'stamp' in name_lower: return "date-time"
            if 'url' in name_lower or 'uri' in name_lower: return "uri"
            if 'uuid' in name_lower or 'guid' in name_lower: return "uuid"
        return None

    def _check_if_required(self, param_name, handler_body, source):
        """Check if parameter appears to be required based on validation patterns."""
        # Look for validation patterns like: if (!req.query.param) { return res.status(400) }
        validation_pattern = re.compile(
            rf'if\s*\(\s*!\s*req\.{source}\.{param_name}|' +
            rf'if\s*\(\s*req\.{source}\.{param_name}\s*(?:==|===)\s*(?:undefined|null|\'\'|"")',
            re.IGNORECASE
        )
        
        return validation_pattern.search(handler_body) is not None

    def _find_default_value(self, param_name, handler_body, source):
        """Find default value for a parameter."""
        # Look for patterns like: const param = req.query.param || 'default';
        default_pattern = re.compile(
            rf'(?:const|let|var)\s+\w+\s*=\s*req\.{source}\.{param_name}\s*\|\|\s*([^;,)+\]]+)',
            re.IGNORECASE
        )
        
        # Alternative pattern: req.query.param || 'default'
        alt_pattern = re.compile(
            rf'req\.{source}\.{param_name}\s*\|\|\s*([^;,)+\]]+)',
            re.IGNORECASE
        )
        
        match = default_pattern.search(handler_body)
        if not match:
            match = alt_pattern.search(handler_body)
            
        if match:
            default_text = match.group(1).strip()
            # Try to interpret the value
            if default_text in ('true', 'false'):
                return default_text == 'true'
            if default_text.isdigit():
                return int(default_text)
            if default_text.startswith("'") or default_text.startswith('"'):
                return default_text.strip('\'"')
            return default_text
            
        return None

    def _extract_responses(self, handler_body: str) -> dict:
        """Extract detailed response information from a JS API handler body."""
        responses = {"success": [], "errors": []}

        # Regex to find response calls with optional status, method, and body
        response_pattern = re.compile(
            r"res\.(?:status\(\s*(?P<status>\d+)\s*\)\.)?"
            r"(?P<method>json|send|sendStatus)\((?P<body>[\s\S]*?)\)",
            re.IGNORECASE | re.DOTALL
        )

        for match in response_pattern.finditer(handler_body):
            raw_status = match.group('status')
            method = match.group('method').lower()
            raw_body = match.group('body').strip() if method != 'sendstatus' else ''

            status_code = int(raw_status) if raw_status else (204 if method == 'sendstatus' else 200)

            # Parse body JSON if possible for richer extraction
            body_obj = None
            schema = {"type": "null"} if method == 'sendstatus' else {"type": "object"}
            try:
                # Ensure valid JSON by replacing single-quotes to double-quotes if needed
                sanitized = raw_body.replace("'", '"')
                body_obj = json.loads(sanitized)
                # Infer schema from parsed object
                schema = self._infer_schema_from_response_body(body_obj)
            except Exception:
                # Fall back to regex-based or default schema
                if raw_body:
                    schema = self._infer_schema_from_response_body(raw_body)

            # Build description and collect details
            description_parts = []

            if status_code >= 400:
                # Errors: look for common error fields
                if isinstance(body_obj, dict):
                    for field in ('error', 'message', 'detail', 'issue'):
                        if field in body_obj:
                            description_parts.append(f"{field}: {body_obj[field]}")
                    # Handle array of detail objects
                    if 'details' in body_obj and isinstance(body_obj['details'], list):
                        for item in body_obj['details']:
                            for k, v in item.items():
                                description_parts.append(f"{k}: {v}")
                else:
                    # Regex fallback
                    for key, val in re.findall(r"['\"`]?\b(error|message|detail|issue|field)\b['\"`]?\s*:\s*['\"`](.*?)['\"`]", raw_body, re.IGNORECASE):
                        description_parts.append(f"{key}: {val}")
                description = "; ".join(description_parts) or f"Error with status {status_code}."
                responses['errors'].append({
                    'statusCode': status_code,
                    'description': description,
                    'schema': schema
                })

            else:
                # Success responses
                if isinstance(body_obj, dict) and 'message' in body_obj:
                    description = body_obj['message']
                else:
                    # Regex fallback for message field
                    m = re.search(r"['`\"]?\bmessage\b['`\"]?\s*:\s*['`\"](.*?)['`\"]", raw_body)
                    description = m.group(1) if m else 'Successful operation.'

                responses['success'].append({
                    'statusCode': status_code,
                    'description': description,
                    'schema': schema
                })

        # Consolidate: if multiple, keep the most detailed (e.g., highest schema properties)
        # For simplicity, pick the last
        if responses['success']:
            responses['success'] = responses['success'][-1]
        else:
            responses['success'] = None

        # Deduplicate errors by statusCode + description
        unique = []
        seen = set()
        for err in responses['errors']:
            key = (err['statusCode'], err['description'])
            if key not in seen:
                seen.add(key)
                unique.append(err)
        responses['errors'] = unique

        return responses


    def _infer_schema_from_response_body(self, body_content):
        """Attempt to infer OpenAPI schema from JS object literal string or parsed object."""
        # Handle already parsed objects (from json.loads)
        if isinstance(body_content, dict):
            schema = {"type": "object", "properties": {}}
            for key, value in body_content.items():
                if isinstance(value, str):
                    prop_schema = {"type": "string"}
                elif isinstance(value, bool):
                    prop_schema = {"type": "boolean"}
                elif isinstance(value, (int, float)):
                    prop_schema = {"type": "number"}
                elif isinstance(value, dict):
                    prop_schema = {"type": "object"}
                elif isinstance(value, list):
                    prop_schema = {"type": "array", "items": {"type": "any"}}
                else:
                    prop_schema = {"type": "any"}
                
                # Add format if applicable
                prop_format = self._infer_parameter_format(key, prop_schema["type"])
                if prop_format:
                    prop_schema["format"] = prop_format
                
                schema["properties"][key] = prop_schema
            return schema
        
        # Handle string content (JS object literal)
        schema = {"type": "object", "properties": {}}
        
        # Skip if not a string
        if not isinstance(body_content, str):
            return schema
        
        # Very basic regex to find key-value pairs in a JS object literal
        prop_pattern = re.compile(r'([a-zA-Z_$][a-zA-Z0-9_$]*|\'[^\']*\'|"[^"]*")\s*:\s*([^,}]+)')
        
        for key_match, value_match in prop_pattern.findall(body_content):
            key = key_match.strip('\'"')
            value_str = value_match.strip()
            prop_schema = {"type": "any"}  # Default
            
            # Infer type from value string
            if value_str.startswith("'") or value_str.startswith('"') or value_str.startswith("`"):
                prop_schema = {"type": "string"}
            elif value_str.isdigit() or re.match(r'parseInt\s*\(', value_str) or 'id' in key.lower():
                prop_schema = {"type": "number"}  # Could be string if it's a large ID
            elif value_str in ['true', 'false']:
                prop_schema = {"type": "boolean"}
            elif value_str.startswith('{'):
                prop_schema = {"type": "object"}  # Could recurse, but keep simple for now
            elif value_str.startswith('['):
                prop_schema = {"type": "array", "items": {"type": "any"}}
            elif re.match(r'req\.(?:params|body|query)\.([a-zA-Z0-9_]+)', value_str):
                # Try to link back to parameter type if possible (complex)
                var_name = re.match(r'req\.(?:params|body|query)\.([a-zA-Z0-9_]+)', value_str).group(1)
                inferred_type = self._infer_parameter_type(var_name).split(" | ")[0]  # Take first guess
                if inferred_type != "any":
                    prop_schema = {"type": inferred_type}
            
            # Add format for common patterns
            prop_format = self._infer_parameter_format(key, prop_schema.get("type", "any"))
            if prop_format:
                prop_schema["format"] = prop_format
            
            schema["properties"][key] = prop_schema
        
        # If no properties found, maybe it's not an object literal?
        if not schema["properties"]:
            # Check if it appears to be a simple string
            if body_content.startswith("'") or body_content.startswith('"') or body_content.startswith("`"):
                return {"type": "string"}
            # Fallback to basic object
            return {"type": "object"}
        
        return schema

    def _infer_validation_constraints(self, handler_body):
        """Infer validation constraints from handler code."""
        constraints = []
        
        # Look for common validation error messages
        validation_msgs = re.finditer(
            r'(?:send|json|status)\([^)]*[\'"]([^\'"]*(required|invalid|must|minimum|maximum|length)[^\'"]*)[\'"]\)',
            handler_body,
            re.IGNORECASE
        )
        
        for match in validation_msgs:
            message = match.group(1).strip()
            if message and message not in constraints:
                constraints.append(message)
        
        # Look for validation middleware or validation library usage
        validation_libs = [
            (r'body\([\'"](\w+)[\'"]\)\.(?:isEmail|isLength|isInt)', 'Validate $1'),
            (r'check\([\'"](\w+)[\'"]\)\.(?:isEmail|isLength|isInt)', 'Validate $1'),
            (r'joi\.(?:string|number|boolean|object)\(\)\.(\w+)\(\)', 'Must satisfy $1 validation'),
            (r'yup\.(?:string|number|boolean|object)\(\)\.(\w+)\(\)', 'Must satisfy $1 validation')
        ]
        
        for pattern, template in validation_libs:
            for match in re.finditer(pattern, handler_body, re.IGNORECASE):
                field = match.group(1)
                constraint = template.replace('$1', field)
                if constraint not in constraints:
                    constraints.append(constraint)
                
        return constraints

    def _generate_description(self, term):
        """Generate a description for a parameter or endpoint."""
        words = re.findall('[A-Z][a-z]*|[a-z]+', term)
        desc = ' '.join(words).capitalize()
        
        # Add type-specific descriptions
        if 'id' in term.lower():
            return f"{desc} - Unique identifier"
        if 'email' in term.lower():
            return f"{desc} - Email address of the user"
        if 'name' in term.lower():
            return f"{desc} - Name of the resource"
        
        return desc

    def _infer_resource_from_context(self, function_name, route_path):
        """Infer the resource type from context."""
        resource_keywords = ['user', 'product', 'order', 'item', 'account', 'post', 'comment', 'category', 'session', 'profile']
        
        # Check path components
        path_parts = [part for part in route_path.strip('/').split('/') if not part.startswith(':') and part]
        
        if path_parts:
            resource_candidate = path_parts[0].lower()
            # Handle plural forms
            if resource_candidate.endswith('s'):
                resource_candidate = resource_candidate[:-1]
                
            for keyword in resource_keywords:
                if keyword in resource_candidate:
                    return keyword.capitalize()
            
        # Check function name
        func_name_lower = function_name.lower()
        for keyword in resource_keywords:
            if keyword in func_name_lower:
                return keyword.capitalize()
                
        # Default to first path component or Unknown
        if path_parts:
            return path_parts[0].capitalize()
        return "Unknown"

    def _infer_purpose_from_context(self, function_name, method, resource):
        """Infer the purpose of the endpoint."""
        func_name_lower = function_name.lower()
        
        # Determine action based on HTTP method
        if method == "GET":
            action = "retrieve"
            if "list" in func_name_lower or "all" in func_name_lower:
                return f"API endpoint to list all {resource} resources."
            return f"API endpoint to retrieve a specific {resource}."
            
        if method == "POST":
            action = "create"
            return f"API endpoint to create a new {resource}."
            
        if method == "PUT" or method == "PATCH":
            action = "update"
            return f"API endpoint to update an existing {resource}."
            
        if method == "DELETE":
            action = "delete"
            return f"API endpoint to delete a {resource}."
            
        # Check function name for clues
        if "create" in func_name_lower or "add" in func_name_lower or "new" in func_name_lower:
            action = "create"
        elif "get" in func_name_lower or "list" in func_name_lower or "find" in func_name_lower:
            action = "retrieve"
        elif "update" in func_name_lower or "edit" in func_name_lower or "modify" in func_name_lower:
            action = "update"
        elif "delete" in func_name_lower or "remove" in func_name_lower:
            action = "delete"
        else:
            action = "handle"
            
        return f"API endpoint to {action} {resource} resources."

    def _extract_function_name(self, handler_text):
        """Extract function name from handler text."""
        # Check if it's a direct reference to a named function
        if re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$.]*$', handler_text):
            return handler_text
            
        # Check for function declaration: function name(...) { ... }
        func_decl = re.match(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', handler_text)
        if func_decl:
            return func_decl.group(1)
            
        # It's an anonymous function
        return "anonymous"
    
    def _build_standardized_responses(self, responses_data):
        """Convert raw response data to standardized format for better output integration."""
        result = {
            "successResponse": None,
            "errorResponses": []
        }
        
        # Process success response
        if responses_data['success']:
            result['successResponse'] = {
                "statusCode": responses_data['success']['statusCode'],
                "description": responses_data['success']['description'],
                "schema": responses_data['success']['schema']
            }
        
        # Process error responses
        if responses_data['errors']:
            for error in responses_data['errors']:
                result['errorResponses'].append({
                    "statusCode": error['statusCode'],
                    "description": error['description'],
                    "schema": error['schema']
                })
        
        return result

    def extract_api_info(self):
        docs = []
        for route in self._find_route_definitions():
            method = route['method'].upper()
            path = route['path']
            start = route['handler_start']
            body = self._extract_function_body(start)
            # Gather all parts
            responses = self._extract_responses(body)
            params = self._extract_parameters(body, path)
            validation = self._infer_validation_constraints(body)
            func_name = self._extract_function_name(route['handler_text'])
            resource = self._infer_resource_from_context(func_name, path)
            purpose = self._infer_purpose_from_context(func_name, method, resource)
            # Remove empty categories
            params = {k: v for k, v in params.items() if v}
            docs.append({
                'codeContext': {
                    'filename': self.filepath,
                    'functionName': func_name,
                    'line': route['line'],
                    'general_purpose': purpose
                },
                'apiDetails': {
                    'endpoint': {'path': path, 'method': method, 'resourceType': resource},
                    'parameters': params,
                    'responses': responses,
                    'validation': {'inputConstraints': validation}
                }
            })
        return docs


# Example usage
if __name__ == "__main__":
    js_file_to_parse = input("Enter the path to the JavaScript API file: ")

    if not js_file_to_parse:
        print("No file path provided.")
    else:
        try:
            parser = ApiDocParser(js_file_to_parse)
            extracted_data = parser.extract_api_info()

            if extracted_data:
                print(json.dumps(extracted_data, indent=2))
            else:
                print(f"Could not extract any API information from {js_file_to_parse}")

        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()  # Print full trace for debugging