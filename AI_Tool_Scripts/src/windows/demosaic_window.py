from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QScrollArea, QWidget, QTextEdit, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

class DemosaicWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Larvae AI Tool - Demosaic Settings")
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
        self.btn_demosaic = QPushButton("Demosaic All")
        self.btn_cancel_process = QPushButton("Cancel Processing")
        self.btn_cancel_main = QPushButton("Cancel/Main Page")
        self.btn_cancel_process.setEnabled(False)

        bottom_layout.addWidget(self.btn_demosaic)
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

        # Left panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        # Top row
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        lbl_input = QLabel("Input:")
        btn_input = QPushButton("Input Folder")
        le_input = QLineEdit()
        le_input.setReadOnly(True)

        lbl_output = QLabel("Output:")
        btn_output = QPushButton("Output Folder")
        le_output = QLineEdit()
        le_output.setReadOnly(True)

        for w in [lbl_input, lbl_output]:
            w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for b in [btn_input, btn_output]:
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for le in [le_input, le_output]:
            le.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        top_row.addWidget(lbl_input)
        top_row.addWidget(btn_input)
        top_row.addWidget(le_input)
        top_row.addSpacing(20)
        top_row.addWidget(lbl_output)
        top_row.addWidget(btn_output)
        top_row.addWidget(le_output)

        # Second row
        second_row = QHBoxLayout()
        second_row.setSpacing(8)

        lbl_width = QLabel("Width:")
        le_width = QLineEdit()
        le_width.setPlaceholderText("Default: 4056")

        lbl_height = QLabel("Height:")
        le_height = QLineEdit()
        le_height.setPlaceholderText("Default: 3040")

        lbl_stride = QLabel("Stride:")
        le_stride = QLineEdit()
        le_stride.setPlaceholderText("Default: 8128")

        for w in [lbl_width, lbl_height, lbl_stride]:
            w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for le in [le_width, le_height, le_stride]:
            le.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        second_row.addWidget(lbl_width)
        second_row.addWidget(le_width)
        second_row.addWidget(lbl_height)
        second_row.addWidget(le_height)
        second_row.addWidget(lbl_stride)
        second_row.addWidget(le_stride)

        left_layout.addLayout(top_row)
        left_layout.addLayout(second_row)

        # Right panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        btn_demosaic = QPushButton("Demosaic")
        btn_remove = QPushButton("Remove")

        for btn in (btn_demosaic, btn_remove):
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumWidth(120)

        right_layout.addStretch(1)
        right_layout.addWidget(btn_demosaic)
        right_layout.addStretch(1)
        right_layout.addWidget(btn_remove)
        right_layout.addStretch(1)

        # Assemble row
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
            "le_width": le_width,
            "le_height": le_height,
            "le_stride": le_stride,
            "btn_demosaic": btn_demosaic,
            "btn_remove": btn_remove
        }

        self.row_widgets.append(row_dict)
        return row_dict

    def append_log(self, message):
        self.text_log.append(message)
