from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
SWAGGER_DOCS_DIR = DATA_DIR / "swagger_docs"
FINETUNE_DATA_PATH = DATA_DIR / "jsdocs_finetune.jsonl"

# Model paths
MODEL_OUTPUT_DIR = PROJECT_ROOT / "lora_adapters"