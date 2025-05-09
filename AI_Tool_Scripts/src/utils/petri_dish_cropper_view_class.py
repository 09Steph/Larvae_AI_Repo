import os
import cv2
import numpy as np

# Class to veiw cropped images in a circular area 
# Workflow:
# 1. Initialize the class with input folder, center coordinates, and radius.
# 2. Finds the first image in the input folder.
# 3. Create a circular mask based on the center and radius.
# 4. Crop the image using the mask.
# 5. Display the cropped image in a window.
# 6. If no images are found, print a message and return.

class PetriDishCropperView:
    def __init__(self, input_folder, centerX, centerY, radius):
        self.input_folder = input_folder
        self.center = (int(centerX), int(centerY))
        self.radius = int(radius)

    def crop_image(self, image):
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, self.center, self.radius, 255, thickness=-1)
        return cv2.bitwise_and(image, image, mask=mask)

    def view(self, extensions=(".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        files = sorted(f for f in os.listdir(self.input_folder)
                       if f.lower().endswith(extensions))
        if not files:
            print("No images found in", self.input_folder)
            return

        first = files[0]
        path = os.path.join(self.input_folder, first)
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print("Error reading", path)
            return

        cropped = self.crop_image(img)

        window_name = "Cropped Image Example"
        cv2.imshow(window_name, cropped)
        cv2.waitKey(0)
        cv2.destroyWindow(window_name)

    def __call__(self, extensions=(".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        self.view(extensions)
