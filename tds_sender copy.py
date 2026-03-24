# tds_sender.py (Jetson)
import requests
import time
import random

MAC_IP = "192.168.1.2"  # <-- Replace with Mac's IP
SEND_URL = f"http://{MAC_IP}:8500/tds_push"

def generate_data():
    tds = round(random.uniform(300, 1200), 2)
    label = "anomaly" if tds > 800 or tds < 100 else "normal"
    return {"tds_ppm": tds, "label": label}

while True:
    try:
        data = generate_data()
        print("🔼 Sending:", data)
        requests.post(SEND_URL, json=data)
    except Exception as e:
        print("❌ Send error:", e)
    time.sleep(1)

