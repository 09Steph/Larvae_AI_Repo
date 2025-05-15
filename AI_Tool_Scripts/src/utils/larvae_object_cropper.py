import os
import cv2
import glob
from collections import defaultdict

# Class to crop larvae objects from images based on annotations from a text file (YOLO format + Object ID from Boxmot Output)
# Workflow:
# 1. Initialize the class with input folder, image folder, and output folder paths.
# 2. Create the output folder if it doesn't exist.
# 3. Method to stop processing.
# 4. Method to find matching images based on the base name of the text file.
# 5. Method to crop the larvae objects from the images based on the annotations.
# 6. Save the cropped images in a structured folder format based on object IDs.

class LarvaeObjectCropper:
    def __init__(self, input_folder: str, image_folder: str, output_folder: str):
        self.input_folder = input_folder
        self.image_folder = image_folder
        self.output_folder = output_folder
        self.croppped_object_counter = defaultdict(int)
        self.unique_ids = set()
        self.output_txt_lines = []
        self.should_stop = False 

        os.makedirs(self.output_folder, exist_ok=True)

    def stop(self):
        self.should_stop = True

    def run(self):
        txt_files = sorted(glob.glob(os.path.join(self.input_folder, "*.txt")))
        total_files = len(txt_files)

        for idx, txt_file in enumerate(txt_files, 1):
            if self.should_stop:
                print(f"Stopping cropping at {idx}/{total_files} frames")
                break

            base_name = os.path.splitext(os.path.basename(txt_file))[0]
            print(f"[{idx}/{total_files}] Processing {base_name}.txt...")

            image_path = self.find_matching_image_by_name(base_name)
            if not image_path:
                print(f"Image not found for: {base_name}")
                continue

            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not read image: {image_path}")
                continue

            h, w = image.shape[:2]

            with open(txt_file, "r") as f:
                lines = f.readlines()

            for line in lines:
                cls_id, x, y, bw, bh, obj_id = line.strip().split()
                x, y, bw, bh, obj_id = float(x), float(y), float(bw), float(bh), int(obj_id)

                x1 = int((x - bw / 2) * w)
                y1 = int((y - bh / 2) * h)
                x2 = int((x + bw / 2) * w)
                y2 = int((y + bh / 2) * h)

                crop = image[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
                if crop.size == 0:
                    continue

                obj_folder = os.path.join(self.output_folder, f"larvae_{obj_id}")
                os.makedirs(obj_folder, exist_ok=True)

                crop_filename = f"{obj_id}_{base_name}.png"
                crop_path = os.path.join(obj_folder, crop_filename)
                cv2.imwrite(crop_path, crop)

                self.croppped_object_counter[obj_id] += 1
                self.unique_ids.add(obj_id)

                annotated_line = f"{cls_id} {x} {y} {bw} {bh} {obj_id} {base_name}"
                self.output_txt_lines.append(annotated_line)

            print(f"[{idx}/{total_files}] Finished processing {base_name}")

    def find_matching_image_by_name(self, base_name: str) -> str:
        extensions = ['.png', '.jpg', '.jpeg']
        for ext in extensions:
            image_path = os.path.join(self.image_folder, base_name + ext)
            if os.path.exists(image_path):
                return image_path
        return None
