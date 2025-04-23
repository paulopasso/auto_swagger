import json
import os
import re
from typing import Dict, List

import spacy
from spacy.lang.en import English

# NLP Used: POS Tagging, NER, and Regex


class ApiDocParser:
    """Parser for extracting API documentation from source code files."""

    @staticmethod
    def is_api_file(filepath: str) -> bool:
        """Check if a file contains API definitions.

        Args:
            filepath: Path to the file to check

        Returns:
            bool: True if file contains API routes
        """
        if not os.path.exists(filepath):
            return False

        if not filepath.endswith((".js", ".ts", ".py")):
            return False

        try:
            # Try different encodings
            encodings = ["utf-8", "latin-1", "cp1252"]
            content = None

            for encoding in encodings:
                try:
                    with open(filepath, "r", encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                return False

            # API route patterns to match
            route_patterns = [
                r"app\.(get|post|put|delete|patch)",
                r"router\.(get|post|put|delete|patch)",
                r"@(Get|Post|Put|Delete|Patch)",
                r"express\.Router\(\)",
                r"createRouter",
            ]
            return any(re.search(p, content, re.I) for p in route_patterns)
        except Exception:
            return False

    @staticmethod
    def parse_files(files: List[str]) -> List[dict]:
        """Parse multiple files and return their API documentation as a flattened list.

        Args:
            files: List of file paths to parse

        Returns:
            List of API documentation objects for all files
        """
        all_routes = []
        for filepath in files:
            if ApiDocParser.is_api_file(filepath):
                try:
                    parser = ApiDocParser(filepath)
                    docs = parser.extract_api_info()
                    if docs:  # Only include if API docs were found
                        all_routes.extend(docs)
                except Exception as e:
                    print(f"Error parsing {filepath}: {str(e)}")
        return all_routes

    def __init__(self, js_filepath: str, repo_root: str | None = None):
        """Initialize the API documentation parser.

        Args:
            js_filepath: Path to the JavaScript/TypeScript file to parse
            repo_root: Root path of the repository. If provided, paths will be relative to this.
        """
        self.filepath = js_filepath
        
        # Calculate relative path from repo root if provided, otherwise from current directory
        if repo_root:
            self.relative_path = os.path.relpath(js_filepath, repo_root)
        else:
            self.relative_path = os.path.basename(js_filepath)
        
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        # Try different encodings
        encodings = ["utf-8", "latin-1", "cp1252"]
        self.code = None

        for encoding in encodings:
            try:
                with open(self.filepath, "r", encoding=encoding) as f:
                    self.code = f.read()
                break
            except UnicodeDecodeError:
                continue

        if self.code is None:
            raise UnicodeError(
                "Could not decode {} with any supported encoding".format(self.filepath)
            )

        # Initialize NLP
        self._init_nlp()

    def _init_nlp(self) -> None:
        """Initialize the NLP pipeline with error handling and fallbacks."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print(f"spaCy model loaded successfully for {self.relative_path}.")
        except Exception as e:
            msg = (
                f"Warning: spaCy model failed ({e}) for {self.relative_path}. "
                "Using basic tokenization."
            )
            print(msg)
            self.nlp = English()
            if not self.nlp.has_pipe("tagger"):
                self.nlp.add_pipe("tagger", last=True)
                try:
                    self.nlp.initialize()
                except Exception as init_e:
                    print(f"Warning: Failed to initialize POS tagger ({init_e}).")
                    if self.nlp.has_pipe("tagger"):
                        self.nlp.remove_pipe("tagger")

    def _read_file(self):
        """Reads the content of the JavaScript file."""
        with open(self.filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _find_route_definitions(self):
        """Find Express-style routes: app.METHOD('path', handler)"""
        routes = []
        # Regex captures method, path, and handler identifier/function text
        pattern = re.compile(
            r"(?:app|router)\."
            r"(?P<method>get|post|put|delete|patch)\s*"
            r"\(\s*"
            r"['\"`](?P<path>[^'\"`]+)['\"`]\s*,\s*"
            r"(?P<handler>[^)]+)"  # Captures everything until the closing parenthesis
            r"\)",
            re.IGNORECASE,
        )

        for m in pattern.finditer(self.code):
            start_line = self.code.count('\n', 0, m.start()) + 1  # Route definition start
            handler_start = m.start('handler')
            handler_text = m.group('handler').strip()
            
            # Find the end of the handler function
            handler_body = self._extract_function_body(handler_start)
            if handler_body:
                # Calculate end line by counting newlines up to the end of handler body
                end_line = self.code.count('\n', 0, m.start() + len(m.group(0)) + len(handler_body)) + 1
            else:
                # If no function body found, use the route definition line as end line
                end_line = start_line

            routes.append({
                'method': m.group('method'),
                'path': m.group('path'),
                'handler_text': handler_text,
                'handler_start': handler_start,
                'line': {
                    'beginning': start_line,
                    'end': end_line
                }
            })

        return routes

    def _extract_function_body(self, pos):
        """Extracts the code block enclosed in {} starting near the given position."""
        code = self.code
        # Find the first opening brace after the handler definition starts
        i = code.find("{", pos)
        if i < 0:
            return ""  # No function body found
        depth = 0
        # Iterate through the code to find the matching closing brace
        for j in range(i, len(code)):
            if code[j] == "{":
                depth += 1
            elif code[j] == "}":
                depth -= 1
            if depth == 0:
                return code[i + 1 : j]  # Return content between the braces
        return ""  # Unmatched brace

    def _extract_parameters(self, handler_body, path):
        """Extract parameters from handler body, including destructuring."""
        parameters = {"path": {}, "query": {}, "body": {}}

        # Path Parameters: Direct access (req.params.X) and route definitions (/:X)
        path_params_direct = re.findall(r"req\.params\.(\w+)", handler_body)
        path_param_names_route = re.findall(r":(\w+)", path)
        all_path_params = set(path_params_direct + path_param_names_route)

        # Query Parameters: Direct access (req.query.X) and destructuring
        query_params_direct = re.findall(r"req\.query\.(\w+)", handler_body)
        query_params_destructured = set()
        # Regex for: const { key1, key2 } = req.query
        destructure_query_pattern = re.compile(
            r"(?:const|let|var)\s*{\s*(?P<keys>[\w\s,]+)\s*}\s*=\s*req\.query",
            re.IGNORECASE,
        )
        for match in destructure_query_pattern.finditer(handler_body):
            keys = [
                key.strip() for key in match.group("keys").split(",") if key.strip()
            ]
            query_params_destructured.update(keys)
        all_query_params = set(query_params_direct) | query_params_destructured

        # Body Parameters: Direct access (req.body.X) and destructuring
        body_params_direct = re.findall(r"req\.body\.(\w+)", handler_body)
        body_params_destructured = set()
        # Regex for: const { key1, key2 } = req.body
        destructure_body_pattern = re.compile(
            r"(?:const|let|var)\s*{\s*(?P<keys>[\w\s,]+)\s*}\s*=\s*req\.body",
            re.IGNORECASE,
        )
        for match in destructure_body_pattern.finditer(handler_body):
            keys = [
                key.strip() for key in match.group("keys").split(",") if key.strip()
            ]
            body_params_destructured.update(keys)
        all_body_params = set(body_params_direct) | body_params_destructured

        # Process discovered path parameters
        for param in all_path_params:
            param_type = self._infer_parameter_type(param)
            param_info = {
                "type": param_type,
                "required": True,  # Path params are always required
                "description": self._generate_description(param, "path"),
            }
            param_format = self._infer_parameter_format(param, param_type)
            if param_format:
                param_info["format"] = param_format
            parameters["path"][param] = param_info

        # Process discovered query parameters
        for param in all_query_params:
            param_type = self._infer_parameter_type(param)
            is_required = self._check_if_required(param, handler_body, "query")
            default_value = self._find_default_value(param, handler_body, "query")
            param_info = {
                "type": param_type,
                "required": is_required,
                "description": self._generate_description(param, "query"),
            }
            param_format = self._infer_parameter_format(param, param_type)
            if param_format:
                param_info["format"] = param_format
            if default_value is not None:
                param_info["default"] = default_value
            parameters["query"][param] = param_info

        # Process discovered body parameters
        for param in all_body_params:
            param_type = self._infer_parameter_type(param)
            is_required = self._check_if_required(param, handler_body, "body")
            default_value = self._find_default_value(param, handler_body, "body")
            param_info = {
                "type": param_type,
                "required": is_required,
                "description": self._generate_description(param, "body"),
            }
            param_format = self._infer_parameter_format(param, param_type)
            if param_format:
                param_info["format"] = param_format
            if default_value is not None:
                param_info["default"] = default_value
            parameters["body"][param] = param_info

        return parameters

    def _infer_parameter_type(self, param_name):
        """Infer parameter type based on common naming conventions."""
        name_lower = param_name.lower()
        if "id" in name_lower or "count" in name_lower or "num" in name_lower:
            return "number | string"  # IDs can often be strings or numbers
        if "is" in name_lower or "has" in name_lower or name_lower.startswith("enable"):
            return "boolean"
        if "email" in name_lower:
            return "string"
        if "password" in name_lower:
            return "string"
        if "date" in name_lower or "time" in name_lower or "stamp" in name_lower:
            return "string"  # Representing date/time
        if "limit" in name_lower or "offset" in name_lower or "page" in name_lower:
            return "number"  # Pagination typically uses numbers
        return "any"  # Default fallback

    def _infer_parameter_format(self, param_name, param_type):
        """Infer parameter format (e.g., email, date-time) based on name and type."""
        name_lower = param_name.lower()
        if param_type == "string":
            if "email" in name_lower:
                return "email"
            if "password" in name_lower:
                return "password"
            if "date" in name_lower or "time" in name_lower or "stamp" in name_lower:
                return "date-time"
            if "url" in name_lower or "uri" in name_lower:
                return "uri"
            if "uuid" in name_lower or "guid" in name_lower:
                return "uuid"
        # Add more format inferences as needed (e.g., byte, binary)
        return None

    def _check_if_required(self, param_name, handler_body, source):
        """Check if parameter appears required based on explicit checks or lack of default."""
        # Look for patterns like: if (!req.query.param) or if (!param) return res.status(400)
        validation_pattern = re.compile(
            rf"if\s*\(\s*!\s*(?:req\.{source}\.)?{param_name}\b|"  # Check for !param or !req.source.param
            + rf'if\s*\(\s*(?:req\.{source}\.)?{param_name}\s*(?:==|===)\s*(?:undefined|null|\'\'|"")',  # Check for param == null/undefined/''
            re.IGNORECASE,
        )

        # Check if a default value seems to be assigned using || or destructuring default
        has_default_assignment = (
            self._find_default_value(param_name, handler_body, source) is not None
        )

        # Parameter is likely required if:
        # 1. It's not a path parameter (which are always required by definition).
        # 2. There's code explicitly checking for its absence.
        # 3. It doesn't appear to have a default value assigned.
        return (
            source != "path"
            and validation_pattern.search(handler_body) is not None
            and not has_default_assignment
        )

    def _find_default_value(self, param_name, handler_body, source):
        """Find default value assigned via '||' operator or destructuring."""

        # Pattern 1: Assignment or direct use with '|| default'
        # Examples: const x = req.query.p || 'def'; func(req.query.p || false);
        default_pattern_assign = re.compile(
            rf"(?:const|let|var)\s+[\w\s,]*?{param_name}[\w\s,]*?\s*=\s*.*?req\.{source}\.{param_name}\s*\|\|\s*(?P<default1>[^;,)+\]\n]+)|"
            + rf"\breq\.{source}\.{param_name}\s*\|\|\s*(?P<default2>[^;,)+\]\n]+)",
            re.IGNORECASE,
        )
        match = default_pattern_assign.search(handler_body)
        if match:
            default_text = (match.group("default1") or match.group("default2")).strip()
            # Attempt to interpret the captured default value literal
            if default_text in ("true", "false"):
                return default_text == "true"
            if default_text.isdigit():
                return int(default_text)
            # Handle quoted strings
            if (
                (default_text.startswith("'") and default_text.endswith("'"))
                or (default_text.startswith('"') and default_text.endswith('"'))
                or (default_text.startswith("`") and default_text.endswith("`"))
            ):
                return default_text[1:-1]
            # If it looks like a variable name or other literal, return as string
            return default_text

        # Pattern 2: Destructuring with default value
        # Example: const { limit = 10 } = req.query;
        # Find the whole destructuring block first: { ... } = req.source
        destructure_block_pattern = re.compile(
            r"(?:const|let|var)\s*{(?P<block>[\s\S]*?)}\s*=\s*req\.{source}",
            re.IGNORECASE,
        )
        # Then look for 'param = value' inside the block
        destructure_default_pattern = re.compile(
            rf"{param_name}\s*=\s*(?P<default>[^,\}}]+)",  # Non-greedy capture until comma or brace
            re.IGNORECASE,
        )
        for block_match in destructure_block_pattern.finditer(handler_body):
            block_content = block_match.group("block")
            default_match = destructure_default_pattern.search(block_content)
            if default_match:
                default_text = default_match.group("default").strip()
                # Attempt to interpret the captured default value literal
                if default_text in ("true", "false"):
                    return default_text == "true"
                if default_text.isdigit():
                    return int(default_text)
                # Handle quoted strings
                if (
                    (default_text.startswith("'") and default_text.endswith("'"))
                    or (default_text.startswith('"') and default_text.endswith('"'))
                    or (default_text.startswith("`") and default_text.endswith("`"))
                ):
                    return default_text[1:-1]
                # If it looks like a variable name or other literal, return as string
                return default_text

        return None  # No default found

    def _generate_description(self, param_name: str, source: str) -> str:
        """Generate a basic description for a parameter, enhanced with NLP if possible."""
        # Use NLP NER if available and model loaded
        if self.nlp and self.nlp.has_pipe("ner"):
            doc = self.nlp(param_name)
            ner_tags = [(ent.text, ent.label_) for ent in doc.ents]
            if ner_tags:
                entity_text, entity_label = ner_tags[0]  # Use the first detected entity
                human_readable_label = entity_label.replace("_", " ").title()
                return f"Parameter '{param_name}', likely representing a {human_readable_label}."

        # Fallback: Use common keywords if no NER match or NLP unavailable
        name_lower = param_name.lower()
        if "id" in name_lower:
            return f"Identifier ({param_name})."
        if "name" in name_lower:
            return f"Name ({param_name})."
        if "email" in name_lower:
            return f"Email address ({param_name})."
        if "date" in name_lower or "time" in name_lower:
            return f"Date or timestamp ({param_name})."
        if "limit" in name_lower or "page" in name_lower or "offset" in name_lower:
            return f"Pagination parameter ({param_name})."
        if "is" in name_lower or "has" in name_lower or name_lower.startswith("enable"):
            return f"Boolean flag ({param_name})."

        # Default description if no specific patterns match
        return f"Parameter '{param_name}' from the request {source}."

    def _extract_responses(self, handler_body: str) -> dict:
        """Extract detailed response information from a JS API handler body."""
        responses = {"success": [], "errors": []}

        # Regex to find response calls (res.json/send/sendStatus)
        # Captures status (optional), method, and body content non-greedily
        response_pattern = re.compile(
            r"res\.(?:status\(\s*(?P<status>\d+)\s*\)\.)?"
            r"(?P<method>json|send|sendStatus)\s*"
            r"\((?P<body>.*?)\s*\);?",  # Non-greedy body capture until closing parenthesis
            re.IGNORECASE | re.DOTALL,
        )

        # Basic scope finding: limit search to within the handler's main {} block
        # This helps avoid matching res.json calls from unrelated nested functions
        handler_scope_match = re.search(r"\{(?P<scope>.*)\}", handler_body, re.DOTALL)
        search_area = (
            handler_scope_match.group("scope") if handler_scope_match else handler_body
        )

        for match in response_pattern.finditer(search_area):
            raw_status = match.group("status")
            method = match.group("method").lower()
            raw_body = match.group("body").strip() if method != "sendstatus" else ""

            # Skip if body capture is empty for methods expecting a body
            if method != "sendstatus" and not raw_body:
                continue

            status_code = (
                int(raw_status)
                if raw_status
                else (204 if method == "sendstatus" else 200)
            )

            body_obj = None
            schema = (
                {"type": "null"}
                if method == "sendstatus"
                else {"type": "object", "properties": {}}
            )  # Default schema

            if method != "sendstatus" and raw_body:
                try:
                    # --- Sanitize JS object literal for JSON parsing ---
                    sanitized = raw_body
                    # 1. Remove JS comments (// and /* */)
                    sanitized = re.sub(r"//.*", "", sanitized)
                    sanitized = re.sub(
                        r"/\*[\s\S]*?\*/", "", sanitized, flags=re.MULTILINE
                    )
                    # 2. Replace single quotes with double quotes (basic)
                    # Note: This is imperfect and might fail on strings containing quotes.
                    sanitized = sanitized.replace("'", '"')
                    # 3. Add quotes around unquoted keys
                    sanitized = re.sub(
                        r"([{,\s])([a-zA-Z_$][\w$]*)\s*:", r'\1"\2":', sanitized
                    )
                    # 4. Remove trailing commas before } or ]
                    sanitized = re.sub(r",\s*([}\]])", r"\1", sanitized)
                    # 5. Replace `undefined` with `null`
                    sanitized = re.sub(r"\bundefined\b", "null", sanitized)
                    sanitized = sanitized.strip()

                    # Attempt parsing only if it looks like an object or array
                    if (
                        sanitized.startswith("{")
                        and sanitized.endswith("}")
                        or sanitized.startswith("[")
                        and sanitized.endswith("]")
                    ):
                        body_obj = json.loads(sanitized)
                        # Infer schema from the successfully parsed object
                        schema = self._infer_schema_from_response_body(body_obj)
                    else:
                        # If it doesn't look like JSON after sanitizing (e.g., a variable name)
                        # Use the raw body string for basic regex-based schema inference
                        schema = self._infer_schema_from_response_body(raw_body)

                except json.JSONDecodeError:
                    # If JSON parsing fails, fall back to regex inference on the original raw body
                    schema = self._infer_schema_from_response_body(raw_body)
                except Exception:
                    # Catch other potential errors during sanitization/parsing, fallback
                    schema = self._infer_schema_from_response_body(raw_body)

            # --- Categorize and describe the response ---
            description_parts = []
            if status_code >= 400:  # Error response
                # Extract 'error', 'message', etc. fields for description if possible
                if isinstance(body_obj, dict):
                    for field in ("error", "message", "detail", "issue"):
                        if field in body_obj and isinstance(
                            body_obj[field], (str, int, bool, float)
                        ):
                            description_parts.append(f"{field}: {body_obj[field]}")
                    if "details" in body_obj and isinstance(body_obj["details"], list):
                        # Add details if available
                        for item in body_obj["details"]:
                            if isinstance(item, dict):
                                for k, v in item.items():
                                    if isinstance(v, (str, int, bool, float)):
                                        description_parts.append(f"{k}: {v}")
                            elif isinstance(item, (str, int, bool, float)):
                                description_parts.append(str(item))
                else:
                    # Regex fallback on raw_body if parsing failed or not a dict
                    for key, val in re.findall(
                        r"['\"`]?\b(error|message|detail|issue|field)\b['\"`]?\s*:\s*['\"`](.*?)['\"`]",
                        raw_body,
                        re.IGNORECASE,
                    ):
                        description_parts.append(f"{key}: {val}")
                description = (
                    "; ".join(description_parts)
                    or f"Error response with status {status_code}."
                )
                responses["errors"].append(
                    {
                        "statusCode": status_code,
                        "description": description,
                        "schema": schema,
                    }
                )
            else:  # Success response
                # Extract 'message' field for description if possible
                if (
                    isinstance(body_obj, dict)
                    and "message" in body_obj
                    and isinstance(body_obj["message"], str)
                ):
                    description = body_obj["message"]
                else:
                    # Regex fallback on raw_body if parsing failed or no message field
                    m = re.search(
                        r"['`\"]?\bmessage\b['`\"]?\s*:\s*['`\"](.*?)['`\"]", raw_body
                    )
                    description = m.group(1) if m else "Successful operation."
                responses["success"].append(
                    {
                        "statusCode": status_code,
                        "description": description,
                        "schema": schema,
                    }
                )

        # Consolidate success: Keep only the last detected success response for simplicity
        if responses["success"]:
            responses["success"] = responses["success"][-1]
        else:
            responses["success"] = (
                None  # Explicitly set to None if no success response found
            )

        # Deduplicate errors based on statusCode + description
        unique_errors = []
        seen_errors = set()
        for err in responses["errors"]:
            key = (err["statusCode"], err["description"])
            if key not in seen_errors:
                seen_errors.add(key)
                unique_errors.append(err)
        responses["errors"] = unique_errors

        return responses

    def _infer_schema_from_response_body(self, body_content):
        """Attempt to infer OpenAPI schema from parsed object or JS object literal string."""

        # --- Handle Parsed Objects (Preferred) ---
        # If json.loads succeeded, recursively infer schema from the Python object
        if isinstance(body_content, dict):
            schema = {"type": "object", "properties": {}}
            for key, value in body_content.items():
                schema["properties"][key] = self._infer_schema_from_value(key, value)
            return schema
        elif isinstance(body_content, list):
            items_schema = {"type": "any"}
            if body_content:  # Infer item type from first element if list is not empty
                items_schema = self._infer_schema_from_value("", body_content[0])
            return {"type": "array", "items": items_schema}

        # --- Handle String Content (Regex Fallback) ---
        # This is used if json.loads failed or the body wasn't a JS object/array literal
        if not isinstance(body_content, str):
            # Handle non-string primitives if body_content wasn't a dict/list/str
            if isinstance(body_content, bool):
                return {"type": "boolean"}
            if isinstance(body_content, (int, float)):
                return {"type": "number"}
            if body_content is None:
                return {"type": "null"}
            return {"type": "string"}  # Default guess

        body_str = body_content.strip()

        # Infer from string looking like an object literal: { key: value }
        if body_str.startswith("{") and body_str.endswith("}"):
            schema = {"type": "object", "properties": {}}
            # Basic regex for top-level key-value pairs (won't handle nesting well)
            prop_pattern = re.compile(
                r'([a-zA-Z_$][\w$]*|\'[^\']*\'|"[^"]*")\s*:\s*([^,}]+(?:\{.*?\}|\[.*?\])?)'
            )
            for key_match, value_match in prop_pattern.findall(body_str[1:-1]):
                key = key_match.strip("'\"")
                value_str = value_match.strip()
                schema["properties"][key] = self._infer_schema_from_value_string(
                    key, value_str
                )
            # Return empty object schema if no properties found by regex
            return schema if schema["properties"] else {"type": "object"}

        # Infer from string looking like an array literal: [ item1, item2 ]
        elif body_str.startswith("[") and body_str.endswith("]"):
            items_schema = {"type": "any"}
            # Basic heuristics for item type
            if "{" in body_str and "}" in body_str:
                items_schema = {"type": "object"}
            elif '"' in body_str or "'" in body_str:
                items_schema = {"type": "string"}
            elif re.search(r"\d", body_str):
                items_schema = {"type": "number"}
            return {"type": "array", "items": items_schema}

        # Infer from string looking like a string literal: "hello" or 'hello'
        elif (
            (body_str.startswith("'") and body_str.endswith("'"))
            or (body_str.startswith('"') and body_str.endswith('"'))
            or (body_str.startswith("`") and body_str.endswith("`"))
        ):
            return {"type": "string"}

        # If it looks like a variable name, guess object (common case for variable response)
        elif re.match(r"^[a-zA-Z_$][\w$]*$", body_str):
            return {"type": "object"}  # Could be anything, object is a safe guess
        else:
            # Default fallback guess for unrecognized string content
            return {"type": "string"}

    def _infer_schema_from_value(self, key, value):
        """Helper to recursively infer schema from a *parsed* Python value."""
        prop_schema = {}
        if isinstance(value, str):
            prop_schema = {"type": "string"}
        elif isinstance(value, bool):
            prop_schema = {"type": "boolean"}
        elif isinstance(value, (int, float)):
            prop_schema = {"type": "number"}
        elif isinstance(value, dict):
            # Recurse for nested objects
            prop_schema = {"type": "object", "properties": {}}
            for sub_key, sub_value in value.items():
                prop_schema["properties"][sub_key] = self._infer_schema_from_value(
                    sub_key, sub_value
                )
        elif isinstance(value, list):
            # Recurse for arrays, inferring item type from first element
            items_schema = {"type": "any"}
            if value:  # Infer from first item if list is not empty
                items_schema = self._infer_schema_from_value(
                    "", value[0]
                )  # No key for array item
            prop_schema = {"type": "array", "items": items_schema}
        elif value is None:
            prop_schema = {"type": "null"}
        else:
            prop_schema = {"type": "any"}  # Fallback for unexpected types

        # Add format hint based on key name and inferred type
        prop_format = self._infer_parameter_format(key, prop_schema.get("type", "any"))
        if prop_format:
            prop_schema["format"] = prop_format
        return prop_schema

    def _infer_schema_from_value_string(self, key, value_str):
        """Helper to infer schema from a *string* value (regex fallback)."""
        prop_schema = {"type": "any"}  # Default

        # Infer type from string value syntax
        if (
            value_str.startswith("'")
            or value_str.startswith('"')
            or value_str.startswith("`")
        ):
            prop_schema = {"type": "string"}
        elif value_str.isdigit() or re.match(r"parseInt\s*\(", value_str):
            prop_schema = {"type": "number"}
        elif value_str in ["true", "false"]:
            prop_schema = {"type": "boolean"}
        elif value_str == "null" or value_str == "undefined":
            prop_schema = {"type": "null"}
        elif value_str.startswith("{"):
            prop_schema = {"type": "object"}  # Not recursing in string mode
        elif value_str.startswith("["):
            # Basic item type inference for arrays in string mode
            items_type = "any"
            if "{" in value_str:
                items_type = "object"
            elif "'" in value_str or '"' in value_str:
                items_type = "string"
            elif re.search(r"\d", value_str):
                items_type = "number"
            prop_schema = {"type": "array", "items": {"type": items_type}}
        elif re.match(r"req\.(?:params|body|query)\.(\w+)", value_str):
            # If value is like req.body.userId, try to infer type from that param
            var_name = re.match(r"req\.(?:params|body|query)\.(\w+)", value_str).group(
                1
            )
            inferred_type = self._infer_parameter_type(var_name).split(" | ")[
                0
            ]  # Take first guess
            prop_schema = (
                {"type": inferred_type} if inferred_type != "any" else {"type": "any"}
            )

        # Add format hint based on key name
        prop_format = self._infer_parameter_format(key, prop_schema.get("type", "any"))
        if prop_format:
            prop_schema["format"] = prop_format
        return prop_schema

    def _infer_validation_constraints(self, handler_body):
        """Infer validation constraints from error messages or common library usage."""
        constraints = []
        # Look for common validation keywords in error response strings
        validation_msgs = re.finditer(
            r'(?:send|json|status)\([^)]*[\'"]([^\'"]*(required|invalid|must|minimum|maximum|length|not found|unauthorized)[^\'"]*)[\'"]\)',
            handler_body,
            re.IGNORECASE,
        )
        for match in validation_msgs:
            message = match.group(1).strip()
            if message and message not in constraints:
                constraints.append(message)

        # Look for common validation library patterns (e.g., express-validator, joi, yup)
        validation_libs = [
            (
                r'body\([\'"](\w+)[\'"]\)\.(is[A-Z]\w+|notEmpty|exists)',
                "Validate $1 using express-validator: $2",
            ),  # express-validator body()
            (
                r'check\([\'"](\w+)[\'"]\)\.(is[A-Z]\w+|notEmpty|exists)',
                "Validate $1 using express-validator: $2",
            ),  # express-validator check()
            (
                r"joi\.(string|number|boolean|object)\(\)(?:\.(?:required|min|max|length|email|pattern)\(.*\))+",
                "Validate using Joi: $1",
            ),  # Basic Joi chain
            (
                r"yup\.(string|number|boolean|object)\(\)(?:\.(?:required|min|max|length|email)\(.*\))+",
                "Validate using Yup: $1",
            ),  # Basic Yup chain
        ]
        for pattern, template in validation_libs:
            for match in re.finditer(pattern, handler_body, re.IGNORECASE | re.DOTALL):
                # Extract field name or type based on pattern group count
                field_or_type = match.group(1)
                method = match.group(2) if len(match.groups()) > 1 else ""
                constraint = (
                    template.replace("$1", field_or_type).replace("$2", method).strip()
                )
                if constraint not in constraints:
                    constraints.append(constraint)
        return constraints

    def _infer_resource_from_context(self, function_name, route_path):
        """Infer the primary resource (e.g., User, Product) using path, function name, and NLP."""
        resource_keywords = [
            "user",
            "product",
            "order",
            "item",
            "account",
            "post",
            "comment",
            "category",
            "session",
            "profile",
            "cart",
            "payment",
            "address",
            "book",
            "article",
            "event",
        ]

        # 1. Check significant path components (e.g., /users/:id -> User)
        path_parts = [
            part
            for part in route_path.strip("/").split("/")
            if not part.startswith(":") and part
        ]
        if path_parts:
            potential_resource = path_parts[0].lower()
            singular_resource = (
                potential_resource[:-1]
                if potential_resource.endswith("s")
                else potential_resource
            )
            if singular_resource in resource_keywords:
                return singular_resource.capitalize()
            # Try NLP NER/POS on the first path part if keyword match failed
            if self.nlp:
                doc = self.nlp(path_parts[0])
                if doc.ents:  # Prefer named entities
                    return doc.ents[0].text.capitalize()
                nouns = [
                    token.lemma_.capitalize()
                    for token in doc
                    if token.pos_ in ["NOUN", "PROPN"]
                ]
                if nouns:
                    return nouns[0]  # Fallback to first noun lemma

        # 2. Check function name using keywords and NLP
        func_name_lower = function_name.lower()
        for keyword in resource_keywords:
            if keyword in func_name_lower:
                return keyword.capitalize()
        # Try NLP on function name if keywords failed and name is not anonymous
        if self.nlp and function_name != "anonymous":
            doc = self.nlp(function_name)
            if doc.ents:  # Prefer named entities
                return doc.ents[0].text.capitalize()
            # Find noun lemmas, excluding common action verbs
            action_verbs = {
                "get",
                "list",
                "find",
                "create",
                "add",
                "update",
                "edit",
                "delete",
                "remove",
                "handle",
                "process",
                "set",
                "register",
            }
            nouns = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"]]
            meaningful_nouns = [n for n in nouns if n.lower() not in action_verbs]
            if meaningful_nouns:
                return meaningful_nouns[
                    0
                ].capitalize()  # Return first meaningful noun found

        # 3. Default fallback to the first path component if available
        if path_parts:
            return path_parts[0].capitalize()

        return "Unknown"  # Default if no resource could be inferred

    def _infer_purpose_from_context(self, function_name, method, resource):
        """Infer the endpoint's purpose using HTTP method, function name (NLP enhanced), and resource."""
        func_name_words = []
        # Use NLP POS tagging on function name if available
        if (
            self.nlp
            and function_name != "anonymous"
            and (self.nlp.has_pipe("tagger") or "tagger" in self.nlp.pipe_names)
        ):
            doc = self.nlp(function_name)
            # Extract lemmas of Verbs, Nouns, Proper Nouns
            func_name_words = [
                token.lemma_.lower()
                for token in doc
                if token.pos_ in ["VERB", "NOUN", "PROPN"]
            ]
            # Remove the inferred resource itself to avoid redundancy (e.g., "Create User user")
            if resource != "Unknown" and resource.lower() in func_name_words:
                func_name_words.remove(resource.lower())
        else:
            # Basic CamelCase/snake_case split if NLP unavailable or anonymous function
            func_name_words = re.findall(
                r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", function_name
            )
            func_name_words = [w.lower() for w in func_name_words]

        # Map HTTP method to a default action verb
        action_map = {
            "GET": "Retrieve",
            "POST": "Create",
            "PUT": "Update",
            "PATCH": "Partially update",
            "DELETE": "Delete",
        }
        action = action_map.get(method, "Handle")  # Default to "Handle"

        # Refine action based on specific verbs found in the function name
        verb_map = {
            "get": "Retrieve",
            "list": "List",
            "find": "Find",
            "search": "Search",
            "fetch": "Fetch",
            "create": "Create",
            "add": "Add",
            "new": "Register",
            "post": "Post",
            "register": "Register",
            "update": "Update",
            "edit": "Edit",
            "modify": "Modify",
            "set": "Set",
            "patch": "Patch",
            "delete": "Delete",
            "remove": "Remove",
            "cancel": "Cancel",
            "process": "Process",
            "handle": "Handle",
            "login": "Log in",
            "logout": "Log out",
            "authenticate": "Authenticate",
            "authorize": "Authorize",
        }
        identified_verb = ""
        for word in func_name_words:
            if word in verb_map:
                identified_verb = verb_map[word]
                break
        if identified_verb:
            action = identified_verb  # Override default action if specific verb found

        # Determine if resource should be plural (e.g., List Users vs Retrieve User)
        is_plural = False
        # Plural likely for GET list/search, or if function name implies multiple items
        if method == "GET" and (
            action == "List" or "all" in func_name_words or "search" in func_name_words
        ):
            is_plural = True
            action = "List"  # Standardize action for listing multiple
        elif method == "GET":  # Single GET by ID usually singular
            is_plural = False
        elif method == "POST":  # Creating one resource usually singular result context
            is_plural = False
        # PUT/PATCH/DELETE usually operate on a single resource ID
        elif method in ["PUT", "PATCH", "DELETE"]:
            is_plural = False

        # Construct the resource display string (singular or plural)
        resource_display = resource if resource != "Unknown" else "resource"
        if is_plural:
            # Basic pluralization (append 's' unless already ends in 's')
            resource_display += "s" if not resource_display.endswith("s") else ""
        else:
            # Ensure resource is singular if needed
            if (
                resource_display.endswith("s") and len(resource_display) > 1
            ):  # Avoid making 's' -> ''
                resource_display = resource_display[:-1]

        # Add extra context words from function name if they weren't the main action verb or resource
        extra_context = " ".join(
            w
            for w in func_name_words
            if w not in verb_map and w != resource.lower() and w != action.lower()
        )
        purpose = f"API endpoint to {action.lower()} {resource_display}"
        if extra_context.strip() and extra_context.strip() != "anonymous":
            purpose += f" related to {extra_context.strip()}"
        purpose += "."
        return purpose

    def _extract_function_name(self, handler_text):
        """Extract function name from handler text (e.g., 'getUser', 'function createUser(...)')."""
        # Case 1: Direct reference to a named function or controller method
        if re.match(
            r"^[a-zA-Z_$][\w$.]*$", handler_text
        ):  # Allows dot notation like controller.method
            return handler_text
        # Case 2: Inline function declaration: function name(...) { ... }
        func_decl = re.match(r"function\s+([a-zA-Z_$][\w$]*)", handler_text)
        if func_decl:
            return func_decl.group(1)
        # Case 3: Arrow function assigned to const/let/var (try to find variable name)
        # Example: const getUser = (...) => { ... }
        # This requires looking *before* the route definition, complex. Omitted for now.

        # Default for anonymous functions (e.g., app.get('/', (req, res) => {...}))
        return "anonymous"

    def _build_standardized_responses(self, responses_data):
        """Convert raw extracted response data into a standardized success/error structure."""
        result = {"successResponse": None, "errorResponses": []}
        if responses_data["success"]:
            # Assumes responses_data['success'] holds the single chosen success response object
            result["successResponse"] = {
                "statusCode": responses_data["success"]["statusCode"],
                "description": responses_data["success"]["description"],
                "schema": responses_data["success"]["schema"],
            }
        if responses_data["errors"]:
            # Assumes responses_data['errors'] holds the list of unique error response objects
            for error in responses_data["errors"]:
                result["errorResponses"].append(
                    {
                        "statusCode": error["statusCode"],
                        "description": error["description"],
                        "schema": error["schema"],
                    }
                )
        return result

    def extract_api_info(self):
        """Extracts API documentation information for all routes found in the file."""
        docs = []
        for route in self._find_route_definitions():
            method = route["method"].upper()
            path = route["path"]
            # Extract the code block for the handler function
            body = self._extract_function_body(route["handler_start"])
            if not body:  # Skip if handler body couldn't be extracted
                continue

            # Extract function name for context
            func_name = self._extract_function_name(route["handler_text"])
            # Infer resource (e.g., User) using name and path
            resource = self._infer_resource_from_context(func_name, path)
            # Infer purpose (e.g., Retrieve users) using name, method, resource
            purpose = self._infer_purpose_from_context(func_name, method, resource)
            # Extract parameters (path, query, body)
            params = self._extract_parameters(body, path)
            # Extract response details (status codes, descriptions, schemas)
            responses_data = self._extract_responses(body)
            standardized_responses = self._build_standardized_responses(responses_data)
            # Infer validation constraints from error messages or library usage
            required_constraints = []
            for source, source_params in params.items():
                for name, info in source_params.items():
                    if (
                        info.get("required", False) and source != "path"
                    ):  # Path params handled via structure
                        required_constraints.append(
                            f"Parameter '{name}' in {source} is required."
                        )
            freeform_constraints = self._infer_validation_constraints(body)
            all_constraints = required_constraints + freeform_constraints
            validation = {"inputConstraints": all_constraints}

            # Remove empty parameter categories (path, query, body) if no params found
            params = {k: v for k, v in params.items() if v}

            docs.append({
                "codeContext": {
                    "filename": self.relative_path,  # Use relative path instead of just filename
                    "functionName": func_name,
                    "line": route["line"],
                    "general_purpose": purpose
                },
                "apiDetails": {
                    resource.lower() + "s": {  # Pluralize resource name
                        "endpoint": {
                            "path": path,
                            "methods": [method],
                            "resourceType": resource
                        },
                        "parameters": params if params else {},
                        "responses": {
                            "success": self._convert_success_response(standardized_responses["successResponse"], method),
                            "error": self._convert_error_responses(standardized_responses["errorResponses"])
                        }
                    }
                }
            })
        return docs

    def _convert_success_response(self, success_response, method):
        """Convert success response to match context.py format."""
        if not success_response:
            return {}
            
        method_map = {
            "GET": "get_one" if "/{" in self.filepath else "get_all",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        
        action = method_map.get(method, "handle")
        
        return {
            action: {
                "statusCode": success_response["statusCode"],
                "description": success_response["description"],
                **({"schema": success_response["schema"]} if "schema" in success_response else {})
            }
        }

    def _convert_error_responses(self, error_responses):
        """Convert error responses to match context.py format."""
        if not error_responses:
            return {}
            
        result = {}
        for error in error_responses:
            result[str(error["statusCode"])] = {
                "description": error["description"],
                "conditions": [error["description"]]  # Use description as condition
            }
        return result
