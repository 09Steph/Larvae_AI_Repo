import os
import json
from PySide6.QtWidgets import QMessageBox

# Controller used to control the RPI camera settings window.
# Workflow:
# 1. Wait for the user to confirm the camera settings.
# 2. Read the user inputs from the camera settings window.
# 3. Validate the user inputs and set default values if necessary.
# 4. Write the camera settings to a JSON file.
# 5. Close the camera settings window.

class RPICameraController:
    def __init__(self, camera_window):
        self.camera_window = camera_window
        self.setup_connections()

    def setup_connections(self):
        self.camera_window.btn_confirm.clicked.connect(self.confirm_settings)
        self.camera_window.btn_cancel.clicked.connect(self.camera_window.close)

    def confirm_settings(self):
        # Default values for HQ Camera
        default_mode = "4056:3040:12:U"
        default_capture_length = 35000
        default_framerate = 10
        default_gain = 1.0

        # Read and clean user inputs
        mode = self.camera_window.le_mode.text().strip() or default_mode
        capture_length_input = self.camera_window.le_capture_length.text().strip()
        framerate_input = self.camera_window.le_framerate.text().strip()
        gain_input = self.camera_window.le_gain.text().strip()
        shutter_speed_input = self.camera_window.le_shutter_speed.text().strip()

        try:
            capture_length = int(capture_length_input)
        except ValueError:
            capture_length = default_capture_length

        try:
            framerate = int(framerate_input)
        except ValueError:
            framerate = default_framerate

        try:
            gain = float(gain_input)
        except ValueError:
            gain = default_gain
        try:
            shutter_speed = int(shutter_speed_input)
        except (ValueError, TypeError):
            shutter_speed = None


        # Build settings dictionary.
        settings = {
            "mode": mode,
            "capture_length": capture_length,
            "framerate": framerate,
            "gain": gain,
            "shutter_speed": shutter_speed
        }

        # Write settings to Camera settings JSON file.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(base_dir, "..", "resources", "config_cam.json")
        try:
            with open(config_file_path, 'w') as f:
                json.dump(settings, f, indent=2)
            QMessageBox.information(
                self.camera_window,
                "Settings Saved",
                f"Camera settings saved:\n"
                f"Mode: {mode}\n"
                f"Capture Length: {capture_length}\n"
                f"Framerate: {framerate}\n"
                f"Gain: {gain}\n"
                f"Shutter Speed: {shutter_speed}"
            )
        except Exception as e:
            QMessageBox.critical(self.camera_window, "Save Error", f"Error saving settings: {e}")
        self.camera_window.close()
