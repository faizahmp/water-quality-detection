import serial
import pandas as pd
import time
import re
import os

# === CONFIGURATION ===
PORT = "COM4"  # Change this to your Arduino's serial port
BAUDRATE = 9600
DURATION_SEC = 120  # Total collection time in seconds
SAMPLE_RATE_HZ = 10  # 10 samples per second
CSV_FILE = "data/ph_data.csv"
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)

# === INITIALIZE SERIAL ===
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2)  # Allow Arduino to reset

# === DATA COLLECTION ===
data = []
interval = 1 / SAMPLE_RATE_HZ
timestep = 0
last_print_time = -1

print(f"Collecting pH data for {DURATION_SEC} seconds...")

start_time = time.time()

while (time.time() - start_time) < DURATION_SEC:
    loop_start = time.time()

    try:
        raw_bytes = ser.readline()
        line = raw_bytes.decode("utf-8", errors="ignore").strip()
        if line:
            match = re.match(r"Voltage:\s*([\d.]+)\s*V\s*\t\s*pH:\s*([\d.]+)", line)
            if match:
                voltage = float(match.group(1))
                ph = float(match.group(2))

                data.append({"timestep": timestep, "voltage_V": voltage, "pH": ph})

                if timestep // SAMPLE_RATE_HZ > last_print_time:
                    print(
                        f"[{timestep // SAMPLE_RATE_HZ}s] Voltage: {voltage:.3f} V, pH: {ph:.2f}"
                    )
                    last_print_time = timestep // SAMPLE_RATE_HZ

                timestep += 1
    except Exception as e:
        print("Read error:", e)

    elapsed = time.time() - loop_start
    sleep_time = interval - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)

# === CLEAN UP ===
ser.close()

# === SAVE TO CSV ===
df = pd.DataFrame(data)
df.to_csv(CSV_FILE, index=False)
print(f"Saved {len(df)} samples to '{CSV_FILE}'")
