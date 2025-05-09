import serial
import json
import time
import RPi.GPIO as GPIO

# UART Receiver Class used to receive configuration data from the UART interface and pass this data to the PWM control class.
# Workflow:
# 0. Initialization of the UART receiver and UART port
# 1. Wait for configuration data from the UART interface.
# 2. Write the received configuration data to a JSON file.
# 3. Continuously read incoming data from the UART interface, i.e data from the transmitter.
# 3. Wait for a trigger signal from the UART interface
# 4. Upon receiving the trigger signal, start the PWM control for the IR LED and optogenetic LED.
# 5. The PWM control class will read the configuration data from the JSON file and control the LEDs accordingly.

# Set correct path for the configuration file
OUTPUT_FILE = "/home/steph/Desktop/Receiver/config.json"
IDLE_TIMEOUT = 1.0  # Time to wait for new incoming data
READ_TIMEOUT = 3  # For update_config()

class UARTReceiver:
    def __init__(self, port='/dev/serial0', baudrate=115200, timeout=1):
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            print(f"Opened {port} at {baudrate} baud.")
        except Exception as e:
            print("Error opening serial port:", e)
            raise e
        time.sleep(2)
        self.__trigger = 0

    def read_payload(self):
        payload = b""
        last_time = time.time()
        while True:
            if self.ser.in_waiting > 0:
                chunk = self.ser.read(self.ser.in_waiting)
                payload += chunk
                last_time = time.time()
            else:
                if (time.time() - last_time) > IDLE_TIMEOUT:
                    break
            time.sleep(0.01)
        return payload

    def write_json(self, data):
        try:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print("JSON configuration updated:", data)
        except Exception as e:
            print("Error writing JSON file:", e)

    def update_config(self):
        total_payload = b""
        while True:
            if self.ser.in_waiting > 0:
                total_payload += self.read_payload()
                try:
                    payload_str = total_payload.decode('utf-8').strip()
                except Exception as e:
                    print("Error decoding payload:", e)
                    payload_str = ""
                print("Accumulated payload:", payload_str)
                # Prepend "{" if missing
                # Workaround and sometimes the { at the start is mising when data is sent over through UART
                if not payload_str.startswith("{"):
                    print("Payload missing initial '{', prepending it.")
                    payload_str = "{" + payload_str
                # If payload appears complete, parse it.
                if payload_str.endswith("}"):
                    try:
                        data = json.loads(payload_str)
                        self.write_json(data)
                        return
                    except Exception as e:
                        print("JSON parse error, waiting for more data:", e)
            else:
                time.sleep(0.1)

    def wait_for_trigger(self):
        print("Waiting for trigger")
        while True:
            if self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)
                try:
                    decoded = data.decode('utf-8').strip()
                except Exception as e:
                    decoded = ""
                print("Received trigger data:", decoded)
                if decoded == "1":
                    self.__trigger = 1
                    return 1
            time.sleep(0.1)

    def run(self):
        print("Receiver running: Waiting for data and trigger")
        try:
            self.update_config()
            self.ser.reset_input_buffer()
            trigger = self.wait_for_trigger()
            if trigger == 1:
                print("Triggered")
        except KeyboardInterrupt:
            print("Receiver stopping")
        finally:
            self.ser.close()
            GPIO.cleanup()

if __name__ == "__main__":
    receiver = UARTReceiver(port='/dev/serial0', baudrate=115200, timeout=1)
    receiver.run()
