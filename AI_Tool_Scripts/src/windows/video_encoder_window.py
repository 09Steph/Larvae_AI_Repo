from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QScrollArea, QWidget, QFrame, QSizePolicy, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt

class VideoEncoderWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Encoder Tool")
        self.video_sets = []
        self.setup_ui()
        self.resize(1200, 800)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Log Output TextEdit
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setFixedHeight(150)
        main_layout.addWidget(self.text_log)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

        self.add_video_set_row()

        # Bottom control buttons
        bottom_layout = QHBoxLayout()
        self.btn_encode_all = QPushButton("Encode All")
        self.btn_cancel_process = QPushButton("Cancel Processing")
        self.btn_cancel_main = QPushButton("Cancel/Main Page")
        self.btn_cancel_process.setEnabled(False)

        bottom_layout.addWidget(self.btn_encode_all)
        bottom_layout.addWidget(self.btn_cancel_process)
        bottom_layout.addWidget(self.btn_cancel_main)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def add_video_set_row(self):
        container = QWidget()
        container.setFixedHeight(150)

        row_layout = QHBoxLayout(container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        # Left Panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        btn_input = QPushButton("Input Folder")
        le_input = QLineEdit(); le_input.setReadOnly(True)

        btn_output = QPushButton("Output Folder")
        le_output = QLineEdit(); le_output.setReadOnly(True)

        label_name = QLabel("Output File Name")
        le_name = QLineEdit()

        label_framerate = QLabel("Framerate (Default: 10)")
        le_framerate = QLineEdit()
        le_framerate.setPlaceholderText("Default: 10")

        cb_8bit = QCheckBox("8-bit")
        cb_16bit = QCheckBox("16-bit")

        for label, widget in [
            (btn_input, le_input),
            (btn_output, le_output),
            (label_name, le_name),
            (label_framerate, le_framerate),
        ]:
            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(widget)
            left_layout.addLayout(row)

        checkbox_row = QHBoxLayout()
        checkbox_row.addWidget(cb_8bit)
        checkbox_row.addWidget(cb_16bit)
        left_layout.addLayout(checkbox_row)

        # Right Panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)

        btn_encode = QPushButton("Encode")
        btn_remove = QPushButton("Remove")

        for btn in (btn_encode, btn_remove):
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        right_layout.addStretch(1)
        right_layout.addWidget(btn_encode)
        right_layout.addStretch(1)
        right_layout.addWidget(btn_remove)
        right_layout.addStretch(1)

        # Combine Left and Right
        row_layout.addWidget(left_widget, 5)
        row_layout.addWidget(right_widget, 1)

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
            "le_input": le_input,
            "btn_output": btn_output,
            "le_output": le_output,
            "le_name": le_name,
            "le_framerate": le_framerate,
            "cb_8bit": cb_8bit,
            "cb_16bit": cb_16bit,
            "btn_encode": btn_encode,
            "btn_remove": btn_remove
        }

        self.video_sets.append(row_dict)
        return row_dict

    def append_log(self, message):
        self.text_log.append(message)
