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

ROOTDIR = "C:\\Projects\\VSCodeWorkspace\\StudyScreeningLanguageModel\\Dataset\\"

#CSV Values
path = ROOTDIR + "good_papers_with_topics.csv"
dataCSV = pd.read_csv(path)
doiList = dataCSV["DOI"].tolist()

#PDF retrieval API values
EMAIL = 'Provide email'
API = 'https://api.unpaywall.org/v2/'
output_directory = './PDF_output'

#GPT API setup
load_dotenv('key.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

#Function to download and extract text from a PDF
def pdfConvert(pdf_url, output_dir, filename):
    try:
        os.makedirs(output_dir, exist_ok=True)
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        pdf_filepath = os.path.join(output_dir, f"{filename}.pdf")
        with open(pdf_filepath, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                pdf_file.write(chunk)

        pdf_reader = PdfReader(pdf_filepath)
        pdf_text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        return pdf_text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
    except Exception as e:
        print(f"Error processing PDF: {e}")
    return None

#Function to request GPT extraction
def gpt_request(message):
    gen_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}]
    )
    return gen_response.choices[0].message.content

#GPT Prompt setup
prompt1 = "For the following biomedical paper: "
prompt2 = "\nPlease extract the following details from the paper: Number of references, Study Type (such as RCT, observational, cohort, case-control, etc.), Study Population Size, Control Group Size, Sampling Method (Randomized, convenience sampling, or stratified sampling)"
prompt3 = " ONLY respond with the extracted details in the given order with each detail separated by a comma. Only the value itself should be included with terms such as 'Number of references' and 'Study Type' being left out of the output"

#Process dataset in chunks
doiListSize = len(doiList)
startRange = 0
endRange = 500

print(f"Total # of entries to process {doiListSize}")

request_limit = 0

while endRange <= doiListSize:

    print(f"\nProcessing doi entries {startRange} to {endRange}")
  
    rowsToRemove = []
    #Process each DOI one by one
    for i, doi in enumerate(doiList[startRange:endRange]): #doiList[startRange : endRange]
        response = requests.get(f'{API}{doi}?email={EMAIL}')
        if response.status_code == 200:
            data = response.json()
            jsonResponse = data.get('best_oa_location')
            if jsonResponse:
                pdf_url = jsonResponse.get('url_for_pdf')
                if pdf_url and pdf_url != 'PDF URL not found':
                    filename = doi.replace('/', '_')
                    pdf_text = pdfConvert(pdf_url, output_directory, filename)
                    
                    if pdf_text:
                        final_prompt = prompt1 + pdf_text + prompt2 + prompt3
                        gpt_response = gpt_request(final_prompt)
                        parameters = gpt_response.split(",")
                        # print("GPT requests made, total req: ", request_limit)
                        
                        #Re-request gpt until right # of params given
                        gpt_reprompts = request_limit + 5
                        while (len(parameters) != 5 and request_limit < gpt_reprompts):
                                prompt_add = f"\nThe last response to this query had {len(parameters)} details. Ensure the comma seperated list contains ONLY the 5 requested details."
                                final_prompt = prompt1 + pdf_text + prompt2 + prompt3 + prompt_add
                                gpt_response = gpt_request(final_prompt)
                                parameters = gpt_response.split(",")

                                request_limit += 1
                                # print("GPT re-request made, total req: ", request_limit)

                        if len(parameters) == 5:
                            dataCSV.loc[startRange + i, "Number of references"] = parameters[0]
                            dataCSV.loc[startRange + i, "Study Type"] = parameters[1]
                            dataCSV.loc[startRange + i, "Study Population Size"] = parameters[2]
                            dataCSV.loc[startRange + i, "Control Group Size"] = parameters[3]
                            dataCSV.loc[startRange + i, "Sampling Method"] = parameters[4]
                        else: #Parameter mismatch
                            print("GPT Provided incorrect # of parameters for doi: ", doi)
                            print(f"For doi {doi} incorrect given parameters were: {parameters}")
                            rowsToRemove.append(startRange + i)
                    
                    else:   #PDF Text does not exist
                        rowsToRemove.append(startRange + i)
                else:       #PDF URL not found
                    rowsToRemove.append(startRange + i)
            else:   #No api JSON response
                rowsToRemove.append(startRange + i)
        else:   #API failed
            rowsToRemove.append(startRange + i)
        
        request_limit += 1
        # if request_limit > 450:
        #     print("\n-Soft Limit Reached-index: ", i)
        #     time.sleep(60)
        #     request_limit = 0
    
    #Drop rows w. invalid params
    saveCSV = dataCSV.drop(index=rowsToRemove)
    print("Invalid params dropped for indexes: ", rowsToRemove)

    #Include only processed rows for appending
    saveCSV = saveCSV.iloc[startRange:endRange - len(rowsToRemove)] #Move endRange back for # of rows removed
    #print(f"Appending rows from {startRange} to {endRange - len(rowsToRemove)}")

    #Append current loop progress
    savePath = ROOTDIR + "DatasetParams2\\good_papers_with_topics_with_params.csv"
    saveCSV.to_csv(savePath, mode='a', index=False, header=not os.path.exists(savePath))

    if(endRange == doiListSize):#End reached
        break

    startRange += 500
    endRange += 500
    startRange = min(startRange, doiListSize)
    endRange = min(endRange, doiListSize)

print("All Processing Complete.")