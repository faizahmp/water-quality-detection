# import time
# import random
# from queue import Queue
# from line_notifier import push_message
# import time

# def stream_ph_data(queue: Queue):
#     print("🧪 Starting simulated pH data stream...")
#     while True:
#         # 10% abnormal values
#         if random.random() < 0.1:
#             ph = round(random.choice([random.uniform(4.0, 5.9), random.uniform(8.1, 9.0)]), 2)
#         else:
#             ph = round(7 + random.uniform(-1.0, 1.0), 2)

#         voltage = round(random.uniform(2.0, 3.0), 3)
#         timestamp = time.time()

#         # Detect abnormal and notify
#         if ph < 6.0 or ph > 8.0:
#             ts_str = time.strftime("%M:%S", time.localtime(timestamp))
#             msg = f"🚨 Abnormal pH: {ph} detected at {ts_str}"
#             print("⚠️", msg)
#             push_message(msg)

#         queue.put({
#             "timestamp": timestamp,
#             "voltage": voltage,
#             "pH": ph
#         })

#         time.sleep(1)

# tds_streamer.py
# import time
# import random
# from queue import Queue
# from line_notifier import push_message
# import requests

# def stream_tds_data(queue: Queue):
#     print("📡 Simulating TDS stream...")

#     while True:
#         # 10% chance of abnormal (e.g., TDS > 800 or < 100)
#         if random.random() < 0.1:
#             tds_ppm = round(random.choice([random.uniform(900, 1200), random.uniform(50, 90)]), 2)
#             is_anomaly = True
#         else:
#             tds_ppm = round(random.uniform(300, 700), 2)
#             is_anomaly = False

#         voltage = round(random.uniform(2.0, 3.0), 3)
#         timestamp = time.time()

#         data = {
#             "timestamp": timestamp,
#             "voltage": voltage,
#             "tds_ppm": tds_ppm,
#             "is_anomaly": is_anomaly
#         }

#         queue.put(data)

#         # Notify LINE and local server only if anomaly
#         if is_anomaly:
#             ts_str = time.strftime("%M:%S", time.localtime(timestamp))
#             msg = f"🚨 Abnormal TDS: {tds_ppm} ppm at {ts_str}"
#             push_message(msg)

#             # POST to another server (e.g., FastAPI or Flask on localhost)
#             try:
#                 requests.post("http://localhost:8000/tds_alert", json=data)
#             except Exception as e:
#                 print("❌ Failed to notify local server:", e)

#         time.sleep(1)

# tds_streamer.py
import time
import random
from queue import Queue
from line_notifier import push_message
import requests

def stream_tds_data(queue: Queue, post_url: str = None):
    print("🧪 Starting local simulated TDS stream...")

    while True:
        # Simulate TDS value: 90% normal, 10% abnormal
        if random.random() < 0.1:
            tds_ppm = round(random.choice([random.uniform(900, 1200), random.uniform(50, 90)]), 2)
            label = "anomaly"
        else:
            tds_ppm = round(random.uniform(300, 700), 2)
            label = "normal"

        is_anomaly = (label == "anomaly")
        voltage = round(random.uniform(2.0, 3.0), 3)
        timestamp = time.time()

        result = {
            "timestamp": timestamp,
            "voltage": voltage,
            "tds_ppm": tds_ppm,
            "label": label,
            "is_anomaly": is_anomaly
        }

        # Send to queue
        queue.put(result)

        # Optional: send to local POST endpoint (if provided)
        if is_anomaly and post_url:
            try:
                requests.post(post_url, json=result)
            except Exception as e:
                print("❌ Failed to post to server:", e)

        # Send LINE alert
        if is_anomaly:
            ts_str = time.strftime("%M:%S", time.localtime(timestamp))
            msg = f"🚨 Anomaly Detected: {tds_ppm} ppm at {ts_str}"
            push_message(msg)

        time.sleep(1)
