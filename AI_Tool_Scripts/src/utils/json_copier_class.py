import os
import shutil

# Helper class to copy JSON files from one folder to another
# Workflow:
# 1. Initialize the class with source and destination folder paths.
# 2. Create the destination folder if it doesn't exist.
# 3. Define a method to stop processing.
# 4. Method to copy JSON files from the source folder to the destination folder.
# 5. If the file already exists in the destination folder, skip copying.
# 6. If the source folder does not exist, print an error message.
# 7. If no JSON files are found, print a message and return.

class JsonCopier:
    def __init__(self, source_folder, destination_folder):
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.should_stop = False
        os.makedirs(self.destination_folder, exist_ok=True)

    def stop(self):
        self.should_stop = True

    def __call__(self):
        if not os.path.isdir(self.source_folder):
            print(f"Source folder {self.source_folder} does not exist.")
            return
        if not os.path.isdir(self.destination_folder):
            print(f"Destination folder {self.destination_folder} does not exist.")
            return

        json_files = [f for f in os.listdir(self.source_folder) if f.lower().endswith(".json")]

        if not json_files:
            print(f"No JSON files found in {self.source_folder}")
            return

        for idx, filename in enumerate(json_files, 1):
            if self.should_stop:
                print(f"Stopping JsonCopier early at file [{idx}/{len(json_files)}]")
                return

            src_path = os.path.join(self.source_folder, filename)
            dst_path = os.path.join(self.destination_folder, filename)

            try:
                shutil.copy2(src_path, dst_path)
                print(f"Copied config: {src_path} → {dst_path}")
            except Exception as e:
                print(f"Error copying {filename}: {e}")
