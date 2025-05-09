import json
import os

# Class used to write timings to a JSON file in output directory of each experiment
# Helper class used to time acutually exectution of code i.e from button press to end of capture
# Stored as ./timings.json as well

class Timings:
    def __init__(self, output_dir, capture_time, experiment_name=None):
        if experiment_name is None:
            experiment_name = os.path.basename(output_dir.rstrip(os.sep))
        self.experiment_name = experiment_name
        self.output_dir = output_dir
        self.capture_time = capture_time

    def write(self):
        data = {
            "Experiment_name": self.experiment_name,
            "Camera": {"capture_time": self.capture_time}
        }
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        output_file_path = os.path.join(self.output_dir, "timings.json")
        with open(output_file_path, "w") as f:
            json.dump(data, f, indent=4)
        print("Timings successfully written to:", output_file_path)
