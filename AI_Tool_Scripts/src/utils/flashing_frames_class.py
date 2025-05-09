import os
import cv2
import numpy as np

# Functor Class to outline frames in a folder
# Workflow:
# 1. Initialize the class with input and output folder paths, frame indices, and colour and/or thickness of the outline
# 2. Create the output folder if it doesn't exist.
# 3. Define a method to stop processing.
# 4. Helper function used to identify and ignore MAC OS hidden files
# 6. Method to draw an outline around the image.
# 4. Define a method to generate image paths based on the specified pattern.
# 5. Call Method to process the images, draw outlines, and save them to the output folder.

class FlashingFrames:
    def __init__(self, input_folder, output_folder, frame_indices,
                 filename_pattern="frame_{:05d}",
                 outline_color=(0, 0, 255), 
                 outline_thickness=50):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.frame_indices = frame_indices
        self.pattern = filename_pattern
        self.should_stop = False
        os.makedirs(self.output_folder, exist_ok=True)

        self.outline_color = outline_color
        self.outline_thickness = outline_thickness

    def stop(self):
        self.should_stop = True

    def image_paths(self):
        self.frame_paths = []
        files = os.listdir(self.input_folder)
        for idx in self.frame_indices:
            try:
                suffix = self.pattern.format(int(idx))
            except ValueError:
                print(f"Invalid frame index for formatting: {idx}")
                continue

            matched = [f for f in files if f.endswith(suffix) or f.split('.')[0].endswith(suffix)]
            if not matched:
                print(f"No file ending with frame index '{suffix}'")
            for fname in matched:
                self.frame_paths.append((idx, os.path.join(self.input_folder, fname)))

    def __call__(self):
        self.image_paths()
        total = len(self.frame_paths)
        if total == 0:
            print("No frames to process.")
            return

        saved = 0
        for idx_count, (idx, in_path) in enumerate(self.frame_paths, 1):
            if self.should_stop:
                print(f"Stopping FlashingFrames early at [{idx_count}/{total}]")
                return

            img = cv2.imread(in_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                print(f"Failed to load image: {in_path}")
                continue

            outlined = self.draw_outline(img)
            out_name = os.path.basename(in_path)
            out_path = os.path.join(self.output_folder, out_name)
            if cv2.imwrite(out_path, outlined):
                saved += 1
                print(f"[{idx_count}/{total}] Saved outlined frame: {out_path}")
            else:
                print(f"[{idx_count}/{total}] Failed to save outlined image: {out_path}")

        print(f"Processed and saved {saved} outlined frames to '{self.output_folder}'.")

    def draw_outline(self, img):
        h, w = img.shape[:2]
        outlined = img.copy()
        cv2.rectangle(
            outlined,
            (0, 0),
            (w - 1, h - 1),
            self.outline_color, 
            thickness=self.outline_thickness
        )
        return outlined
