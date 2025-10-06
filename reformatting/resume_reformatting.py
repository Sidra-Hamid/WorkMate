#!apt-get install texlive-xetex texlive-fonts-recommended texlive-plain-generic -qq > /dev/null

import json
from jinja2 import Environment, FileSystemLoader
import subprocess
import os

# Define paths
base_dir = "/reformatting"
data_path = f"{base_dir}/data/resume.json"
template_dir = f"{base_dir}/template"
output_dir = f"{base_dir}/output"
os.makedirs(output_dir, exist_ok=True)

# Load JSON data
with open(data_path, "r") as f:
    resume_data = json.load(f)

# Function to escape ampersands recursively
def escape_ampersands(data):
    if isinstance(data, str):
        return data.replace('&', '\\&')
    elif isinstance(data, dict):
        return {k: escape_ampersands(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [escape_ampersands(item) for item in data]
    else:
        return data

# Escape ampersands in all data
resume_data = escape_ampersands(resume_data)

# Load LaTeX template
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template("resume_template.tex")

# Render with data
rendered_tex = template.render(**resume_data)

# Save .tex file
tex_path = f"{output_dir}/resume.tex"
with open(tex_path, "w") as f:
    f.write(rendered_tex)

# Compile to PDF
subprocess.run(["pdflatex", "-output-directory", output_dir, tex_path], check=True)

print("Resume generated successfully!")