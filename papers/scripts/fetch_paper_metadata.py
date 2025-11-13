import requests
import pandas as pd
import os
import re

# Path to your DOI file
doi_file = "dois.txt"

# Output CSV
output_csv = "papers_metadata.csv"

# Function to explicitly replace accented characters with ASCII equivalents
def replace_accents(text):
    if not text:
        return ""
    replacements = {
        'á': 'a', 'Á': 'A',
        'é': 'e', 'É': 'E',
        'í': 'i', 'Í': 'I',
        'ó': 'o', 'Ó': 'O',
        'ú': 'u', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N',
        'ü': 'u', 'Ü': 'U'
    }
    for accented_char, replacement in replacements.items():
        text = text.replace(accented_char, replacement)
    return text

# Function to fetch metadata from CrossRef
def fetch_metadata(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()['message']

        title = replace_accents(data.get('title', [''])[0])
        authors = ', '.join([replace_accents(f"{a.get('given', '')} {a.get('family', '')}".strip()) 
                             for a in data.get('author', [])])
        journal = replace_accents(data.get('container-title', [''])[0])
        year = data.get('issued', {}).get('date-parts', [[None]])[0][0]

        return {
            'DOI': doi,
            'Title': title,
            'Authors': authors,
            'Journal': journal,
            'Year': year
        }

    except Exception as e:
        print(f"Error fetching {doi}: {e}")
        return {'DOI': doi, 'Title': '', 'Authors': '', 'Journal': '', 'Year': ''}

# Read DOIs from file
dois = []
with open(doi_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            doi = line.split()[-1].replace("https://doi.org/", "").replace("DOI:", "").strip()
            dois.append(doi)

# Fetch metadata
records = [fetch_metadata(doi) for doi in dois]

# Save to CSV
df = pd.DataFrame(records)
df.to_csv(output_csv, index=False, encoding='utf-8')
print(f"Metadata saved to {output_csv}")
