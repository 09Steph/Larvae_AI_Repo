import subprocess
import sys
import os
from PySide6.QtWidgets import QMessageBox

from windows.video_encoder_window import VideoEncoderWindow
from windows.cropper_window import CropperWindow
from windows.demosaic_window import DemosaicWindow
from windows.extra_processor_window import ExtraProcessorWindow
from windows.yolo_formatter_window import YOLOFormatterWindow
from windows.reid_formatter_window import REIDFormatterWindow
from windows.mot_window import MotWindow
from windows.pose_estimation_window import PoseEstimationWindow
from windows.cropped_master_window import CroppedMasterWindow

from controllers.video_encoder_controller import VideoEncoderController
from controllers.cropper_controller import CropperController
from controllers.demosaic_controller import DemosaicController
from controllers.extra_processor_controller import ExtraProcessorController
from controllers.yolo_formatter_controller import YOLOFormatterController
from controllers.reid_formatter_controller import REIDFormatterController
from controllers.mot_controller import MotController
from controllers.pose_estimation_controller import PoseEstimationController
from controllers.cropped_master_controller import CroppedMasterController

# Controller script used to control logic of main window buttons in UI
# Used to open different windows for different functionalities

class MainWindowController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.setup_connections()

    def setup_connections(self):
        self.main_window.btn_crop.clicked.connect(self.open_cropper_window)
        self.main_window.btn_video_encoder.clicked.connect(self.open_video_encoder_window)
        self.main_window.btn_imageimg.clicked.connect(self.open_imageimg_window)
        self.main_window.btn_dlc.clicked.connect(self.open_dlc_app)
        self.main_window.btn_demosaic.clicked.connect(self.open_demosaic_window)
        self.main_window.btn_extra_processor.clicked.connect(self.open_extra_processor_window)
        self.main_window.btn_yolo_format.clicked.connect(self.open_yolo_formatter_window)
        self.main_window.btn_reid_format.clicked.connect(self.open_reid_formatter_window)
        self.main_window.btn_mot.clicked.connect(self.open_mot_window)
        self.main_window.btn_pose.clicked.connect(self.open_pose_estimation_window)
        self.main_window.btn_cropped.clicked.connect(self.open_cropped_window)

    # Section: Image Processing
    def open_video_encoder_window(self):
        window = VideoEncoderWindow(self.main_window)
        controller = VideoEncoderController(window)
        window.exec()

    def open_cropper_window(self):
        window = CropperWindow(self.main_window)
        controller = CropperController(window)
        window.exec()

    def open_demosaic_window(self):
        window = DemosaicWindow(self.main_window)
        controller = DemosaicController(window)
        window.exec()

    def open_extra_processor_window(self):
        window = ExtraProcessorWindow(self.main_window)
        controller = ExtraProcessorController(window)
        window.exec()

    # Section: AI Training Tools
    def open_imageimg_window(self):
        try:
            subprocess.Popen(["labelimg"])
        except FileNotFoundError:
            QMessageBox.critical(
                self.main_window,
                "LabelImg Not Found",
                "LabelImg is not installed or not found in PATH. Please install it first."
            )

    def open_dlc_app(self):
        try:
            env = os.environ.copy()
            env["DLClight"] = "0"
            env["QT_API"] = "pyside6"

            subprocess.Popen([sys.executable, "-m", "deeplabcut"], env=env)
        except FileNotFoundError:
            QMessageBox.critical(
                self.main_window,
                "DeepLabCut Not Found",
                "DeepLabCut is not installed or not found in PATH. Please install it first."
            )

    def open_yolo_formatter_window(self):
         window = YOLOFormatterWindow(self.main_window)
         controller = YOLOFormatterController(window)
         window.exec()

    def open_reid_formatter_window(self):
         window = REIDFormatterWindow(self.main_window)
         controller = REIDFormatterController(window)
         window.exec()

    # Section: AI Inference
    def open_mot_window(self):
        window = MotWindow(self.main_window)
        controller = MotController(window)
        window.exec()

    def open_pose_estimation_window(self):
         window = PoseEstimationWindow(self.main_window)
         controller = PoseEstimationController(window)
         window.exec()

    # Section: Master Button
    def open_cropped_window(self):
        window = CroppedMasterWindow(self.main_window)
        controller = CroppedMasterController(window)
        window.exec()
