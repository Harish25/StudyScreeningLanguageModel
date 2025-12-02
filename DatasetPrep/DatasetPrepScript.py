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

#File paths
qrel_file = "qrelSetA.txt"
pubmed_file = "PubMed-Title.txt"
output_file = "PubMed-Title-Cleaned.txt"

#Extract DOIs from qrelSetA.txt
def extract_dois_qrel(file_path):
    dois = set()
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 3:  #Assuming DOI is the 3rd column
                dois.add(parts[2])
    return dois

#Extract DOIs from PubMed-Title.txt
def extract_dois_pubmed(file_path):
    entries = []
    with open(file_path, "r") as file:
        for line in file:
            entries.append(line.strip())
    return entries

#Write cleaned PubMed data to a new file
def write_cleaned_file(file_path, cleaned_data):
    with open(file_path, "w") as file:
        for entry in cleaned_data:
            file.write(entry + "\n")


def remove_duplicates():
    #Extract DOIs from qrelSetA.txt
    qrel_dois = extract_dois_qrel(qrel_file)

    #Read PubMed-Title.txt and identify duplicates
    pubmed_entries = extract_dois_pubmed(pubmed_file)
    cleaned_entries = [entry for entry in pubmed_entries if entry.split()[2] not in qrel_dois]

    #Write cleaned entries to the output file
    write_cleaned_file(output_file, cleaned_entries)

    print(f"Removed duplicates. Cleaned file saved as {output_file}")

remove_duplicates()
