import serial
import json
import time

# Class to handle UART communication for transmitting JSON data
# Workflow of class:
# Initialize the class with the file path and serial port parameters
# Data is set in a JSON file througth the GUI
# Reads JSON File from input path
# Converts JSON to bytes payload
# Sends payload to UART port
# Waits for a specified delay
# Sends a trigger signal to the UART port
# Extra trigger signal function - A byte (b'1') is used to indicate the start of the experiment

class UARTTransmitter:
    def __init__(self, file_path, port='/dev/serial0', baudrate=115200, timeout=1, send_delay=1.0):
        self.file_path = file_path
        self.send_delay = send_delay
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        except Exception as e:
            print("Error opening serial port:", e)
            raise e
        time.sleep(2)
        self.data_payload = {}

    def read_config(self):
        try:
            with open(self.file_path, 'r') as f:
                self.data_payload = json.load(f)
            print("Configuration loaded from file:", self.data_payload)
        except Exception as e:
            print("Error reading JSON configuration:", e)
            self.data_payload = {}

    def update_config(self):
        self.read_config()

    def prepare_payload(self):
        self.payload_str = json.dumps(self.data_payload)
        self.payload_bytes = self.payload_str.encode('utf-8')

    def send_payload(self):
        self.update_config()
        self.prepare_payload()
        print("Transmitter: Payload to be sent:")
        print(self.payload_str)
        self.ser.write(self.payload_bytes)
        self.ser.flush()
        print("Transmitter: Payload sent.")
        time.sleep(self.send_delay)

    def trigger(self, data=b'1'):
        if self.ser and self.ser.is_open:
            self.ser.write(data)
            self.ser.flush()
            print("Sent trigger signal:", data)
        else:
            print("UART port is not open; cannot send trigger signal.")

    def close(self):
        self.ser.close()

# if __name__ == "__main__":
#     # Example usage:
#     file_path = ""  
#     transmitter = UARTTransmitter(file_path, port='/dev/serial0', baudrate=115200, timeout=1)
#     transmitter.send_payload()
#     transmitter.trigger()  # Sends trigger (b'1')
#     transmitter.close()
