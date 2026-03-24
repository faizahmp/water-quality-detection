import streamlit as st
import pandas as pd
import time
import requests
from datetime import datetime, timedelta
from line_notifier import push_message
from threading import Thread, Event, Lock
import subprocess
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# === CONFIG ===
JETSON_USER = "jetson"
JETSON_IP = "192.168.1.1"
RECEIVER_FEED_URL = "http://localhost:8500/get_latest"
#RECEIVER_FEED_URL = "http://192.168.1.1:8500/get_latest"


# === THREAD-SAFE GLOBAL BUFFER ===
shared_buffer = []
buffer_lock = Lock()

# === INIT SESSION STATE ===
if "stop_event" not in st.session_state:
    st.session_state.stop_event = Event()
if "data" not in st.session_state:
    st.session_state.data = []
if "stream_thread" not in st.session_state:
    st.session_state.stream_thread = None

# === SSH CONTROL ===
def start_on_jetson():
    try:
        subprocess.call([
            "ssh", f"{JETSON_USER}@{JETSON_IP}",
            "screen -dmS tds_sender python3 /home/jetson/tds_sender.py"
        ])
    except Exception as e:
        st.error(f"❌ SSH start error: {e}")

def stop_on_jetson():
    try:
        subprocess.call([
            "ssh", f"{JETSON_USER}@{JETSON_IP}",
            "pkill -f tds_sender.py"
        ])
    except Exception as e:
        st.error(f"❌ SSH stop error: {e}")

# === POLLING THREAD ===
def poll_data(stop_event):
    global shared_buffer
    try:
        while not stop_event.is_set():
            res = requests.get(RECEIVER_FEED_URL, timeout=2)
            if res.status_code == 200:
                item = res.json()
                tds = float(item.get("tds_ppm", 0))
                label = item.get("label", "normal")
                is_anomaly = (label.lower() == "anomaly")
                timestamp = time.time()

                with buffer_lock:
                    shared_buffer.append({
                        "timestamp": timestamp,
                        "tds_ppm": tds,
                        "is_anomaly": is_anomaly
                    })

                if is_anomaly:
                    ts_str = time.strftime("%M:%S", time.localtime(timestamp))
                    push_message(f"🚨 TDS Anomaly Detected: {tds} ppm at {ts_str}")

            time.sleep(1)
    except Exception as e:
        print("❌ Polling thread crashed:", e)

# === STREAMLIT UI ===
st.set_page_config(layout="wide")
st.title("💧 Continuous TDS Monitoring (Time Series)")

col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start Monitoring"):
        start_on_jetson()
        if not st.session_state.stream_thread or not st.session_state.stream_thread.is_alive():
            st.session_state.stop_event.clear()
            t = Thread(target=poll_data, args=(st.session_state.stop_event,), daemon=True)
            t.start()
            st.session_state.stream_thread = t

with col2:
    if st.button("⏹️ Stop Monitoring"):
        stop_on_jetson()
        st.session_state.stop_event.set()

# === LIVE PLOTTING (no reset, continuous time)
chart_placeholder = st.empty()

last_plot_data_len = 0  # Track how many points were plotted before

while True:
    new_data_received = False

    # Merge new data if available
    with buffer_lock:
        if shared_buffer:
            st.session_state.data.extend(shared_buffer)
            shared_buffer.clear()
            new_data_received = True

    # Plot only if new data arrived
    if new_data_received:
        df = pd.DataFrame(st.session_state.data)
        df = df[pd.to_numeric(df["timestamp"], errors="coerce").notnull()]
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

        # === Matplotlib plot ===
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df["timestamp"], df["tds_ppm"], color="blue", label="TDS (ppm)")
        ax.scatter(df["timestamp"], df["tds_ppm"], color="blue", s=25)

        # Red shading for anomalies
        for _, row in df.iterrows():
            if row["is_anomaly"]:
                ax.axvspan(row["timestamp"] - timedelta(seconds=0.5),
                           row["timestamp"] + timedelta(seconds=0.5),
                           color="red", alpha=0.3)

        ax.set_title("📈 Continuous Real-Time TDS Monitoring")
        ax.set_xlabel("Time (MM:SS)")
        ax.set_ylabel("TDS (ppm)")
        ax.set_ylim(0, 500)  # Fixed Y-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        ax.grid(True)
        ax.legend()
        fig.autofmt_xdate()

        chart_placeholder.pyplot(fig)

    elif not st.session_state.data:
        chart_placeholder.info("No data yet. Click ▶️ Start Monitoring.")

    time.sleep(1)


