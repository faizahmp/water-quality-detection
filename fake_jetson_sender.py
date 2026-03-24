# fake_jetson_sender.py
import requests
import time
import random

while True:
    tds = round(random.uniform(300, 1200), 2)
    label = "anomaly" if tds > 800 or tds < 100 else "normal"

    payload = {
        "tds_ppm": tds,
        "label": label
    }

    try:
        res = requests.post("http://localhost:8500/tds_push", json=payload)
        print("🔼 Sent:", payload, "| Response:", res.status_code)
    except Exception as e:
        print("❌ Error sending to local receiver:", e)

    time.sleep(1)
