import json
import nbformat
import os
import re

def anonymize_notebook(notebook_filename):
    # Load the notebook
    with open(notebook_filename, 'r') as file:
        notebook = nbformat.read(file, as_version=4)

    # Regular expressions for matching
    patterns = {
        r"\.\s*Ladd and LeBlanc": ". The Authors",
        r"\.\s*LeBlanc and Ladd": ". The Authors",
        "Ladd and LeBlanc": "the authors",
        "LeBlanc and Ladd": "the authors",
        "Ladd": "Author1",
        "LeBlanc": "Author2"
    }

    # Iterate through each cell
    for cell in notebook.cells:
        if cell.cell_type == 'markdown' or cell.cell_type == 'code':
            for pattern, replacement in patterns.items():
                cell.source = re.sub(pattern, replacement, cell.source)

    # Save the anonymized notebook
    with open(notebook_filename, 'w') as file:
        nbformat.write(notebook, file)

# Function to load source descriptions from a JSON file
def load_source_descriptions(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to check if a tag matches any of the source description keys
def tag_matches_sources(tag, cells):
    for cell in cells:
        # Create a regular expression pattern from the source tag
        # Replace '*' with '.*' to match any character(s)
        pattern = '^' + re.escape(cell["tag"]).replace("\\*", ".*") + '$'
        if re.match(pattern, tag):
            return cell["source"]
    return None

# Function to add metadata to cells with specific tags
def add_metadata_to_notebook(notebook_filename, sources):
    # Load the notebook
    with open(notebook_filename, 'r') as file:
        notebook = nbformat.read(file, as_version=4)

    # Iterate through each cell
    for cell in notebook.cells:
        if 'metadata' in cell and 'tags' in cell['metadata']:
            for tag in cell['metadata']['tags']:
                # Check if the tag matches any in our sources
                matching_source = tag_matches_sources(tag, sources)
                if matching_source:
                    # Add or update the 'jdh' metadata
                    cell['metadata']['jdh'] = {
                        "object": {
                            "source": matching_source
                        }
                    }

    # Save the updated notebook
    with open(notebook_filename, 'w') as file:
        nbformat.write(notebook, file)


# Function to find all cells with tags containing the word "figure"
def find_figure_cells(notebook_filename, output_filename, rerun_code=False):
    if os.path.exists(output_filename) or rerun_code:
        figure_cells = load_source_descriptions(output_filename)
    else:
        # Load the notebook
        with open(notebook_filename, 'r') as file:
            notebook = nbformat.read(file, as_version=4)

        figure_cells = []
        
        # Iterate through each cell
        for cell_index, cell in enumerate(notebook.cells):
            if 'metadata' in cell and 'tags' in cell['metadata']:
                for tag in cell['metadata']['tags']:
                    if ('figure' in tag) or ('table' in tag):
                        # Add cell index and tag to the list
                        figure_cells.append({"cell_index": cell_index, "tag": tag, "source": []})

        # Save the figure cells list to a JSON file
        with open(output_filename, 'w') as outfile:
            json.dump(figure_cells, outfile, indent=4)
    return figure_cells

if __name__ == '__main__':


    """Example usage
    "metadata": {
        "jdh": {
            "object": {
                "source": [
                    "This graph illustrates the frequency of 'Tool' in quotes from whatisdigitalhumanities.com and Day of DH."
                ]
            }
        },
        "tags": [
        "figure-whatisdh-tools-*",
        "narrative",
        "hermeneutics"
        ]
    }
    """
    #Example usage for adding metadata to article-text.ipynb
    # Generate lists of cells that need sources based on tags
    figure_cells = find_figure_cells('../article-text.ipynb', 'data/jsons/figure_cells.json')
    # Once manually added sources, add metadata to cells
    add_metadata_to_notebook('../article-text.ipynb', figure_cells)
    add_metadata_to_notebook('../article-text-partial-anonymous.ipynb', figure_cells)
    
    #Example usage for anonymizing article-text.ipynb
    ## Generate lists of cells that need sources based on tags
    figure_cells = find_figure_cells('../article-text-fully-anonymized.ipynb', 'data/jsons/figure_cells.json')
    # Once manually added sources, add metadata to cells
    add_metadata_to_notebook('../article-text-fully-anonymized.ipynb', figure_cells)
    ## Anonymize the notebook
    anonymize_notebook('../article-text-fully-anonymized.ipynb')