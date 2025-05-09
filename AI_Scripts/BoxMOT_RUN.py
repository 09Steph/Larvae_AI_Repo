# Script to run YOLOv8 tracking with DeepSORT and ReID model
# Follow README instructions for setup
# Place script within the root 'BoxMOT' directory after cloning the repository and setting up the environment
# Output of script will save a subfolder called ./labels containing the tracking results
# Copy ./labels to same directory as the folder of containing the images for the Larvae AI Tool GUI
import subprocess
import os
import time

BOX_DIR = os.path.dirname(os.path.abspath(__file__))

yolo_model = './path/to/yolo_model.pt'  
project = 'Name_of_project'
tracking_method = 'deepocsort'
reid_model = './path/to/reid_model.pth'  

folder_pairs = [
    ('input_folder_images', 'ouput_folder_name'),
]

total_start = time.time()

for source, name in folder_pairs:
    command = [
        'python',
        os.path.join(BOX_DIR, 'tracking', 'track.py'),
        '--yolo-model', yolo_model,
        '--source', source,
        '--project', project,
        '--name', name,
        '--conf', '0.35',
        '--iou', '0.5',
        '--save-txt',
        '--tracking-method', tracking_method,
        '--reid-model', reid_model
    ]
    
    print("\nRunning command:", " ".join(command))
    start = time.time()
    
    try:
        subprocess.run(command, check=True)
        elapsed = time.time() - start
        print(f"Finished processing '{source}' in {elapsed:.2f} seconds.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error while processing '{source}': {e}")

total_elapsed = time.time() - total_start
print(f"\nAll processing complete using tracker: {tracking_method}")
print(f"ReID model: {reid_model}")
print(f"YOLO model: {yolo_model}")
print(f"Total time: {total_elapsed:.2f} seconds")
