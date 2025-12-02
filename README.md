# M.A.R.S. LM - Model Assisted Review System Language Model

![License](https://img.shields.io/badge/License-Apache%202.0-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Library](https://img.shields.io/badge/Unsloth-Fast_Fine--Tuning-yellow)
![Hardware](https://img.shields.io/badge/Hardware-RTX_4080-red)

**M.A.R.S. LM** (Model Assisted Review System Language Model) is an AI-powered LLM tool designed to automate the screening phase of **Biomedical Systematic Literature Reviews (SLRs)**.  
This repository contains the fine-tuning code for the system's core classifier, which utilizes a **Llama 3.2 3B Instruct** model to categorize research papers as **Good (Relevant)** or **Bad (Irrelevant)** for a given biomedical topic.

### Web Application Integration
The LLM acts as the classification engine for the full-stack M.A.R.S. web application, working downstream from OpenAI's GPT-4o (which is used for parameter extraction of PDF inputs) to streamline academic workflows.  

**[View the M.A.R.S. Web Interface Repository](https://github.com/ashwin-v1/Capstone)**

The web app provides a user-friendly interface to test the system. Upload PDFs, and the app handles text extraction, parameter extraction, and LLM querying automatically. 
* *Note: The web app requires an OpenAI API Key for parameter extraction and the model weights must be downloaded separately.*


## Model Weights

The model is hosted on Hugging Face in two merged formats:

* [**🤗 Merged 4-bit Model (.safetensors)**](https://huggingface.co/1nfuse/llama3.2-3B_SLR_FTmodel-4bit-3epoch)
* [**🤗 Quantized GGUF (.gguf)**](https://huggingface.co/1nfuse/llama3.2-3B_SLR_FTmodel-q4km-3epoch)


## Repository Structure

```text
├── data/                                 # Training and validation datasets (.csv)
├── data_prep/                            # Scripts for data cleaning and feature engineering
├── llama3.2_3B_fullParamDataset_3epoch/  # Final model config (metadata only)
├── UnslothLlama_3.2_3B_FineTune.ipynb    # Jupyter notebook for fine-tuning LLM (Unsloth)
├── inference_test.py                     # Python script to test model inference
├── requirements.txt                      # Python dependencies
└── README.md                             # Project documentation
```


## Dataset & Features

The model was trained on a curated dataset of **4,227 biomedical papers** (3,170 Training / 1,057 Testing).

### Input Features
Unlike standard text classifiers that often rely solely on the Abstract, this model is trained on specific parameters extracted from PDF documents:
* **Topic** & **Title**
* **Abstract**
* **Number of References**
* **Study Type**
* **Study Population Size**

*Note: Features such as Control Group Size and Sampling Method were analyzed but excluded during feature selection.*

### Target Labels
* **Good:** Relevant/High-quality paper.
* **Bad:** Irrelevant/Low-quality paper.


## Fine-Tuning Details

The model was fine-tuned using **Unsloth** and **LoRA (Low-Rank Adaptation)** on a single NVIDIA RTX 4080 (16GB VRAM).

* **Base Model:** `unsloth/Llama-3.2-3B-Instruct`
* **Optimizer:** AdamW 8-bit
* **Learning Rate:** 2e-4
* **Epochs:** 3
* **Context Length:** 2048 tokens
* **Quantization:** 4-bit (QLoRA)

To reproduce the training, run the notebook located at:
`UnslothLlama_3.2_3B_FineTune.ipynb`


## Performance

The model was evaluated on a held-out test set of **1,057 papers**.

| Metric | Score |
| :--- | :--- |
| **Accuracy** | **91.3%** |
| **Recall** | 0.836 |
| **Precision** | 0.782 |


## Getting Started

### 1. Installation
Clone the repository and install dependencies

**Note:**  
* To ensure GPU acceleration is enabled (Unsloth requires CUDA), please install PyTorch first, followed by the project requirements.
* Installation of this CUDA version requires Linux.

```bash
git clone https://github.com/Harish25/StudyScreeningLanguageModel.git
cd StudyScreeningLanguageModel

# 1. Install PyTorch with CUDA 12.4 support (Required for Unsloth)
pip install torch==2.5.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 2. Install the remaining dependencies
pip install -r requirements.txt
```

### 2. Fine-Tuning
To reproduce the model training process, run the provided notebook at: `UnslothLlama_3.2_3B_FineTune.ipynb`

### 3. Inference
You can test the model using the provided inference script. This loads the base model and applies the fine-tuned adapter.

```bash
python inference_test.py
```


## Credits & Acknowledgements

**Team Members:**
* H. Umapathithasan
* A. Vasantharasan
* N. Mehanathan
* N. Kannan
  
**Supervised by:**
* Dr. Faezeh Ensan

*Developed as part of Final Year Capstone Design Project.*  
*Toronto Metropolitan University, Department of Electrical, Computer, & Biomedical Engineering (2025).*

## License

This project is licensed under the Apache 2.0 License. The base Llama 3.2 model is governed by the Meta Llama 3.2 Community License.