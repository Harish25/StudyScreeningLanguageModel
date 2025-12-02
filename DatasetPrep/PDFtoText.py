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

import requests
from PyPDF2 import PdfReader
import os

#Base URL and API key
EMAIL = 'Provide email'
BASE_URL = 'https://api.unpaywall.org/v2/'
output_directory = './output'

#List of DOIs
doiList = ['10.1038/s41586-020-2649-2', '10.1148/radiol.2020200274']

#Stores extracted text of each pdf
pdf_texts = []

#Function to download and convert pdf to text
def download_pdf_and_convert_to_text(pdf_url, output_dir, filename):
    try:
        os.makedirs(output_dir, exist_ok=True)

        #Download pdf
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()  #Check for req errors

        #Save PDF locally
        pdf_filepath = os.path.join(output_dir, f"{filename}.pdf")
        with open(pdf_filepath, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                pdf_file.write(chunk)

        #Extract pdf text
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


#Main loop to process DOIs
for doi in doiList:
    response = requests.get(f'{BASE_URL}{doi}?email={EMAIL}')
    if response.status_code == 200:
        data = response.json()
        best_oa_location = data.get('best_oa_location')

        if best_oa_location is not None:
            pdf_url = best_oa_location.get('url_for_pdf')
            if pdf_url and pdf_url != 'PDF URL not found':
                print(f"Downloading PDF for DOI: {doi}")
                filename = doi.replace('/', '_')  #Uses DOI as filename
                text = download_pdf_and_convert_to_text(pdf_url, output_directory, filename)
                if text:
                    pdf_texts.append(text)
            else:
                print(f"No PDF URL found for DOI: {doi}")
        else:
            print(f"No Open Access location found for DOI: {doi}")
    else:
        print(f"Failed to retrieve data for DOI: {doi}. Status code: {response.status_code}")

#Output: Array of extracted text
for i, text in enumerate(pdf_texts):
    print(f"\n--- Extracted Text from PDF {i + 1} ---\n")
  #  print(text)  #Print first 500 characters of each text


