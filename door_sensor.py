from machine import Pin, time_pulse_us
import time

# Setup Pins
TRIG_A = Pin(10, Pin.OUT)
ECHO_A = Pin(11, Pin.IN)
TRIG_B = Pin(8, Pin.OUT)
ECHO_B = Pin(9, Pin.IN)
led = Pin(6, Pin.OUT)

# Constants
THRESHOLD = 50      # cm
TIMEOUT = 30000     # μs
TRIGGER_WINDOW = 5  # seconds

# Counters
entries = 0
exits = 0
total_inside = 0

# Trigger state
last_trigger = None
last_trigger_time = 0

# Measure distance
def measure_distance(trig, echo):
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()
    try:
        duration = time_pulse_us(echo, 1, TIMEOUT)
        distance = (duration * 0.0343) / 2
        if distance > 400 or distance < 0:
            return -1
        return round(distance, 2)
    except OSError:
        return -1

print("Smart Door Counter Running...\n")

while True:
    time.sleep(0.3)  # Slight delay to slow the loop

    distance_A = measure_distance(TRIG_A, ECHO_A)
    distance_B = measure_distance(TRIG_B, ECHO_B)
    now = time.time()

    triggered_A = distance_A != -1 and distance_A < THRESHOLD
    triggered_B = distance_B != -1 and distance_B < THRESHOLD

    if triggered_A:
        led.value(1)
        if last_trigger == "B" and now - last_trigger_time <= TRIGGER_WINDOW:
            entries += 1
            total_inside += 1
            print("Sensor A triggered after B → Entry detected")
            print(f"Total Entered : {entries}")
            print(f"Total Exited  : {exits}")
            print(f"Current Inside: {total_inside}")
            print("------------------------------------------------\n")
            last_trigger = None
        else:
            last_trigger = "A"
            last_trigger_time = now

    elif triggered_B:
        led.value(1)
        if last_trigger == "A" and now - last_trigger_time <= TRIGGER_WINDOW:
            exits += 1
            total_inside = max(0, total_inside - 1)
            print("Sensor B triggered after A → Exit detected")
            print(f"Total Entered : {entries}")
            print(f"Total Exited  : {exits}")
            print(f"Current Inside: {total_inside}")
            print("------------------------------------------------\n")
            last_trigger = None
        else:
            last_trigger = "B"
            last_trigger_time = now

    else:
        led.value(0)
