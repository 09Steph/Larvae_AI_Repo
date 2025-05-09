from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt

class RPIPWMWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RPI Camera Interface – PWM Settings")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Dark Field IR LEDs Settings
        gb_dark_field = QGroupBox("Dark Field IR LEDs Settings")
        dark_layout = QFormLayout()

        self.le_ir_duty_cycle = QLineEdit()
        self.le_ir_duty_cycle.setPlaceholderText("Default: 100")
        dark_layout.addRow("Duty Cycle:", self.le_ir_duty_cycle)

        self.le_ir_frequency = QLineEdit()
        self.le_ir_frequency.setPlaceholderText("Default: 500")
        dark_layout.addRow("Frequency:", self.le_ir_frequency)

        self.le_ir_active_time = QLineEdit()
        self.le_ir_active_time.setPlaceholderText("Default: 100")
        dark_layout.addRow("Active Time:", self.le_ir_active_time)

        gb_dark_field.setLayout(dark_layout)
        main_layout.addWidget(gb_dark_field)

        # Optogenetic LEDs Settings
        gb_opto = QGroupBox("Optogenetic LEDs Settings")
        opto_layout = QFormLayout()

        self.le_opto_duty_cycle = QLineEdit()
        self.le_opto_duty_cycle.setPlaceholderText("Default: 100")
        opto_layout.addRow("Duty Cycle:", self.le_opto_duty_cycle)

        self.le_opto_frequency = QLineEdit()
        self.le_opto_frequency.setPlaceholderText("Default: 100")
        opto_layout.addRow("Frequency:", self.le_opto_frequency)

        self.le_opto_flash_length = QLineEdit()
        self.le_opto_flash_length.setPlaceholderText("Default: 5")
        opto_layout.addRow("Flash Length:", self.le_opto_flash_length)

        self.le_opto_initial_delay = QLineEdit()
        self.le_opto_initial_delay.setPlaceholderText("Default: 8")
        opto_layout.addRow("Initial Delay:", self.le_opto_initial_delay)

        gb_opto.setLayout(opto_layout)
        main_layout.addWidget(gb_opto)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        self.btn_confirm = QPushButton("Confirm and Save")
        self.btn_cancel = QPushButton("Cancel/Main Page")

        bottom_layout.addWidget(self.btn_confirm)
        bottom_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
