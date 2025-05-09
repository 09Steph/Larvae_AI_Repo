import os
import cv2
import numpy as np

# Class to crop images in a circular area
# Workflow:
# 1. Initialize the class with input folder, output folder, center coordinates, and radius.
# 2. Create the output folder if it doesn't exist.
# 3. Method to stop processing.
# 4. Method to crop the image using a circular mask.
# 5. Method to process the images, crop them, and save them to the output folder.
# 6. If no images are found, print a message and return.


class PetriDishCropperCircle:
    def __init__(self, input_folder, output_folder, centerX, centerY, radius):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.center = (centerX, centerY)
        self.radius = radius
        self.should_stop = False
        os.makedirs(self.output_folder, exist_ok=True)

    def crop_image(self, image):
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, self.center, self.radius, 255, thickness=-1)
        return cv2.bitwise_and(image, image, mask=mask)

    def stop(self):
        self.should_stop = True

    def execute(self, extensions=(".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        files = [f for f in os.listdir(self.input_folder) if f.lower().endswith(extensions)]
        if not files:
            print("No images found in", self.input_folder)
            return

        total = len(files)
        for idx, filename in enumerate(files, 1):
            if self.should_stop:
                print(f"Stopping cropping at {idx}/{total} files")
                break

            filepath = os.path.join(self.input_folder, filename)
            image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
            if image is None:
                print("Error reading", filepath)
                continue

            try:
                processed = self.crop_image(image)
                output_path = os.path.join(self.output_folder, filename)
                cv2.imwrite(output_path, processed)
                print(f"[{idx}/{total}] Cropped and saved: {output_path}")
            except Exception as e:
                print(f"Skipping {filename} due to error: {e}")

    def __call__(self, extensions=(".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        self.execute(extensions)
