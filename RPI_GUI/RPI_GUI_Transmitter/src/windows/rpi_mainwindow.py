from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QPlainTextEdit
)
from PySide6.QtCore import Qt

class RPIMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPI Camera Interface – Main Menu")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Output folder with a Browse button
        top_layout = QHBoxLayout()
        self.lbl_output = QLabel("Output Folder:")
        self.le_output_path = QLineEdit()
        self.le_output_path.setPlaceholderText("Path")
        self.btn_browse_output = QPushButton("Browse")
        top_layout.addWidget(self.lbl_output)
        top_layout.addWidget(self.le_output_path)
        top_layout.addWidget(self.btn_browse_output)
        main_layout.addLayout(top_layout)

        # Buttons for Camera Check, PWM Control Settings, Capture Settings, and Capture
        middle_layout = QHBoxLayout()
        self.btn_camera_check = QPushButton("Camera Check")
        self.btn_pwm_settings = QPushButton("PWM Control Settings")
        self.btn_capture_settings = QPushButton("Capture Settings")
        self.btn_capture = QPushButton("Capture")
        middle_layout.addWidget(self.btn_camera_check)
        middle_layout.addWidget(self.btn_pwm_settings)
        middle_layout.addWidget(self.btn_capture_settings)
        middle_layout.addWidget(self.btn_capture)
        main_layout.addLayout(middle_layout)

        # Terminal output area
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("background-color: black; color: white;")
        self.terminal_output.setMinimumHeight(200)
        main_layout.addWidget(self.terminal_output)

        self.setLayout(main_layout)
