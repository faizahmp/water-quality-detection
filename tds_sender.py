# tds_sender.py (Jetson)
import requests
import time
import random

MAC_IP = "192.168.1.2"  # <-- Replace with your Mac's IP
#MAC_IP = "131.206.233.196"
SEND_URL = f"http://{MAC_IP}:8500/tds_push"

def generate_data():
	tds = round(random.uniform(300, 1200), 2)
	ph = round(random.uniform(1, 7), 2)
	tds_label = "anomaly" if tds > 800 or tds < 100 else "normal"
	ph_label = "anomaly" if ph > 4 else "normal"
	status_range = ["Calibrating", "Detecting"]
	status = random.choice(status_range)
	return {"tds_ppm": tds, "tds_label": tds_label, "ph": ph, "ph_label":ph_label, "status":status }

while True:
    try:
        data = generate_data()
        print("🔼 Sending:", data)
        response = requests.post(SEND_URL, json=data, timeout = 2)
        print("Status:", response.status_code, response.text)
    except Exception as e:
        print("❌ Send error:", e)
    time.sleep(1)
