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
from dotenv import load_dotenv
import pandas as pd

from openai import OpenAI

#API Setup
load_dotenv('key.env')
client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

def gpt_request(message):
  gen_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": message}]
  )

  return gen_response.choices[0].message.content

#Prompt Setup
prompt1 = "This is the criteria for evaluating the biomedical papers as \"good\" or \"bad\". The maximum total score is 41, and each criteria point has a weight associated with it. If the paper has a score of at least 28 associated with it, it is classified as a \"good\" paper. If not, it's \"bad\". Mentions Key Terms: Abstract includes specific terms or concepts directly related to the research topic. Weight: 10. Study Type: Prioritize randomized controlled trials, cohort studies, or meta-analyses. Weight: 8. Sample Size and Details: Specifies a well-defined sample size and population. Weight: 7. Outcome Metrics: Includes measurable outcomes. Weight: 9. Study Design: Preference for longitudinal studies or studies with adequate duration for capturing outcomes. Weight: 7. \nPaper Details Title: "
prompt2 = "\nBased on the Title and Abstract from the paper details and using the criteria, determine if this paper is \"good\" or \"bad\". Only output the numerical value of the total score."

#Excel Setup
data_file_path = 'Enter dataset path'
data = pd.read_excel(data_file_path)

#Script Start
request_limit = 0
for row in data.itertuples():
  title = row.Title
  abstract = row.Abstract
  final_prompt = prompt1 + title + " Abstract: " + abstract + prompt2

  response = gpt_request(final_prompt)

  if int(response) >= 28:
    target_output = 1
  else:
    target_output = 0

  data.at[row.Index, "TargetOutput"] = target_output
  request_limit += 1

  if request_limit > 450:
    print("\n-Soft Limit Reached-")
    time.sleep(60)
    request_limit = 0

data.to_excel(data_file_path, index=False)

    





