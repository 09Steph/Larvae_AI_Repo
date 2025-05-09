import os
import shutil
import random
from typing import List

# Class to create a REID dataset in Market1501 format
# Workflow:
# 1. Initialize the class with input and output folder paths, train and query ratios.
# 2. Create the output directories for train, query, and test images.
# 3. Generate the dataset by reading images from the input folders.
# 4. Randomly shuffle the images and split them into train, query, and test sets.
# 5. Rename the images according to the Market1501 format.
# Format: "PID"_c"CAMID"_s"SEQID"_frameID.png
# 6. Copy the images to the respective output directories.
# 7. Print the total number of images in each set.

# Note:
# This code assumes that the unique object ID (PID) is stored in the first 4 characters of filenames.
# It also assumes a single camera ID and sequence ID.
# The output format will follow the Market1501 dataset structure.
# Code is not part of GUI but can be used in as a standlone script 
# Use if main below as example usage

class REIDMarkerDataCreator:
    def __init__(self, input_root: str, output_root: str, train_ratio: float = 0.7, query_ratio: float = 0.2):
        self.input_root = input_root
        self.output_root = output_root
        self.train_ratio = train_ratio
        self.query_ratio = query_ratio
        self.bounding_box_train = os.path.join(output_root, "bounding_box_train")
        self.query = os.path.join(output_root, "query")
        self.bounding_box_test = os.path.join(output_root, "bounding_box_test")
        self.create_output_dirs()

    def create_output_dirs(self):
        for path in [self.bounding_box_train, self.query, self.bounding_box_test]:
            os.makedirs(path, exist_ok=True)

    def generate(self):
        all_folders = sorted([
            f for f in os.listdir(self.input_root)
            if os.path.isdir(os.path.join(self.input_root, f))
        ])
        
        for folder_idx, folder in enumerate(all_folders, 1):
            folder_path = os.path.join(self.input_root, folder)
            image_files = sorted([
                f for f in os.listdir(folder_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])

            if not image_files:
                continue

            pid = int(image_files[0].split('_')[0])  
            camid = 1
            seqid = 1

            random.shuffle(image_files)
            total_images = len(image_files)
            train_end = int(total_images * self.train_ratio)
            query_end = train_end + int(total_images * self.query_ratio)

            for i, filename in enumerate(image_files, 1):
                src = os.path.join(folder_path, filename)
                frame_id = i
                new_name = f"{pid:04d}_c{camid}s{seqid}_{frame_id:05d}.png"

                if i <= train_end:
                    dst = os.path.join(self.bounding_box_train, new_name)
                elif i <= query_end:
                    dst = os.path.join(self.query, new_name)
                else:
                    dst = os.path.join(self.bounding_box_test, new_name)

                shutil.copy(src, dst)
                print(f"[{i}/{total_images}] Processed: {src} → {dst}")

        print("REID dataset prepared in Market1501 format.")
        print(f"Total train images: {len(os.listdir(self.bounding_box_train))}")
        print(f"Total query images: {len(os.listdir(self.query))}")
        print(f"Total gallery images: {len(os.listdir(self.bounding_box_test))}")

# Example Usage
if __name__ == "__main__":
    reid_formatter = REIDMarkerDataCreator(
        input_root="/path/to/your/input/folders",
        output_root="/path/to/your/output/folder",
        train_ratio=0.7,
        query_ratio=0.2
    )
    reid_formatter.generate()
