import os

# Helper Class to remove hidden files from a specified folder
# Workflow:
# 1. Initialize the class with the folder path.
# 2. Create the folder if it doesn't exist.
# 3. Define a method to stop processing.
# 4. Method to remove hidden files from the folder.
# 5. If the file is a hidden image file, remove it.
# 6. If the file is not a hidden image file, skip it.
# 7. Print the total number of removed files.

# Note:
# Mac OS hidden files are typically prefixed with a dot this was added to account for users device specific issue

class RemoveHiddenFiles:
    def __init__(self, folder):
        self.folder = folder
        self.should_stop = False

    def stop(self):
        self.should_stop = True 

    def execute(self):
        if not os.path.isdir(self.folder):
            print(f"Invalid folder: {self.folder}")
            return

        removed = 0
        for name in os.listdir(self.folder):
            if self.should_stop:
                print("Stopping RemoveHiddenFiles early.")
                return

            if not name.startswith('.'):
                continue

            lower = name.lower()
            if not (
                lower.endswith('.png') or
                lower.endswith('.jpg') or
                lower.endswith('.jpeg') or
                lower.endswith('.tif') or
                lower.endswith('.tiff')
            ):
                continue

            path = os.path.join(self.folder, name)
            if os.path.isfile(path) or os.path.islink(path):
                try:
                    os.remove(path)
                    removed += 1
                    print(f"Removed hidden file: {path}")
                except Exception as e:
                    print(f"Could not remove {path}: {e}")

        print(f"\nHidden image cleanup complete. Total removed: {removed}")

    def __call__(self):
        self.execute()
