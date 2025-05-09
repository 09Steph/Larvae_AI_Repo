import os
import cv2
import numpy as np
import shutil

# Class to convert 16-bit images to 8-bit images
# Workflow:
# 1. Read the image file
# 2. Check the bit depth of the image
# 3. If the image is 16-bit, convert it to 8-bit
# 4. Save the converted image to the output folder
# 5. If the image is already 8-bit copy it to the output folder

class BitDepthConverter:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.should_stop = False
        os.makedirs(self.output_folder, exist_ok=True)

    def stop(self):
        self.should_stop = True

    def check_bit_depth(self, image):
        if image is None:
            return None
        if image.dtype == np.uint16:
            return 16
        elif image.dtype == np.uint8:
            return 8
        return None

    def convert_16bit_to_8bit(self, image):
        min_val = np.min(image)
        max_val = np.max(image)
        return ((image - min_val) / (max_val - min_val) * 255.0).astype(np.uint8)

    def __call__(self, extensions=(".tif", ".tiff", ".png", ".jpg", ".jpeg")):
        files = [f for f in os.listdir(self.input_folder)
                 if not f.startswith(".") and f.lower().endswith(extensions)]

        total_files = len(files)
        if total_files == 0:
            print("No image files found in:", self.input_folder)
            return

        input_equals_output = os.path.abspath(self.input_folder) == os.path.abspath(self.output_folder)

        for idx, file in enumerate(files, 1):
            if self.should_stop:
                print(f"Stopping BitDepthConverter early at [{idx}/{total_files}]")
                return

            input_path = os.path.join(self.input_folder, file)
            output_path = os.path.join(self.output_folder, file)

            image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
            bit_depth = self.check_bit_depth(image)

            if bit_depth == 16:
                image = self.convert_16bit_to_8bit(image)
                cv2.imwrite(output_path, image)
                print(f"[{idx}/{total_files}] Converted 16-bit to 8-bit: {file}")

            elif bit_depth == 8:
                if not input_equals_output:
                    shutil.copy2(input_path, output_path)
                    print(f"[{idx}/{total_files}] Copied (already 8-bit): {file}")
                else:
                    print(f"[{idx}/{total_files}] Skipped copy (already 8-bit and/or same folder): {file}")

            else:
                print(f"[{idx}/{total_files}] Skipped (unsupported or unreadable): {file}")
