import os
import pandas as pd
import json
import re

# Function to explicitly replace accented characters with ASCII equivalents
def replace_accents(text):
    if pd.isna(text) or not text:
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

# Function to make filesystem-safe names
def safe_filename(name):
    name = replace_accents(name)
    name = name.replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9_\-]", "", name)
    return name

# Path to CSV with metadata
metadata_csv = "papers_metadata.csv"
base_folder = "."  # papers/ folder

# Load metadata
df = pd.read_csv(metadata_csv, encoding='utf-8')

# Clean text fields
df['Authors'] = df['Authors'].apply(replace_accents)
df['Title'] = df['Title'].apply(replace_accents)
df['Journal'] = df['Journal'].apply(replace_accents)

for index, row in df.iterrows():
    authors = row['Authors']
    title = row['Title']
    journal = row['Journal']
    doi = row['DOI']
    year = str(int(row['Year'])) if not pd.isna(row['Year']) else "yyyy"
    decade = year[:3] + "0s" if year != "yyyy" else "unknown"

    # Folder structure: decade/year/paper
    decade_folder = os.path.join(base_folder, safe_filename(decade))
    os.makedirs(decade_folder, exist_ok=True)
    year_folder = os.path.join(decade_folder, safe_filename(year))
    os.makedirs(year_folder, exist_ok=True)
    first_author_last = authors.split(",")[0].split()[-1] if authors else "unknown"
    short_label = f"{first_author_last}_{year}"
    short_label_safe = safe_filename(short_label)
    folder_path = os.path.join(year_folder, short_label_safe)
    os.makedirs(folder_path, exist_ok=True)

    # Create README.md
    readme_path = os.path.join(folder_path, "README.md")
    with open(readme_path, "w", encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"**DOI:** {doi}\n\n")
        f.write(f"**Authors:** {authors}\n\n")
        f.write(f"**Journal:** {journal}\n\n")
        f.write(f"**Year:** {year}\n\n")
        f.write("## Description\n\nAdd notes about this paper, datasets, and figure-reproduction scripts here.\n")

    # Create friendly Jupyter notebook with Summary
    notebook_path = os.path.join(folder_path, f"{short_label_safe}_analysis.ipynb")
    if not os.path.exists(notebook_path):
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# {title}\n",
                        f"Analysis notebook for {short_label_safe}\n\n",
                        f"**Citation:** {authors}. ({year}). [{title}]({doi}). {journal}.\n\n",
                        "## Sections\n",
                        "- ### 1. Summary\n",
                        "- ### 2. Data\n",
                        "- ### 3. Analysis\n",
                        "- ### 4. Notes\n"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## 1. Summary\n",
                        "Provide a brief summary of the paper here.\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "## 2. Data\n",
                        "# Import necessary packages\n",
                        "import pandas as pd\n",
                        "import matplotlib.pyplot as plt\n",
                        "import seaborn as sns\n\n",
                        "# Load your data here, e.g.:\n",
                        "# df = pd.read_csv('your_dataset.csv')\n",
                        "# df.head()\n"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## 3. Analysis\n",
                        "Reproduce figures and analyses from the paper here.\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Example plotting template\n",
                        "# sns.set(style='whitegrid')\n",
                        "# plt.figure(figsize=(8,6))\n",
                        "# sns.lineplot(data=df, x='X_column', y='Y_column')\n",
                        "# plt.show()\n"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## 4. Notes\n",
                        "Add observations, insights, or future ideas here.\n"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.9"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }

        with open(notebook_path, 'w', encoding='utf-8') as nb:
            json.dump(notebook_content, nb, indent=2, ensure_ascii=False)
