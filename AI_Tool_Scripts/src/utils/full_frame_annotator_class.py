import os
import shutil
import cv2

# Class to annotate images with bounding boxes based on annotations folder with files of matching names
# Workflow:
# 1. Initialize the class with input and output folder paths.
# 2. Create the output folder if it doesn't exist.
# 3. Define a method to stop processing.
# 4. Helper function used to identify and ignore MAC OS hidden files
# 5. Method to draw bounding boxes on the image based on the annotation file.
# 6. Define a method to process the images, draw boxes, and save them to the output folder.
# 7. If no annotation file is found, copy the image to the output folder without annotations.
# Ensures there are no missing images in the output folder.

class FullFrameAnnotator:
    def __init__(self, images_folder, annotations_folder, output_folder):
        self.images_folder = images_folder
        self.annotations_folder = annotations_folder
        self.output_folder = output_folder
        self.should_stop = False
        os.makedirs(self.output_folder, exist_ok=True)

    def draw_boxes(self, image_path, annotation_path):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            return

        h, w = image.shape[:2]
        with open(annotation_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 6:
                    continue
                _, x_c, y_c, bw, bh, obj_id = parts[:6]
                try:
                    x_c = float(x_c) * w
                    y_c = float(y_c) * h
                    bw = float(bw) * w
                    bh = float(bh) * h
                except ValueError:
                    continue

                x0 = int(round(x_c - bw / 2))
                y0 = int(round(y_c - bh / 2))
                x1 = int(round(x_c + bw / 2))
                y1 = int(round(y_c + bh / 2))

                # Blue bounding box and text color (BGR)
                cv2.rectangle(image, (x0, y0), (x1, y1), (255, 0, 0), 2)
                cv2.putText(
                    image,
                    f"ID:{obj_id}",
                    (x0, max(y0 - 5, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    1
                )

        out_path = os.path.join(self.output_folder, os.path.basename(image_path))
        cv2.imwrite(out_path, image)
        print(f"Labeled and saved: {out_path}")

    def __call__(self):
        image_files = sorted(os.listdir(self.images_folder))
        total = len(image_files)

        for idx, image_name in enumerate(image_files, 1):
            if self.should_stop:
                print(f"Stopped annotation at {idx}/{total} images")
                break

            image_path = os.path.join(self.images_folder, image_name)
            base, ext = os.path.splitext(image_name)
            annotation_path = os.path.join(self.annotations_folder, base + '.txt')

            if not os.path.isfile(image_path):
                continue

            if os.path.isfile(annotation_path):
                self.draw_boxes(image_path, annotation_path)
            else:
                shutil.copy(image_path, os.path.join(self.output_folder, image_name))
                print(f"No annotation for {image_name}; copied image only.")
