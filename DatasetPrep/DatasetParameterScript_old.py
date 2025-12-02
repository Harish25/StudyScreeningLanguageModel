# Copyright 2025 H. Umapathithasan, A. Vasantharasan, N. Mehanathan, & N. Kannan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI

#Script to extract additional parameters for papers in dataet

#CSV Values
path = "../Dataset/good_papers_with_topics.csv" 
dataCSV = pd.read_csv(path)
doiList = dataCSV["DOI"].tolist()

load_dotenv('key.env')

#PDF retrieval API values
EMAIL = os.getenv('UNPAYWALL_EMAIL')
API = 'https://api.unpaywall.org/v2/'
output_directory = './PDF_output'

#GPT API setup
client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

pdf_texts = []

#Downloads PDF file and then reads it as text
def pdfConvert(pdf_url, output_dir, filename):
    try:
        #Create output dir
        os.makedirs(output_dir, exist_ok=True)

        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        #Download PDF to ./PDF_output
        pdf_filepath = os.path.join(output_dir, f"{filename}.pdf")
        with open(pdf_filepath, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                pdf_file.write(chunk)

        #Extract text from the PDF
        pdf_reader = PdfReader(pdf_filepath)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()

        return pdf_text

    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
    except Exception as e:
        print(f"Error processing PDF: {e}")
    return None


#Loop to retrieve text for all PDFs
for doi in doiList:

    #Paper API
    response = requests.get(f'{API}{doi}?email={EMAIL}')
    if response.status_code == 200:
        data = response.json()
        jsonResponse = data.get('best_oa_location')

        if jsonResponse is not None:
            pdf_url = jsonResponse.get('url_for_pdf')
            if pdf_url and pdf_url != 'PDF URL not found':
                # print(f"Downloading PDF for DOI: {doi}")
                # print("PDF URL: " + pdf_url)

                filename = doi.replace('/', '_')
                text = pdfConvert(pdf_url, output_directory, filename)

                # Append the extracted text to array of all PDF texts
                pdf_texts.append(text)    
            else:
                # print(f"No PDF URL found for DOI: {doi}")
                pdf_texts.append(None)
        else:
            # print(f"No open access found for DOI: {doi}")
            pdf_texts.append(None)
    else:
        # print(f"Failed to retrieve data for DOI: {doi}. Status code: {response.status_code}")
        pdf_texts.append(None)

print("PDF downloading and text conversion complete")

def gpt_request(message):
  gen_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": message}]
  )

  return gen_response.choices[0].message.content

#GPT Prompt setup
prompt1="For the following biomedical paper: "
prompt2="\nPlease extract the following details from the paper: Number of references, Study Type (such as RCT, observational, cohort, case-control, etc.), Study Population Size, Control Group Size, Sampling Method (Randomized, convenience sampling, or stratified sampling)"
prompt3="ONLY respond with the extracted details in the given order with each detail separated by a comma. Only the value itself should be included with terms such as 'Number of references' and 'Study Type' being left out of the output"

request_limit = 0
#Prompt GPT to extract requested parameters from pdf_texts
for i, pdf_text in enumerate(pdf_texts):
    if(pdf_text != None):
        final_prompt = prompt1 + pdf_text + prompt2 + prompt3
        response = gpt_request(final_prompt)

        parameters = response.split(",")

        dataCSV.loc[i, "Number of references"] = parameters[0]
        dataCSV.loc[i, "Study Type"] = parameters[1]
        dataCSV.loc[i, "Study Population Size"] = parameters[2]
        dataCSV.loc[i, "Control Group Size"] = parameters[3]
        dataCSV.loc[i, "Sampling Method"] = parameters[4]
        
        request_limit += 1
    else:   #PDF file not retrieved
        dataCSV.loc[i, "Number of references"] = ""
        dataCSV.loc[i, "Study Type"] = ""
        dataCSV.loc[i, "Study Population Size"] = ""
        dataCSV.loc[i, "Control Group Size"] = ""
        dataCSV.loc[i, "Sampling Method"] = ""

    if request_limit > 450:
        print("\n-Soft Limit Reached-")
        time.sleep(60)
        request_limit = 0

#Save modified CSV file with parameters
savePath = "../Dataset/DatasetParams/good_papers_with_topics.csv"
dataCSV.to_csv(savePath)