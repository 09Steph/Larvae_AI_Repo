import os
from collections import Counter

# Helper Class to clean up a folder by removing files that are significantly smaller or larger than the mode size.
# Workflow:
# 0. Assumption that some raw/image files are corrupted this happens typcially at teh start of end of libcamera-raw operation
# files sizes may differ and hence will cause cropping, noise, etc.
# 1. Initialize the class with the folder path, tolerance, and file extensions to consider.
# 2. Create the folder if it doesn't exist.
# 3. Methof to stop processing.
# 4. Helper function used to identify and ignore MAC OS hidden files
# 5. Method to collect file sizes and identify the mode size. 
# 6. Method to delete files that are significantly smaller or larger than the mode size.

class FolderCleaner:
    def __init__(self, folder, tolerance=1000000, extensions=(".png", ".jpg", ".jpeg", ".tif", ".tiff")):
        self.folder = folder
        self.tolerance = tolerance
        self.extensions = extensions
        self.should_stop = False

    def stop(self):
        self.should_stop = True 

    def execute(self):
        all_files = [f for f in os.listdir(self.folder) if f.lower().endswith(self.extensions)]
        if not all_files:
            print(f"No supported files in {self.folder}")
            return

        # Added to account/ignore for hidden files and Mac specific Hidden files
        files = [f for f in all_files if not (f.startswith(".") or f.startswith("._"))]
        if not files:
            print(f"No valid files left in {self.folder}")
            return

        file_sizes = {}
        sizes = []
        for filename in files:
            if self.should_stop:
                print("Stopping FolderCleaner early during file size collection.")
                return

            path = os.path.join(self.folder, filename)
            try:
                size = os.path.getsize(path)
                file_sizes[filename] = size
                sizes.append(size)
            except Exception as e:
                print(f"Could not get size for {filename}: {e}")

        if not sizes:
            print(f"No readable files in {self.folder}")
            return

        count = Counter(sizes)
        mode_size, _ = count.most_common(1)[0]
        lower_bound = mode_size - self.tolerance
        upper_bound = mode_size + self.tolerance

        print(f"\nFolder: {self.folder}")
        print(f"Mode size: {mode_size} bytes")
        print(f"Range: {lower_bound} to {upper_bound} bytes")

        deleted_files = []
        for filename, size in file_sizes.items():
            if self.should_stop:
                print("Stopping FolderCleaner early during deletion.")
                return

            if size < lower_bound or size > upper_bound:
                try:
                    os.remove(os.path.join(self.folder, filename))
                    deleted_files.append(filename)
                    print(f"Deleted {filename} ({size} bytes)")
                except Exception as e:
                    print(f"Could not delete {filename}: {e}")

        print(f"\nTotal deleted: {len(deleted_files)}")

    def __call__(self):
        self.execute()
