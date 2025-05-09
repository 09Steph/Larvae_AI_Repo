from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QScrollArea, QWidget, QFrame, QSizePolicy, QFileDialog, QGroupBox
)
from PySide6.QtCore import Qt
import os

class CroppedMasterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Larvae AI Tool - Cropped Master Settings")
        self.row_widgets = []
        self.setup_ui()
        self.resize(1200, 800)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Log Display
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setFixedHeight(150)
        main_layout.addWidget(self.text_log)

        # Model Path Inputs
        shared_box = QGroupBox("Model Input Paths")
        shared_layout = QHBoxLayout()

        self.btn_yolo_browse = QPushButton("Yolo Model Path")
        self.btn_yolo_browse.setAutoDefault(False)
        self.btn_yolo_browse.setDefault(False)
        self.btn_yolo_browse.clicked.connect(self.select_yolo)

        self.le_yolo_model = QLineEdit()
        self.le_yolo_model.setPlaceholderText("Path to .pt")
        self.le_yolo_model.setReadOnly(True)

        self.btn_reid_browse = QPushButton("REID Model Path")
        self.btn_reid_browse.setAutoDefault(False)
        self.btn_reid_browse.setDefault(False)
        self.btn_reid_browse.clicked.connect(self.select_reid)

        self.le_reid_model = QLineEdit()
        self.le_reid_model.setPlaceholderText("Path to .pth")
        self.le_reid_model.setReadOnly(True)

        self.btn_dlc_browse = QPushButton("DLC Path")
        self.btn_dlc_browse.setAutoDefault(False)
        self.btn_dlc_browse.setDefault(False)
        self.btn_dlc_browse.clicked.connect(self.select_dlc)

        self.le_dlc_model = QLineEdit()
        self.le_dlc_model.setPlaceholderText("Path to config.yaml")
        self.le_dlc_model.setReadOnly(True)

        self.btn_reset_models = QPushButton("Reset")
        self.btn_reset_models.clicked.connect(self.reset_model_paths)

        shared_layout.addWidget(self.btn_yolo_browse)
        shared_layout.addWidget(self.le_yolo_model)
        shared_layout.addSpacing(10)
        shared_layout.addWidget(self.btn_reid_browse)
        shared_layout.addWidget(self.le_reid_model)
        shared_layout.addSpacing(10)
        shared_layout.addWidget(self.btn_dlc_browse)
        shared_layout.addWidget(self.le_dlc_model)
        shared_layout.addSpacing(10)
        shared_layout.addWidget(self.btn_reset_models)

        shared_box.setLayout(shared_layout)
        main_layout.addWidget(shared_box)

        # Scroll Area for Parameter Sets
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

        # Bottom Buttons 
        bottom_layout = QHBoxLayout()
        self.btn_process_all = QPushButton("Process All")
        self.btn_cancel_process = QPushButton("Cancel Processing")
        self.btn_cancel_main = QPushButton("Cancel/Main Page")
        self.btn_cancel_process.setEnabled(False)

        bottom_layout.addWidget(self.btn_process_all)
        bottom_layout.addWidget(self.btn_cancel_process)
        bottom_layout.addWidget(self.btn_cancel_main)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        self.add_input_row()

    def add_input_row(self):
        container = QWidget()
        container.setFixedHeight(150)

        main_row_layout = QHBoxLayout(container)
        main_row_layout.setContentsMargins(0, 0, 0, 0)
        main_row_layout.setSpacing(10)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        lbl_input = QLabel("Input:")
        btn_input = QPushButton("Input Folder")
        btn_input.setAutoDefault(False)
        btn_input.setDefault(False)
        le_input = QLineEdit()
        le_input.setReadOnly(True)

        lbl_output = QLabel("Output:")
        btn_output = QPushButton("Output Folder")
        btn_output.setAutoDefault(False)
        btn_output.setDefault(False)
        le_output = QLineEdit()
        le_output.setReadOnly(True)

        lbl_folder = QLabel("Folder Name:")
        le_name = QLineEdit()

        top_row.addWidget(lbl_input)
        top_row.addWidget(btn_input)
        top_row.addWidget(le_input)
        top_row.addSpacing(20)
        top_row.addWidget(lbl_output)
        top_row.addWidget(btn_output)
        top_row.addWidget(le_output)
        top_row.addSpacing(20)
        top_row.addWidget(lbl_folder)
        top_row.addWidget(le_name)

        left_layout.addLayout(top_row)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        btn_process = QPushButton("Process")
        btn_remove = QPushButton("Remove")

        right_layout.addStretch(1)
        right_layout.addWidget(btn_process)
        right_layout.addStretch(1)
        right_layout.addWidget(btn_remove)
        right_layout.addStretch(1)

        main_row_layout.addWidget(left_widget, 5)
        main_row_layout.addWidget(right_widget, 1)
        self.scroll_layout.addWidget(container)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: lightgray;")
        self.scroll_layout.addWidget(divider)

        row_dict = {
            "container": container,
            "divider": divider,
            "btn_input": btn_input,
            "btn_output": btn_output,
            "le_input": le_input,
            "le_output": le_output,
            "le_name": le_name,
            "btn_process": btn_process,
            "btn_remove": btn_remove
        }

        self.row_widgets.append(row_dict)
        return row_dict

    def select_yolo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select YOLO Model File", os.path.expanduser("~"))
        if path:
            self.le_yolo_model.setText(path)

    def select_reid(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select REID Model File", os.path.expanduser("~"))
        if path:
            self.le_reid_model.setText(path)

    def select_dlc(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select DLC Config File", os.path.expanduser("~"))
        if path:
            self.le_dlc_model.setText(path)

    def reset_model_paths(self):
        self.le_yolo_model.clear()
        self.le_yolo_model.setPlaceholderText("Path to .pt")
        self.le_reid_model.clear()
        self.le_reid_model.setPlaceholderText("Path to .pth")
        self.le_dlc_model.clear()
        self.le_dlc_model.setPlaceholderText("Path to config.yaml")

    def append_log(self, message):
        self.text_log.append(message)
