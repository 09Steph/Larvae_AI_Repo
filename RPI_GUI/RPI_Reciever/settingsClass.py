import os
import json

# Class to handle the receiver settings and reads the configuration from a JSON file and provides methods to access the settings.
# Workflow:
# 1. Initialize the class with the path to the JSON file.
# 2. Read the JSON file and load the configuration data.
# 3. Provide getter methods to access the settings for IR LEDs and Optogenetic LEDs.
# 4. If the JSON file is not found or contains errors, use default values.
# 5. Provide a method to get all settings as a dictionary.
# 6. Provide a method to get individual settings for IR LEDs and Optogenetic LEDs.
# 7. Provide a method to get all settings as a dictionary.

class ReceiverSettings:
    def __init__(self, json_path):
        self.__json_path = json_path
        self.__default_config = {
            "IR_LED": {
                "duty": 80,
                "frequency": 500,
                "active_time": 40
            },
            "Optogenetic_LEDs": {
                "duty": 100,
                "flash_length": 5,
                "frequency": 500,
                "initial_delay": 8
            }
        }
        # Load configuration into a private variable.
        self.__data = self.__read_json()

        # Store individual values in private variables.
        self.__ir_led_duty = self.__data.get("IR_LED", {}).get("duty", 0)
        self.__ir_led_frequency = self.__data.get("IR_LED", {}).get("frequency", 0)
        self.__ir_led_active_time = self.__data.get("IR_LED", {}).get("active_time", 0)

        self.__opto_led_duty = self.__data.get("Optogenetic_LEDs", {}).get("duty", 0)
        self.__opto_led_flash_length = self.__data.get("Optogenetic_LEDs", {}).get("flash_length", 0)
        self.__opto_led_frequency = self.__data.get("Optogenetic_LEDs", {}).get("frequency", 0)
        self.__opto_led_initial_delay = self.__data.get("Optogenetic_LEDs", {}).get("initial_delay", 0)

    def __read_json(self):
        if os.path.exists(self.__json_path):
            try:
                with open(self.__json_path, "r") as f:
                    data = json.load(f)
                return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading JSON file: {e}. Using default configs.")
                return self.__default_config.copy()
        else:
            print(f"File '{self.__json_path}' not found. Using default configs.")
            return self.__default_config.copy()

    # Getter methods for IR_LED settings.
    def get_ir_led_duty(self):
        return self.__ir_led_duty

    def get_ir_led_frequency(self):
        return self.__ir_led_frequency

    def get_ir_led_active_time(self):
        return self.__ir_led_active_time

    # Getter methods for Optogenetic_LEDs settings.
    def get_opto_led_duty(self):
        return self.__opto_led_duty

    def get_opto_led_flash_length(self):
        return self.__opto_led_flash_length

    def get_opto_led_frequency(self):
        return self.__opto_led_frequency

    def get_opto_led_initial_delay(self):
        return self.__opto_led_initial_delay

    def get_all_settings(self):
 
        return self.__data

# if __name__ == "__main__":
#     # Example usage:
#     settings = ReceiverSettings("config.json")
#     print("Current configuration:")
#     print(settings.get_all_settings())
#     print("IR LED Duty:", settings.get_ir_led_duty())
#     print("IR LED Frequency:", settings.get_ir_led_frequency())
#     print("IR LED Active Time:", settings.get_ir_led_active_time())
#     print("Optogenetic LED Duty:", settings.get_opto_led_duty())
#     print("Optogenetic LED Flash Length:", settings.get_opto_led_flash_length())
#     print("Optogenetic LED Frequency:", settings.get_opto_led_frequency())
#     print("Optogenetic LED Initial Delay:", settings.get_opto_led_initial_delay())
