import os
import numpy as np
import cv2

# Class to convert raw files to 16-bit PNG images via demosaicing of raw Bayer data
# Workflow:
# 1. Read the raw file
# 2. Reshape the data to a 2D array with the specified/calulated stride
# 3. Extract the valid data
# 4. Demosaic the Bayer data to RGB using OpenCV - expects array 
# 5. Save the RGB image as a PNG file
# 6. Rename the output file to ensure consistency in naming pattern

class RawTo16:
    def __init__(self, input_folder, output_folder, width=4056, height=3040, stride_bytes=8128, dtype=np.uint16):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.width = width
        self.height = height
        self.stride_bytes = stride_bytes
        self.dtype = dtype
        self.should_stop = False
        os.makedirs(self.output_folder, exist_ok=True)

    def stop(self):
        self.should_stop = True

    def demosaic(self, file_path, output_path):
        with open(file_path, "rb") as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint16)

        expected_elements = (self.height * self.stride_bytes) // 2
        if raw_data.size != expected_elements:
            raise ValueError(
                f"Size mismatch: Expected {expected_elements} uint16 elements, but got {raw_data.size} elements."
            )

        raw_data_with_stride = raw_data.reshape((self.height, self.stride_bytes // 2))
        useful_width_pixels = self.width
        valid_data = raw_data_with_stride[:, :useful_width_pixels]
        bayer_array = np.ascontiguousarray(valid_data).copy()

        # Demosaic the Bayer image to RGB - Edge-Aware method chosen
        # Demosaic and colour converion function from OpenCV for the Bayer files BGGR to RGB
        # rgb_image = cv2.cvtColor(bayer_array, cv2.COLOR_BayerBGGR2RGB)
        # rgb_image = cv2.cvtColor(bayer_array, cv2.COLOR_BayerBGGR2RGB)
        # rgb_image = cv2.demosaicing(bayer_array, cv2.COLOR_BayerBGGR2RGB)

        rgb_image = cv2.demosaicing(bayer_array, cv2.COLOR_BayerBGGR2RGB_EA)
        cv2.imwrite(output_path, rgb_image)

    # Heplder Funtion used to rename the output file and ensures consistency filename pattern for rest of program
    # Assumption is made that the .raw files are named in a consistent pattern
    # e.g. "xxxframe00001.raw" or "xxxframe_00002.raw", etc.
    # The function will rename the file to "xxx_frame_00001.png" always to ensure consistency across the program
    # Also assumed max number of frames for a single sitting is 99999
    def insert_underscore(self, base_name):
        if "frame_" in base_name:
            return base_name
        elif "frame" in base_name:
            idx = base_name.index("frame") + len("frame")
            prefix = base_name[:idx]

            digits = ""
            for ch in base_name[idx:]:
                if ch.isdigit():
                    digits += ch
                else:
                    break
            if digits:
                digits = digits[:5]
                return prefix + "_" + digits
        return base_name

    def execute(self, extensions=(".raw",)):
        file_list = sorted([f for f in os.listdir(self.input_folder) if f.lower().endswith(extensions)])
        if not file_list:
            print(f"No raw files found in {self.input_folder}")
            return

        total = len(file_list)
        for idx, file_name in enumerate(file_list, 1):
            if self.should_stop:
                print(f"Stopping demosaicing at {idx}/{total} files")
                break

            input_path = os.path.join(self.input_folder, file_name)
            base_name = os.path.splitext(file_name)[0]
            new_base_name = self.insert_underscore(base_name)
            output_path = os.path.join(self.output_folder, new_base_name + ".png")

            try:
                self.demosaic(input_path, output_path)
                print(f"[{idx}/{total}] Saved: {output_path}")
            except Exception as e:
                print(f"[{idx}/{total}] Error processing {input_path}: {e}")

    def __call__(self, extensions=(".raw",)):
        self.execute(extensions)