from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit

class REIDFormatterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("REID Formatter")
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setPlainText(
            "Feature coming soon.\n\nPlease use the reid_market_data_creator.py script to format your REID dataset for now."
        )
        layout.addWidget(self.text_box)
