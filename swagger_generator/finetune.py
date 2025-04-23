#!/usr/bin/env python
import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import json
from datasets import Dataset

# Configuration
MODEL_NAME = "deepseek-ai/deepseek-coder-1.3b-instruct"
OUTPUT_DIR = "./lora_adapters"
JSONL_PATH = "data/jsdocs_finetune.jsonl"
STOP_TOKEN = "<|endofjsdoc|>"

# Determine device
device = torch.device("mps" if torch.backends.mps.is_available() else 
                     ("cuda" if torch.cuda.is_available() else "cpu"))
print(f"Using device: {device}")

# Load tokenizer early for use in preprocessing
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

# Register stop token with the tokenizer if needed
if STOP_TOKEN not in tokenizer.get_vocab():
    special_tokens_dict = {'additional_special_tokens': [STOP_TOKEN]}
    tokenizer.add_special_tokens(special_tokens_dict)

# Load data
def load_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

# Process one example at a time rather than batching
def preprocess_data_individual(example):
    prompt = f"<s>system\nYou are an expert in API documentation that generates JSDoc Swagger comments.\n\nuser\n{example['prompt']}\n\nassistant\n"
    completion = example['completion']
    
    # Tokenize prompt and completion separately
    prompt_tokens = tokenizer(prompt, truncation=True, padding=False, return_tensors=None)
    completion_tokens = tokenizer(completion, truncation=True, padding=False, return_tensors=None)
    
    # Combine tokens
    input_ids = prompt_tokens['input_ids'] + completion_tokens['input_ids']
    attention_mask = prompt_tokens['attention_mask'] + completion_tokens['attention_mask']
    
    # Create labels: -100 for prompt (ignored in loss), actual ids for completion
    labels = [-100] * len(prompt_tokens['input_ids']) + completion_tokens['input_ids']
    
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }

# Load model
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto"
)

# Resize token embeddings to account for the stop token
model.resize_token_embeddings(len(tokenizer))

# Configure LoRA
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
)

# Prepare model for LoRA
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
model = get_peft_model(model, lora_config)

# Set up the dataset
data = load_jsonl(JSONL_PATH)
dataset = Dataset.from_dict({
    "prompt": [item["prompt"] for item in data],
    "completion": [item["completion"] for item in data],
})

# Process each example individually
tokenized_dataset = dataset.map(
    preprocess_data_individual,
    remove_columns=["prompt", "completion"]
)

# Define a custom data collator to handle padding during batch creation
class CustomDataCollator(DataCollatorForLanguageModeling):
    def __call__(self, features):
        # First pad the inputs to the same length
        max_length = max(len(f["input_ids"]) for f in features)
        
        for feature in features:
            padding_length = max_length - len(feature["input_ids"])
            
            # Pad input_ids and attention_mask
            feature["input_ids"] = feature["input_ids"] + [tokenizer.pad_token_id] * padding_length
            feature["attention_mask"] = feature["attention_mask"] + [0] * padding_length
            
            # Pad labels with -100 (ignored in loss calculation)
            feature["labels"] = feature["labels"] + [-100] * padding_length
            
        # Convert to tensors
        batch = {
            k: torch.tensor([f[k] for f in features]) 
            for k in features[0].keys()
        }
        
        return batch

# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=4,  # Adjust as needed within your 3-5 range
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,  # Simulate batch size of 8
    warmup_steps=50,
    learning_rate=3e-4,
    fp16=device.type == "cuda",  # Use fp16 on CUDA
    bf16=device.type == "mps",   # Use bf16 on MPS
    logging_steps=10,
    save_steps=50,
    save_total_limit=3,
    report_to="none",
    remove_unused_columns=False,
)

# Set up trainer with custom collator
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=CustomDataCollator(tokenizer=tokenizer, mlm=False),
)

# Train and save
model.config.use_cache = False  # Needed for gradient checkpointing
trainer.train()

# Save the LoRA adapter only
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"Fine-tuning complete! LoRA adapters saved to {OUTPUT_DIR}") 