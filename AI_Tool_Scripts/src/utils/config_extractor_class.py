import os
import json

# Class to extract configuration data from a folder containing image files and JSON config files.
# Workflow:
# 1. Load configuration data from JSON files in the specified folder.
# 2. Count the number of image frames in the folder.
# 3. Identify the frames that are flashing based on the configuration data.
# 4. Display the configuration data and the number of image frames.
# 5. Provide methods to retrieve the configuration data, number of frames, and flashing frames.

class ConfigExtractor:
    IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff")

    def __init__(self, folder_path):
        self._folder_path = folder_path
        self._config_data = {}
        self._num_frames = 0
        self._flashing_frames = []
        self.should_stop = False

    def stop(self):
        self.should_stop = True

    def load_configs(self):
        if self.should_stop:
            print("Stopping ConfigExtractor during load_configs()")
            return
        cfg1 = os.path.join(self._folder_path, "config.json")
        if os.path.isfile(cfg1):
            with open(cfg1, encoding="utf-8") as f:
                data = json.load(f)
            self._config_data["IR LEDs"] = data.get("IR_LEDs", {})
            self._config_data["Optogenetic LEDs"] = data.get("Optogenetic_LEDs", {})

        cfg2 = os.path.join(self._folder_path, "config_cam.json")
        if os.path.isfile(cfg2):
            with open(cfg2, encoding="utf-8") as f:
                data = json.load(f)
            self._config_data["Camera"] = {
                "mode":           data.get("mode"),
                "capture_length": data.get("capture_length"),
                "framerate":      data.get("framerate"),
                "gain":           data.get("gain"),
                "shutter_speed":  data.get("shutter_speed"),
            }

        cfg3 = os.path.join(self._folder_path, "timings.json")
        if os.path.isfile(cfg3):
            with open(cfg3, encoding="utf-8") as f:
                data = json.load(f)
            self._config_data["Experiment name"] = data.get("Experiment_name")
            self._config_data["Experiment/System Capture Time"] = data.get("Camera", {}).get("capture_time")

    def count_frames(self):
        cnt = 0
        files = os.listdir(self._folder_path)
        for name in files:
            if self.should_stop:
                print("Stopping ConfigExtractor during count_frames()")
                return
            if name.lower().endswith(self.IMAGE_EXTENSIONS):
                if os.path.isfile(os.path.join(self._folder_path, name)):
                    cnt += 1
        self._num_frames = cnt

    def flashing_frames(self):
        if self.should_stop:
            print("Stopping ConfigExtractor during flashing_frames()")
            return []
        opto = self._config_data.get("Optogenetic LEDs", {})
        cam = self._config_data.get("Camera", {})
        delay = opto.get("initial_delay", 0.0) or 0.0
        length = opto.get("flash_length", 0.0) or 0.0
        fps = cam.get("framerate", 1.0) or 1.0

        start_frame = int(delay * fps)
        frame_count = int(length * fps)
        end_frame = start_frame + frame_count - 1 if frame_count > 0 else start_frame

        self._flashing_frames = list(range(start_frame, end_frame + 1))
        print(f"\nFlash starts at frame {start_frame}, ends at frame {end_frame}")
        print(f"Flashing frames: {self._flashing_frames}")
        return self._flashing_frames

    def display_values(self):
        if self.should_stop:
            print("Stopping ConfigExtractor during display_values()")
            return
        print(f"\nFolder: {self._folder_path}")
        for section, content in self._config_data.items():
            print(f"\n{section}")
            print(json.dumps(content, indent=2, ensure_ascii=False))
        print(f"\nNumber of image frames: {self._num_frames}")

    def run(self):
        if not os.path.isdir(self._folder_path):
            print(f"Invalid folder: {self._folder_path}")
            return
        self.load_configs()
        if self.should_stop:
            return
        self.count_frames()
        if self.should_stop:
            return
        self.display_values()
        if self.should_stop:
            return
        self.flashing_frames()

    def get_config_data(self):
        return self._config_data

    def get_num_frames(self):
        return self._num_frames

    def get_flashing_frames(self):
        return self._flashing_frames
