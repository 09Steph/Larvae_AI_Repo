from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit

class MotWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Larvae AI Tool - Multi-Object Tracker (MOT)")
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setText("Multi-Object Tracking (MOT) GUI feature coming soon\n"
                              "Utilize the Boxmot repo and fun mot_run.py on seperate env to to run inference. Read README for further instructions\n")
        layout.addWidget(self.text_log)
