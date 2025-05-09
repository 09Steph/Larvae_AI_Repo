import os
import time
import threading
import RPi.GPIO as GPIO
from settingsClass import ReceiverSettings
from pwmcontrolClassOld import PWMControl
from uartReceiver import UARTReceiver

# Main.py script to receive configuration data from the UART interface and control the PWM for IR and optogenetic LEDs.
# Workflow:
# 0. Initialization of the UART receiver and UART port
# 1. Wait for configuration data from the UART interface.
# 2. Write the received configuration data to a JSON file.
# 3. Continuously read incoming data from the UART interface, i.e data from the transmitter.
# 3. Wait for a trigger signal from the UART interface
# 4. Upon receiving the trigger signal, start the PWM control for the IR LED and optogenetic LED.
# 5. Threads are used to control the IR and optogenetic LEDs simultaneously.
# 6. The PWM control class will read the configuration data from the JSON file and control the LEDs accordingly.
# 7. Cleanup GPIO and UART resources after execution.
# 8. Restart the main loop to wait for new configuration data.
# Note: This script is designed to run continuously upon bootup of the Raspberry Pi.
# This uses contrab-e to run the script at startup (acting as a puesdo microntroller).

def main():
    # Set correct path for the configuration file
    config_file = "/home/steph/Desktop/Receiver/config.json"
    
    if os.path.exists(config_file):
        os.remove(config_file)
        print("Existing configuration file removed. Waiting for new configuration data.")
    
    uart_receiver = UARTReceiver(port='/dev/serial0', baudrate=115200, timeout=1)
    
    print("Waiting for configuration data from UART...")
    while not os.path.exists(config_file):
        uart_receiver.update_config()
        time.sleep(1)
    
    print("Configuration data received.")
    time.sleep(4)
    
    print("Waiting for trigger signal...")
    trigger = uart_receiver.wait_for_trigger()
    if trigger == 1:
        trigger_time = time.time()
        print("Trigger detected at:", trigger_time)
    else:
        print("Trigger not detected. Aborting capture.")
        return

    print("PWM LED Control Starting...")
    
    # Load configuration from the JSON file.
    settings = ReceiverSettings(config_file)
    config_data = settings.get_all_settings()
    
    pwm_control = PWMControl(config_data)
    
    print("\nPWMControl Configuration Values:")
    print("  IR LED Duty Cycle:", pwm_control.get_ir_led_duty())
    print("  IR LED Frequency:", pwm_control.get_ir_led_frequency())
    print("  IR LED Active Time:", pwm_control.get_ir_led_active_time())
    print("  Optogenetic LED Duty Cycle:", pwm_control.get_opto_led_duty())
    print("  Optogenetic LED Flash Length:", pwm_control.get_opto_led_flash_length())
    print("  Optogenetic LED Frequency:", pwm_control.get_opto_led_frequency())
    print("  Optogenetic LED Initial Delay:", pwm_control.get_opto_led_initial_delay())
    
    # Start LED control threads.
    thread_ir = threading.Thread(target=pwm_control.control_ir_led)
    thread_opto = threading.Thread(target=pwm_control.control_opto_led)
    thread_ir.start()
    thread_opto.start()
    time.sleep(0.1)
    pwm_control.start_event.set()
    thread_ir.join()
    thread_opto.join()
    
    led_off_time = time.time()
    total_elapsed = led_off_time - trigger_time
    print("\nOverall LED execution finished at:", led_off_time)
    print("Total elapsed time from trigger to LED off:", total_elapsed, "seconds")
    
    uart_receiver.ser.close()
    #pwm_control.cleanup() - For hardware PWM GPIO
    GPIO.cleanup()
    print("\nLED Control and Capture complete - Cleaning up and restarting\n")
    time.sleep(2)

if __name__ == '__main__':
    while True:
        main()
