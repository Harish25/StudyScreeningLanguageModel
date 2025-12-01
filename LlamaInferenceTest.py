from unsloth import FastLanguageModel
import torch

#Code for locally loading and testing inference
#Building prompt
identifier = "Global Seasonality of Human Seasonal Coronaviruses, Circulating Season of Severe Acute Respiratory Syndrome"
title = "Diversity and Evolutionary Histories of Human Coronaviruses NL63 and 229E Associated with Acute Upper Respiratory Tract Symptoms in Kuala Lumpur, Malaysia."
abstract = "The human alphacoronaviruses HCoV-NL63 and HCoV-229E are commonly associated with upper respiratory tract infections (URTI). Information on their molecular epidemiology and evolutionary dynamics in the tropical region of southeast Asia however is limited. Here, we analyzed the phylogenetic, temporal distribution, population history, and clinical manifestations among patients infected with HCoV-NL63 and HCoV-229E. Nasopharyngeal swabs were collected from 2,060 consenting adults presented with acute URTI symptoms in Kuala Lumpur, Malaysia, between 2012 and 2013. The presence of HCoV-NL63 and HCoV-229E was detected using multiplex polymerase chain reaction (PCR). The spike glycoprotein, nucleocapsid, and 1a genes were sequenced for phylogenetic reconstruction and Bayesian coalescent inference. A total of 68/2,060 (3.3%) subjects were positive for human alphacoronavirus; HCoV-NL63 and HCoV-229E were detected in 45 (2.2%) and 23 (1.1%) patients, respectively. A peak in the number of HCoV-NL63 infections was recorded between June and October 2012. Phylogenetic inference revealed that 62.8% of HCoV-NL63 infections belonged to genotype B, 37.2% was genotype C, while all HCoV-229E sequences were clustered within group 4. Molecular dating analysis indicated that the origin of HCoV-NL63 was dated to 1921, before it diverged into genotype A (1975), genotype B (1996), and genotype C (2003). The root of the HCoV-229E tree was dated to 1955, before it diverged into groups 1-4 between the 1970s and 1990s. The study described the seasonality, molecular diversity, and evolutionary dynamics of human alphacoronavirus infections in a tropical region."
references = "45"
studyType = "observational"
popSize = "2060"

#Good Target Value
user_prompt = f"For the given Topic: {identifier}\nAsnwer if the following academic paper is good or bad\nTitle: {title}\nAbstract: {abstract} Number of References: {references}\nStudy Type: {studyType}\nStudy Population Size: {popSize}"

#Bad Target Value
# user_prompt = "For the given Topic: The effect of comorbid pulmonary diseases on the severity of COVID-19 patients Asnwer if the following academic paper is good or bad Title: Association of chronic anticoagulant and antiplatelet use on disease severity in SARS-COV-2 infected patients. Abstract: No abstract found Number of References: 12.0 Study Type:  retrospective cohort study Study Population Size:  28076"

#Setup and Test model
max_seq_length = 2048   #Max num of input tokens (2048 tokens)
dtype = None            #None = auto-detect, selects optimal PyTorch data type, used to store model weights/activations
load_in_4bit = True     # (QLoRA = True) Using 4bit quantization

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "llama3.2_3B_fullParamDataset_3epoch",
    # chat_template = "llama-3.1",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)
FastLanguageModel.for_inference(model)


message = [
    {"role": "user", "content": user_prompt},
]

inputs = tokenizer.apply_chat_template(
    message,
    tokenize = True,
    add_generation_prompt = True, # Must add for generation
    return_tensors = "pt",
).to("cuda")

outputs = model.generate(input_ids = inputs, max_new_tokens = 64, use_cache = True,
                         temperature = 1.5, min_p = 0.1)
model_response = str(tokenizer.batch_decode(outputs))
ans = model_response.split("<|start_header_id|>assistant<|end_header_id|>")[1].split("<|eot_id|>")[0].strip()

print(f"Model Response: {model_response}\n\nAnswer: {ans}")
