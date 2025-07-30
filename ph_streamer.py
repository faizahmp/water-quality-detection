import serial
import re
from multiprocessing import Queue
import threading
import time

def stream_ph_data(queue: Queue, port="COM4", baudrate=9600):
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)
    print("🔌 Serial started... streaming pH data.")

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            match = re.match(r"Voltage:\s*([\d.]+)\s*V\s*\t\s*pH:\s*([\d.]+)", line)
            if match:
                voltage = float(match.group(1))
                ph = float(match.group(2))
                timestamp = time.time()
                queue.put({"timestamp": timestamp, "voltage": voltage, "pH": ph})
        except Exception as e:
            print("Streaming error:", e)
        time.sleep(0.1)
