import pigpio
import time
import threading

# Class to control PWM for IR and Optogenetic LEDs using pigpio library.
# Workflow:
# 0. Initialize the pigpio library for hardware PWM control.
# 1. Initialize the class with the configuration data.
# 2. Set up GPIO pins for IR and optogenetic LEDs.
# 3. Control the IR LED using PWM with specified duty cycle and frequency.
# 4. Control the optogenetic LED using PWM with specified duty cycle and frequency.
# 5. Provide getter methods to access the timing and configuration values.
# 6. Provide methods to start and stop the PWM control for both LEDs.
# 7. Use threading events to synchronize the start of PWM control.
# 8. Provide methods to get the timing values for both LEDs.
# 9. Provide methods to get the configuration values for both LEDs.
# 10. Cleanup GPIO and pigpio resources after execution.

class PWMControl:
    def __init__(self, data):
      
        # IR LED configuration.
        self.__ir_led_duty = data.get("IR_LEDs", {}).get("duty_cycle", 0)
        self.__ir_led_frequency = data.get("IR_LEDs", {}).get("frequency", 0)
        self.__ir_led_active_time = data.get("IR_LEDs", {}).get("active_time", 0)
        
        # Optogenetic LED configuration.
        self.__opto_led_duty = data.get("Optogenetic_LEDs", {}).get("duty_cycle", 0)
        self.__opto_led_flash_length = data.get("Optogenetic_LEDs", {}).get("flash_length", 0)
        self.__opto_led_frequency = data.get("Optogenetic_LEDs", {}).get("frequency", 0)
        self.__opto_led_initial_delay = data.get("Optogenetic_LEDs", {}).get("initial_delay", 0)
        
        # Hardware PWM pins.
        self.ir_led_pin = 12      # PWM0 Channel
        self.opto_led_pin = 19    # PWM1 Channel
        
        # Timing variables.
        self.ir_led_on_time = None
        self.ir_led_off_time = None
        self.opto_led_on_time = None
        self.opto_led_off_time = None
        
        # Event for synchronized start.
        self.start_event = threading.Event()
        
        # Initialize pigpio.
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Could not connect to pigpio daemon. Run 'sudo pigpiod'.")

    # Convert duty cycle (percentage) to pigpio's range (0-255)
    def control_ir_led(self):
        self.start_event.wait()
        self.pi.set_PWM_frequency(self.ir_led_pin, self.__ir_led_frequency)
        duty = int((self.__ir_led_duty / 100.0) * 255)
        self.pi.set_PWM_dutycycle(self.ir_led_pin, duty)
        self.ir_led_on_time = time.time()
        print("IR LED (GPIO 12) PWM started at", self.ir_led_on_time)
        time.sleep(self.__ir_led_active_time)
        self.pi.set_PWM_dutycycle(self.ir_led_pin, 0)
        self.ir_led_off_time = time.time()
        print("IR LED PWM stopped at", self.ir_led_off_time)

    def control_opto_led(self):
        self.start_event.wait()
        self.pi.set_PWM_frequency(self.opto_led_pin, self.__opto_led_frequency)
        self.pi.set_PWM_dutycycle(self.opto_led_pin, 0)
        print("Optogenetic LED (GPIO 13) PWM started at 0% duty cycle")
        time.sleep(self.__opto_led_initial_delay)
        self.opto_led_on_time = time.time()
        print("Optogenetic LED turning ON at", self.opto_led_on_time)
        duty = int((self.__opto_led_duty / 100.0) * 255)
        self.pi.set_PWM_dutycycle(self.opto_led_pin, duty)
        time.sleep(self.__opto_led_flash_length)
        self.opto_led_off_time = time.time()
        print("Optogenetic LED turning OFF at", self.opto_led_off_time)
        self.pi.set_PWM_dutycycle(self.opto_led_pin, 0)

    def cleanup(self):
        self.pi.set_PWM_dutycycle(self.ir_led_pin, 0)
        self.pi.set_PWM_dutycycle(self.opto_led_pin, 0)
        self.pi.stop()

    # Getter methods for IR LED timing.
    def get_ir_led_on_time(self):
        return self.ir_led_on_time

    def get_ir_led_off_time(self):
        return self.ir_led_off_time

    # Getter methods for Optogenetic LED timing.
    def get_opto_led_on_time(self):
        return self.opto_led_on_time

    def get_opto_led_off_time(self):
        return self.opto_led_off_time

    # Getter methods for configuration.
    def get_ir_led_duty(self):
        return self.__ir_led_duty

    def get_ir_led_frequency(self):
        return self.__ir_led_frequency

    def get_ir_led_active_time(self):
        return self.__ir_led_active_time

    def get_opto_led_duty(self):
        return self.__opto_led_duty

    def get_opto_led_flash_length(self):
        return self.__opto_led_flash_length

    def get_opto_led_frequency(self):
        return self.__opto_led_frequency

    def get_opto_led_initial_delay(self):
        return self.__opto_led_initial_delay

