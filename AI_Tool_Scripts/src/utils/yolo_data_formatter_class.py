import os
import shutil
import random
from pathlib import Path
import yaml

# Class to format a dataset for YOLO training
# Workflow:
# 1. Initialize the class with input image and label directories, and output directory.
# 2. Create the YOLO directory structure.
# 3. Match image files with their corresponding label files.
# 4. Split the dataset into training, validation, and test sets based on specified percentages.
# 5. Copy the matched files into the respective directories.
# 6. Generate a .yaml file for YOLO configuration.
# 7. Print the total number of files in each set.

# Note:
# This code assumes that the label files are in YOLO format and have the same base name as the image files.
# Not part of GUI but can be used in as a standalone script
# Use if main below as example usage

class YoloDataFormatter:
    def __init__(self, images_dir, labels_dir, output_dir,
                 train_pct=0.8, val_pct=0.1, test_pct=0.1):
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.output_dir = output_dir
        self.train_pct = train_pct
        self.val_pct = val_pct
        self.test_pct = test_pct

    def __call__(self):
        print("Creating YOLO directory structure")
        self.create_yolo_structure()

        print("Matching image and label files")
        matched_pairs = self.get_matched_pairs()

        if not matched_pairs:
            print("No image-label pairs found. Aborting.")
            return

        print(f"Found {len(matched_pairs)} valid image-label pairs.")

        train, val, test = self.split_dataset(matched_pairs)

        print(f"Split result - Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

        print("Copying training files")
        self.copy_files(train, 'train')

        print("Copying validation files")
        self.copy_files(val, 'val')

        print("Copying test files")
        self.copy_files(test, 'test')

        print("Generating .yaml file")
        self.generate_yaml()

        print("Dataset formatting complete.")

    def create_yolo_structure(self):
        for split in ['train', 'val', 'test']:
            image_path = os.path.join(self.output_dir, 'images', split)
            label_path = os.path.join(self.output_dir, 'labels', split)
            os.makedirs(image_path, exist_ok=True)
            os.makedirs(label_path, exist_ok=True)
            print(f"Created: {image_path} and {label_path}")

    def get_matched_pairs(self):
        image_extensions = {'.jpg', '.jpeg', '.png'}
        image_files = [f for f in os.listdir(self.images_dir)
                       if Path(f).suffix.lower() in image_extensions]
        matched = []
        for img_file in image_files:
            label_file = Path(img_file).with_suffix('.txt')
            if (Path(self.labels_dir) / label_file).exists():
                matched.append((img_file, label_file))
        print(f"Matched {len(matched)} image-label pairs.")
        return matched

    def split_dataset(self, pairs):
        random.shuffle(pairs)
        total = len(pairs)
        train_end = int(self.train_pct * total)
        val_end = train_end + int(self.val_pct * total)
        train = pairs[:train_end]
        val = pairs[train_end:val_end]
        test = pairs[val_end:]
        return train, val, test

    def copy_files(self, pairs, split):
        total = len(pairs)
        for idx, (img_file, label_file) in enumerate(pairs, 1):
            img_src = os.path.join(self.images_dir, img_file)
            img_dst = os.path.join(self.output_dir, 'images', split, img_file)
            label_src = os.path.join(self.labels_dir, label_file)
            label_dst = os.path.join(self.output_dir, 'labels', split, label_file)

            shutil.copy(img_src, img_dst)
            shutil.copy(label_src, label_dst)

            print(f"[{idx}/{total}] Copied and formatted: {img_file}")

        print(f"Finished copying {total} files for {split} set.")

    def generate_yaml(self):
        yaml_path = os.path.join(self.output_dir, 'data.yaml')
        yaml_content = {
            'path': '.',
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'names': {
                0: "Larvae"
            }
        }
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, sort_keys=False)
        print(f"data.yaml created at: {yaml_path}")

if __name__ == "__main__":
    formatter = YoloDataFormatter(
        images_dir="/path/to/your/images",
        labels_dir="/path/to/your/labels",
        output_dir="/path/to/output/folder",
        train_pct=0.8,
        val_pct=0.1,
        test_pct=0.1
    )
    formatter()
