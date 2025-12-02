---
base_model: unsloth/llama-3.2-3b-instruct-unsloth-bnb-4bit
library_name: peft
---

# Model Card

This model was fine-tuned from the Llama 3.2 3B Instruct model.  
It is designed for the binary classfication of biomedical papers for a given topic to assist in SLRs.  
The following configuration represents the finalized best performing model from the experimentation phase.

- **Developed by:** Harish25
- **Model type:** LLM
- **Language(s) (NLP):** Multilingual
- **Finetuned from model:** unsloth/Llama-3.2-3B-Instruct
- **Hardware:** 1 RTX 4080 (16GB VRAM)

**For full model weights (.gguf/.safetensors) visit HuggingFace Repo**

## Performance Metrics

The model was evaluated on a held-out test set of 1057 papers

### Metrics on Run 1:
* TP=192, FP=58, TN=765, FN=40
* Number of correct answers: 957
* Number of wrong answers: 98
* Num of tests: 1057

* **Accuracy** = 0.9071090047393365
* **Recall** = 0.8275862068965517
* **Precision** = 0.768

### Metrics on Run 2:
* TP=194, FP=54, TN=770, FN=38
* Number of correct answers:  964
* Number of wrong answers:  92
* Num of tests:  1057

* **Accuracy** = 0.9128787878787878
* **Recall** = 0.8362068965517241
* **Precision** = 0.782258064516129

## Model Training Details

Trained using Unsloth.

### Hyperparameters
* **Epochs:** 3
* **Batch Size (Per Device):** 2
* **Gradient Accumulation Steps:** 4
* **Learning Rate:** 2e-4
* Optimizer: adamw_8bit
* LR Scheduler: Linear
* Weight Decay: 0.01
* Warmup Steps: 5
* Seed: 3407
* Max Sequence Length: 2048

### LoRA Configuration
* **Rank (r):** 32
* **Alpha (lora_alpha):** 32
* Dropout: 0 (Optimized)
* Target Modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`
* Bias: None

### Framework versions

- PEFT 0.13.2
- unsloth 2025.3.10

## Reproduction Code

The following code block details the exact configuration used to load and fine-tune the model. 
For full details check the notebook in this repo.

```python
from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer 
from transformers import TrainingArguments, DataCollatorForSeq2Seq
from unsloth import is_bfloat16_supported

max_seq_length = 2048   #Max num of input tokens
dtype = None            #auto-detect
load_in_4bit = True     #Using 4bit quantization

#Model Init
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Llama-3.2-3B-Instruct",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

#LoRA Adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 32,
    lora_alpha = 32,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
)

#Trainer Config
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = train_dataset_split,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    data_collator = DataCollatorForSeq2Seq(tokenizer = tokenizer),
    dataset_num_proc = 2,
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        num_train_epochs = 3,
        learning_rate = 2e-4,
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
        report_to = "none",
    ),
)
```