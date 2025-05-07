# Larvae_AI_Repo
Repository containing the Larvae AI Tool, Version 1.1 Camera and LED System and additional AI Related Scripts
# Setup
Install Anconda or Miniconda
Ensure both are linked to system PATHs

Install VS Code - Same Development Environment used in project

# Larvae AI Usage
git clone repo 

cd ./path/to/Larvae_AI_Tool

conda env create -f environment.yml
conda activate GUI

python -m pip install -e .

python main.py

# Raspberry PI 
Install Python to PI

cd ./GUI_Transmitter

pip install -e .

python main.py

# MOT 
git clone https://github.com/mikel-brostrom/boxmot.git
cd boxmot
pip install uv
uv sync --group yolo
activate .venv/bin/activate

Copy the BoxMOT_Run.py in VS Code follow edits paths to models and folders
Copy ./labels folder after tracking to same root folder as images for Larvae AI Tool Cropped Master Button
