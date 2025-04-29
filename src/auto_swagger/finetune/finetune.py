#!/usr/bin/env python
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
from auto_swagger.config.settings import MODEL_OUTPUT_DIR, FINETUNE_DATA_PATH

class FineTuner:
    def __init__(self):
        self.output_dir = MODEL_OUTPUT_DIR
        self.jsonl_path = FINETUNE_DATA_PATH
        self.stop_token = "<|endofjsdoc|>"
        self.tokenizer = None
        self.model_name = "deepseek-ai/deepseek-coder-1.3b-instruct"
        
    def setup_tokenizer(self):
        """Initialize the tokenizer with the model and stop token"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        
        # Register stop token with the tokenizer if needed
        if self.stop_token not in self.tokenizer.get_vocab():
            special_tokens_dict = {'additional_special_tokens': [self.stop_token]}
            self.tokenizer.add_special_tokens(special_tokens_dict)
            
    def preprocess_data_individual(self, example):
        """Process one example at a time"""
        prompt = f"<s>system\nYou are an expert in API documentation that generates JSDoc Swagger comments.\n\nuser\n{example['prompt']}\n\nassistant\n"
        completion = example['completion']
        
        # Tokenize prompt and completion separately
        prompt_tokens = self.tokenizer(prompt, truncation=True, padding=False, return_tensors=None)
        completion_tokens = self.tokenizer(completion, truncation=True, padding=False, return_tensors=None)
        
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

    def load_model(self):
        """Load and prepare the model for training"""
        # Determine device
        self.device = torch.device("mps" if torch.backends.mps.is_available() else 
                            ("cuda" if torch.cuda.is_available() else "cpu"))
        print(f"Using device: {self.device}")
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            device_map="auto"
        )
        
        # Resize token embeddings to account for the stop token
        self.model.resize_token_embeddings(len(self.tokenizer))
        
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
        self.model = prepare_model_for_kbit_training(self.model, use_gradient_checkpointing=True)
        self.model = get_peft_model(self.model, lora_config)

    def train(self):
        """Train the model"""
        # Load data
        data = load_jsonl(self.jsonl_path)
        dataset = Dataset.from_dict({
            "prompt": [item["prompt"] for item in data],
            "completion": [item["completion"] for item in data],
        })
        
        # Process each example individually
        tokenized_dataset = dataset.map(
            self.preprocess_data_individual,
            remove_columns=["prompt", "completion"]
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=4,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            warmup_steps=50,
            learning_rate=3e-4,
            fp16=self.device.type == "cuda",
            bf16=self.device.type == "mps",
            logging_steps=10,
            save_steps=50,
            save_total_limit=3,
            report_to="none",
            remove_unused_columns=False,
        )
        
        # Set up trainer with custom collator
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            tokenizer=self.tokenizer,
            data_collator=CustomDataCollator(tokenizer=self.tokenizer),
        )
        
        # Train and save
        self.model.config.use_cache = False
        trainer.train()
        
        # Save the LoRA adapter only
        self.model.save_pretrained(str(self.output_dir))
        self.tokenizer.save_pretrained(str(self.output_dir))
        
        print(f"Fine-tuning complete! LoRA adapters saved to {self.output_dir}")

class CustomDataCollator(DataCollatorForLanguageModeling):
    def __init__(self, tokenizer):
        super().__init__(tokenizer=tokenizer)
        self.tokenizer = tokenizer
        
    def __call__(self, features):
        # First pad the inputs to the same length
        max_length = max(len(f["input_ids"]) for f in features)
        
        for feature in features:
            padding_length = max_length - len(feature["input_ids"])
            
            # Pad input_ids and attention_mask
            feature["input_ids"] = feature["input_ids"] + [self.tokenizer.pad_token_id] * padding_length
            feature["attention_mask"] = feature["attention_mask"] + [0] * padding_length
            
            # Pad labels with -100 (ignored in loss calculation)
            feature["labels"] = feature["labels"] + [-100] * padding_length
            
        # Convert to tensors
        batch = {
            k: torch.tensor([f[k] for f in features]) 
            for k in features[0].keys()
        }
        
        return batch

def load_jsonl(file_path):
    """Load data from a JSONL file"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def main():
    """Main entry point"""
    finetuner = FineTuner()
    finetuner.setup_tokenizer()
    finetuner.load_model()
    finetuner.train()

if __name__ == "__main__":
    main()
