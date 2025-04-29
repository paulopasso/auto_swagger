import re
import json
from pathlib import Path
from config.settings import PROJECT_ROOT, SWAGGER_DOCS_DIR, FINETUNE_DATA_PATH

def prepare_finetune_data_jsdocs(input_dir, output_file, stop_token="<|endofjsdoc|>"):
    """
    Recursively scans .js files in input_dir, extracts each @openapi JSDoc block
    and its route handler stub, and writes prompt-completion pairs to a JSONL file
    for fine-tuning.

    Args:
        input_dir (str | Path): Directory to search for .js files.
        output_file (str | Path): Path to the output JSONL file.
        stop_token (str): Token to append at the end of each completion.
    """
    # Convert input paths to absolute paths
    input_dir = Path(input_dir).resolve()
    output_file = Path(output_file).resolve()

    # Regex to capture JSDoc block with @openapi and the following route stub
    pattern = re.compile(
        r"(/\*\*[\s\S]*?@openapi[\s\S]*?\*/)\s*"
        r"(app\.\w+\s*\([^)]*\)\s*=>\s*\{)",
        re.MULTILINE
    )

    examples = []

    for filepath in input_dir.rglob("*.js"):
        content = filepath.read_text(encoding='utf-8')
        for match in pattern.finditer(content):
            jsdoc = match.group(1).strip()
            stub = match.group(2).strip()

            # Clean up stub: ensure single brace and trailing semicolon
            stub_clean = re.sub(r"\{\s*\{", "{", stub)
            stub_clean = re.sub(r"\}\s*\}", "}", stub_clean)
            stub_clean = stub_clean.rstrip("{").strip() + "{};"

            prompt = (
                "Generate JSDoc Swagger comments for this Express route:\n"
                f"{stub_clean}"
            )
            completion = jsdoc.replace("\r\n", "\n") + "\n" + stop_token

            examples.append({
                "filepath": str(filepath.relative_to(PROJECT_ROOT)),
                "prompt": prompt,
                "completion": completion
            })

    # Write JSONL
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for ex in examples:
            json.dump(ex, out_f, ensure_ascii=False)
            out_f.write("\n")
    print(f"Collected {len(examples)} examples into {output_file}")


if __name__ == "__main__":
    prepare_finetune_data_jsdocs(SWAGGER_DOCS_DIR, FINETUNE_DATA_PATH)
