from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QApplication
)
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Larvae AI Tool - Main Menu")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Master Buttons 
        group_master = QGroupBox("Master Buttons")
        vbox_master = QVBoxLayout()
        self.btn_cropped = QPushButton("Cropped")
        vbox_master.addWidget(self.btn_cropped)
        group_master.setLayout(vbox_master)

        # Data Processor Tools 
        group_processing = QGroupBox("Data Processor Tools")  
        vbox_proc = QVBoxLayout()
        self.btn_demosaic = QPushButton("Demosaic")
        self.btn_crop = QPushButton("Cropper")
        self.btn_extra_processor = QPushButton("Extra Processor")  
        self.btn_video_encoder = QPushButton("Video Encoder")
        vbox_proc.addWidget(self.btn_demosaic)
        vbox_proc.addWidget(self.btn_crop)
        vbox_proc.addWidget(self.btn_extra_processor)  
        vbox_proc.addWidget(self.btn_video_encoder)
        group_processing.setLayout(vbox_proc)

        # AI Training Tools 
        group_ai_train = QGroupBox("AI Training Tools")
        vbox_ai = QVBoxLayout()
        self.btn_imageimg = QPushButton("ImageImg")
        self.btn_dlc = QPushButton("DLC")
        self.btn_yolo_format = QPushButton("Yolo Dataset Formatter")
        self.btn_reid_format = QPushButton("REID Dataset Formatter")
        vbox_ai.addWidget(self.btn_imageimg)
        vbox_ai.addWidget(self.btn_dlc)
        vbox_ai.addWidget(self.btn_yolo_format)
        vbox_ai.addWidget(self.btn_reid_format)
        group_ai_train.setLayout(vbox_ai)

        # AI Models Inference 
        group_models = QGroupBox("AI Models Inference")
        vbox_models = QVBoxLayout()
        self.btn_mot = QPushButton("M.O.T")
        self.btn_pose = QPushButton("Pose Estimation")
        vbox_models.addWidget(self.btn_mot)
        vbox_models.addWidget(self.btn_pose)
        group_models.setLayout(vbox_models)

        # Main Layout 
        main_layout.addWidget(group_master)
        main_layout.addWidget(group_processing)
        main_layout.addWidget(group_ai_train)
        main_layout.addWidget(group_models)

        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
