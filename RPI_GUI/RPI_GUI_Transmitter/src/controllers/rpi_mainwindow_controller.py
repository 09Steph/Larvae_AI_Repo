import os
import json
from PySide6.QtWidgets import QFileDialog, QMessageBox
from windows.rpi_mainwindow import RPIMainWindow
from windows.rpi_camera_window import RPICameraWindow
from windows.rpi_pwm_window import RPIPWMWindow
from controllers.rpi_camera_controller import RPICameraController
from controllers.rpi_pwm_controller import RPIPWMController
from utils.camera_check_class import CameraCheck
from utils.capture_class import LibCameraRawCapture
from utils.uart_transmitter import UARTTransmitter
import time
from utils.timings import Timings
from os.path import basename
import shutil

# Controller for the main window of the RPI application.
# Workflow:
# 0. Assumption is that user has seleceted camera settings and PMW settings from the other windows and are saved to .JSON files.
# 1. Wait for the user to select an output folder.
# 2. Capture button is pressed
# 3. Read the camera settings from the JSON file.
# 4. Read the PWM settings from the JSON file.
# 5. Initialize the camera and UART transmitter.
# 6. Send the payload to the UART receiver.
# 7. Trigger the camera capture.
# 8. Wait for the capture to complete.
# 9. Copy the configuration files to the output folder.
# 10. Write the timings to a file.
# 11. Close the UART transmitter.
# 12. Close the camera capture object.

class RPIMainController:
    def __init__(self, main_window: RPIMainWindow):
        self.main_window = main_window
        self.output_folder = None 
        self.camera_settings = None  
        self.setup_connections()

    def setup_connections(self):
        self.main_window.btn_browse_output.clicked.connect(self.browse_output_folder)
        self.main_window.btn_capture_settings.clicked.connect(self.open_camera_window)
        self.main_window.btn_pwm_settings.clicked.connect(self.open_pwm_window)
        self.main_window.btn_camera_check.clicked.connect(self.camera_check)
        self.main_window.btn_capture.clicked.connect(self.capture_images)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self.main_window, "Select Output Folder", os.path.expanduser("~")
        )
        if folder:
            self.output_folder = folder
            self.main_window.le_output_path.setText(folder)

    def open_camera_window(self):
        cam_win = RPICameraWindow()
        cam_ctrl = RPICameraController(cam_win)
        cam_win.exec()

    def camera_check(self):
        cc = CameraCheck()
        cc.run()

    def open_pwm_window(self):
        pwm_win = RPIPWMWindow()
        pwm_ctrl = RPIPWMController(pwm_win)
        pwm_win.exec()

    def capture_images(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.normpath(os.path.join(base_dir, "..", "resources"))
        config_cam_path = os.path.join(resources_dir, "config_cam.json")
        config_file_path_uart = os.path.join(resources_dir, "config.json")

        if os.path.exists(config_cam_path):
            try:
                with open(config_cam_path, 'r') as f:
                    self.camera_settings = json.load(f)
                self.main_window.terminal_output.appendPlainText(
                    "Camera settings loaded from file: " + str(self.camera_settings)
                )
            except Exception as e:
                self.main_window.terminal_output.appendPlainText(
                    "Error loading camera settings from file: " + str(e)
                )
                self.camera_settings = {
                    "mode": "4056:3040:12:U",
                    "capture_length": 35000,
                    "framerate": 10,
                    "gain": 1,
                    "shutter_speed": None
                }
        else:
            self.main_window.terminal_output.appendPlainText(
                "Camera settings file not found. Using default settings."
            )
            self.camera_settings = {
                "mode": "4056:3040:12:U",
                "capture_length": 35000,
                "framerate": 10,
                "gain": 1,
                "shutter_speed": None
            }
        
        if self.output_folder is None:
            QMessageBox.warning(self.main_window, "Output Folder Missing", 
                                "Output folder not selected! Capture aborted.")
            return

        self.main_window.terminal_output.appendPlainText("Starting capture with settings:")
        self.main_window.terminal_output.appendPlainText("Camera Settings: " + str(self.camera_settings))
        self.main_window.terminal_output.appendPlainText("Output Folder: " + str(self.output_folder))

        try:
            capture_obj = LibCameraRawCapture(
                mode=self.camera_settings["mode"],
                timeout=self.camera_settings["capture_length"],
                framerate=self.camera_settings["framerate"],
                shutter_speed=self.camera_settings["shutter_speed"],
                gain=self.camera_settings["gain"],
                output_dir=self.output_folder
            )
        except Exception as e:
            QMessageBox.critical(self.main_window, "Capture Initialization Error",
                                "Error initializing capture object: " + str(e))
            return

        try:
            transmitter = UARTTransmitter(
                file_path=config_file_path_uart,
                port='/dev/serial0', 
                baudrate=115200,
                timeout=1,
                send_delay=1.0
            )
        except Exception as e:
            QMessageBox.critical(self.main_window, "UART Initialization Error",
                                "Error initializing UART transmitter: " + str(e))
            return

        try:
            transmitter.send_payload()
            self.main_window.terminal_output.appendPlainText("UART payload sent.")
            time.sleep(5)
            transmitter.trigger(b'1')
            self.main_window.terminal_output.appendPlainText("Trigger signal sent.")
            start_capture = time.time()
            capture_obj.capture()
            end_capture = time.time()
            capture_duration = end_capture - start_capture
            self.main_window.terminal_output.appendPlainText(
                "Capture initiated successfully. Duration: {:.2f} seconds".format(capture_duration)
            )
        except Exception as e:
            QMessageBox.critical(self.main_window, "Capture Error",
                                "Error during capture: " + str(e))
        finally:
            transmitter.close()
            self.main_window.terminal_output.appendPlainText("Capture/Experiment complete and transmitter closed.")
            
            experiment_name = basename(self.output_folder.rstrip(os.sep))
            timings_obj = Timings(
                output_dir=self.output_folder,
                capture_time=capture_duration if 'capture_duration' in locals() else self.camera_settings["capture_length"],
                experiment_name=experiment_name
            )
            timings_obj.write()

            try:
                shutil.copy(config_file_path_uart, self.output_folder)
                shutil.copy(config_cam_path, self.output_folder)
                self.main_window.terminal_output.appendPlainText("Config files copied to output folder.")
            except Exception as e:
                QMessageBox.warning(self.main_window, "File Copy Warning",
                                    "Error copying config files: " + str(e))
