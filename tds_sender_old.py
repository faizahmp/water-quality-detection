# tds_sender.py (Windows)
import requests
import time
import random

MAC_IP = "192.168.1.2"  # Replace with Mac's real IP
CONTROL_URL = f"http://{MAC_IP}:8500/control"
SEND_URL = f"http://{MAC_IP}:8500/tds_push"


def generate_data():
    tds = round(random.uniform(300, 1200), 2)
    label = "anomaly" if tds > 800 or tds < 100 else "normal"
    return {"tds_ppm": tds, "label": label}


print("📡 Waiting for control signal from Mac...")

while True:
    try:
        status = requests.get(CONTROL_URL).json()
        if status.get("running", False):
            data = generate_data()
            print("🔼 Sending:", data)
            requests.post(SEND_URL, json=data)
        else:
            print("⏸️ Waiting...")
    except Exception as e:
        print("❌ Error:", e)

    time.sleep(1)
