import json
import os
from PySide6.QtWidgets import QMessageBox

# Controller for the PWM settings window.
# Workflow:
# 1. Wait for the user to confirm the PWM settings.
# 2. Read the user inputs from the PWM settings window.
# 3. Validate the user inputs and set default values if necessary.
# 4. Write the PWM settings to a JSON file.
# 5. Close the PWM settings window.
# Additional Utility function to convert user input to numeric value or return default.

def get_numeric_value(value, default):
    try:
        if not value:
            raise ValueError
        return float(value)
    except ValueError:
        return default

class RPIPWMController:
    def __init__(self, pwm_window):
        self.pwm_window = pwm_window
        self.setup_connections()

    def setup_connections(self):
        self.pwm_window.btn_confirm.clicked.connect(self.confirm_settings)
        self.pwm_window.btn_cancel.clicked.connect(self.pwm_window.close)

    def confirm_settings(self):
        # Define default values
        default_ir_duty = 60
        default_ir_freq = 500
        default_ir_active = 40
        default_opto_duty = 100
        default_opto_freq = 500
        default_opto_flash = 5
        default_opto_delay = 8

        # Gather and convert inputs, or use defaults if invalid/blank.
        ir_duty = get_numeric_value(self.pwm_window.le_ir_duty_cycle.text().strip(), default_ir_duty)
        ir_freq = get_numeric_value(self.pwm_window.le_ir_frequency.text().strip(), default_ir_freq)
        ir_active = get_numeric_value(self.pwm_window.le_ir_active_time.text().strip(), default_ir_active)
        opto_duty = get_numeric_value(self.pwm_window.le_opto_duty_cycle.text().strip(), default_opto_duty)
        opto_freq = get_numeric_value(self.pwm_window.le_opto_frequency.text().strip(), default_opto_freq)
        opto_flash = get_numeric_value(self.pwm_window.le_opto_flash_length.text().strip(), default_opto_flash)
        opto_delay = get_numeric_value(self.pwm_window.le_opto_initial_delay.text().strip(), default_opto_delay)

        config = {
            "IR_LEDs": {
                "duty_cycle": ir_duty,
                "frequency": ir_freq,
                "active_time": ir_active
            },
            "Optogenetic_LEDs": {
                "duty_cycle": opto_duty,
                "frequency": opto_freq,
                "flash_length": opto_flash,
                "initial_delay": opto_delay
            }
        }

        base_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.normpath(os.path.join(base_dir, "..", "resources"))
        config_file_path = os.path.join(resources_dir, "config.json")

        try:
            with open(config_file_path, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self.pwm_window, "Configuration Error", f"Error writing config file: {e}")
            return

        QMessageBox.information(self.pwm_window, "Settings Saved", "PWM settings have been saved.")
        self.pwm_window.close()
