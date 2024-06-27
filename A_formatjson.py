import json
import nbformat as nbf

# Read the JSON content from a file
with open('A_notebook_content.json', 'r') as f:
    data = json.load(f)

# Create a new notebook object
nb = nbf.v4.new_notebook()

# Add cells to the notebook
for cell in data['cells']:
    if cell['cell_type'] == 'markdown':
        new_cell = nbf.v4.new_markdown_cell(cell['source'])
    elif cell['cell_type'] == 'code':
        new_cell = nbf.v4.new_code_cell(cell['source'])
    nb.cells.append(new_cell)

# Write the notebook to a file
with open('Security_Company_Scheduler.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Jupyter Notebook created successfully.")
