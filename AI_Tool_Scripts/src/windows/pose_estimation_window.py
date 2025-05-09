from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit

class PoseEstimationWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pose Estimation")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setText("Pose Estimation inference can be ran through DLC GUI. Utilise this by pointing config.yaml to the DLC GUI. \n\n"
                             "Utilize the DLC_Trainer.py and DLC_Trainer.ipynb to also run inference on videos/frames Read README for further instructions\n")
        layout.addWidget(self.text_box)
        self.setLayout(layout)
