from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout
)
from PySide6.QtCore import Qt

class RPICameraWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RPI Camera Interface – Camera Settings")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Camera Button settings
        form_layout = QFormLayout()

        self.le_mode = QLineEdit()
        self.le_mode.setPlaceholderText("Default: 4056:3040:12:U")
        form_layout.addRow("Mode:", self.le_mode)

        self.le_capture_length = QLineEdit()
        self.le_capture_length.setPlaceholderText("Default: 35000")
        form_layout.addRow("Capture Length:", self.le_capture_length)

        self.le_framerate = QLineEdit()
        self.le_framerate.setPlaceholderText("Default: 10")
        form_layout.addRow("Framerate:", self.le_framerate)

        self.le_gain = QLineEdit()
        self.le_gain.setPlaceholderText("Default: 1")
        form_layout.addRow("Gain:", self.le_gain)

        self.le_shutter_speed = QLineEdit()
        self.le_shutter_speed.setPlaceholderText("Default: None")
        form_layout.addRow("Shutter Speed:", self.le_shutter_speed)

        main_layout.addLayout(form_layout)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        self.btn_confirm = QPushButton("Confirm and Save")
        self.btn_cancel = QPushButton("Cancel/Main Page")
        bottom_layout.addWidget(self.btn_confirm)
        bottom_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

