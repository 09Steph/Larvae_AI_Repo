from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QCheckBox, QScrollArea, QWidget, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

class ExtraProcessorWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Larvae AI Tool - Extra Processor")
        self.row_widgets = []
        self.resize(1200, 800)
        self.initial_text = (
            "Larvae AI Tool - Extra Processor\n"
            "Assumption: Raw input folder may contain original config.json files. "
            "Use the checkboxes below to choose whether to copy from Raw or from Input folder.\n"
        )
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Log output
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setFixedHeight(300)
        main_layout.addWidget(self.text_log)
        self.append_log(self.initial_text)

        # Parameter sets
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

        # Bottom controls
        bottom_layout = QHBoxLayout()
        self.btn_process_all = QPushButton("Process All")
        self.btn_cancel_process = QPushButton("Cancel Processing")
        self.btn_cancel_main = QPushButton("Cancel/Main Page")
        self.btn_cancel_process.setEnabled(False)
        bottom_layout.addWidget(self.btn_process_all)
        bottom_layout.addWidget(self.btn_cancel_process)
        bottom_layout.addWidget(self.btn_cancel_main)
        main_layout.addLayout(bottom_layout)

        # First parameter set row
        self.add_input_row()

        self.setLayout(main_layout)

    def add_input_row(self):
        container = QWidget()
        container.setFixedHeight(150)

        main_row_layout = QHBoxLayout(container)
        main_row_layout.setContentsMargins(0, 0, 0, 0)
        main_row_layout.setSpacing(5) 

        # Left panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        # Raw input folder
        lbl_input_raw = QLabel("Input Raw Folder:")
        btn_input_raw = QPushButton("Select Raw")
        le_input_raw = QLineEdit()
        le_input_raw.setReadOnly(True)

        # Regular input folder
        lbl_input = QLabel("Input Folder:")
        btn_input = QPushButton("Select Input")
        le_input = QLineEdit()
        le_input.setReadOnly(True)

        # Output folder
        lbl_output = QLabel("Output Folder:")
        btn_output = QPushButton("Select Output")
        le_output = QLineEdit()
        le_output.setReadOnly(True)

        # Assemble folder rows
        for lbl, btn, le in [
            (lbl_input_raw, btn_input_raw, le_input_raw),
            (lbl_input,      btn_input,      le_input),
            (lbl_output,     btn_output,     le_output),
        ]:
            row = QHBoxLayout()
            row.addWidget(lbl)
            row.addWidget(btn)
            row.addWidget(le)
            left_layout.addLayout(row)

        # Checkboxes
        chk_convert_8bit     = QCheckBox("Convert to 8-bit")
        chk_copy_raw_configs = QCheckBox("Copy Configs from Raw")
        chk_copy_inp_configs = QCheckBox("Copy Configs from Input")

        chk_convert_8bit.setChecked(False)
        chk_copy_raw_configs.setChecked(False)
        chk_copy_inp_configs.setChecked(False)
        chk_copy_raw_configs.setEnabled(False)
        chk_copy_inp_configs.setEnabled(False)

        cb_row = QHBoxLayout()
        cb_row.addWidget(chk_convert_8bit)
        cb_row.addWidget(chk_copy_raw_configs)
        cb_row.addWidget(chk_copy_inp_configs)
        left_layout.addLayout(cb_row)

        # Right panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)

        btn_process = QPushButton("Process")
        btn_remove  = QPushButton("Remove")
        for btn in (btn_process, btn_remove):
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumWidth(120)

        right_layout.addStretch(1)
        right_layout.addWidget(btn_process)
        right_layout.addStretch(1)
        right_layout.addWidget(btn_remove)
        right_layout.addStretch(1)

        # Combine left & right
        main_row_layout.addWidget(left_widget, 5)
        main_row_layout.addWidget(right_widget, 1)
        self.scroll_layout.addWidget(container)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("color: lightgray;")
        self.scroll_layout.addWidget(divider)

        row_dict = {
            "container": container,
            "divider": divider,
            "btn_input_raw": btn_input_raw,
            "le_input_raw": le_input_raw,
            "btn_input": btn_input,
            "le_input": le_input,
            "btn_output": btn_output,
            "le_output": le_output,
            "chk_convert_8bit":     chk_convert_8bit,
            "chk_copy_raw_configs": chk_copy_raw_configs,
            "chk_copy_inp_configs": chk_copy_inp_configs,
            "btn_process": btn_process,
            "btn_remove":  btn_remove,
        }
        self.row_widgets.append(row_dict)
        return row_dict

    def append_log(self, message):
        self.text_log.append(message)
