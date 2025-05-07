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

# Cropped Master

Once the Larvae tool is open, select input folder containing the images and tracked labels inside the same input folder but a sub folder called "labels"

Select output directory and new output folder name

Repeat for multiple folders if you wish to do so

Press process or process all

# DLC Training

Run DLC through Larvae AI Tool

Create new project follow steps in DLC GUI to input images/videos and annotate keypoints

Once annotated save and press check labels

Find Path to DLC Project in system

Open Config.yaml and change project path to place in Google Drive

Copy only config.yaml an labelled data fodler and upload as a zipped folder or folder to google drive

Run DLC Trainer Notebook/Script for training,evaluating and inference

# YOLO Training

Use ImageIMG to annotate frames

Use Yolo formatter script in VS Code

Input folder of images and labels, ensuring they have the same names respectively

Upload to kaggle and use YOLO Trainer notebook/script for training

# REID Training

Crop larvae from crops

Use REID Formatter script on VS Code

Assumes input folder looks like this

# ----input_root
# ------folder1
# --------0001_frame_xxxxx.png

Upload to kaggle and use REID Trainer notebook/script for training





