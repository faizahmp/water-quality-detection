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

JETSON_USER = "jetson"
#JETSON_USER = "faizah"
JETSON_IP = "192.168.1.1"
RECEIVER_FEED_URL = "http://localhost:8500/get_latest"

shared_buffer = []
shared_status = {"value": "Unknown"}
buffer_lock = Lock()

shared_status = {"value": "Unknown"}

if "stop_event" not in st.session_state:
    st.session_state.stop_event = Event()
if "data" not in st.session_state:
    st.session_state.data = []
if "stream_thread" not in st.session_state:
    st.session_state.stream_thread = None


def start_on_jetson():
    try:
        subprocess.call([
            "ssh", f"{JETSON_USER}@{JETSON_IP}",
            #"screen -dmS tds_sender python3 /home/faizah/tds_sender.py"
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

def poll_data(stop_event):
    global shared_buffer
    try:
        while not stop_event.is_set():
            res = requests.get(RECEIVER_FEED_URL, timeout=2)
            if res.status_code == 200:
                item = res.json()
                tds = float(item.get("tds_ppm", 0))
                ph = float(item.get("ph", 0))
                tds_label = item.get("tds_label", "normal")
                ph_label = item.get("ph_label", "normal")
                raw_status = item.get("status", "").lower()
                status = "Calibrating" if raw_status == "calibrating" else "Detecting" if raw_status == "detecting" else "Unknown"
                shared_status["value"] = status

                timestamp = time.time()
                is_tds_anomaly = tds_label.lower() == "anomaly"
                is_ph_anomaly = ph_label.lower() == "anomaly"

                with buffer_lock:
                    shared_buffer.append({
                        "timestamp": timestamp,
                        "tds_ppm": tds,
                        "ph": ph,
                        "tds_anomaly": is_tds_anomaly,
                        "ph_anomaly": is_ph_anomaly
                    })

                st.session_state.status = status

                if is_tds_anomaly:
                    push_message(f"🚨 TDS Anomaly Detected: {tds} ppm")
                if is_ph_anomaly:
                    push_message(f"🚨 pH Anomaly Detected: {ph}")
            time.sleep(1)
    except Exception as e:
        print("❌ Polling thread crashed:", e)

st.set_page_config(layout="wide")
st.title("💧 Continuous TDS and pH Monitoring")

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


# =========== PLOTTING ============
status_placeholder = st.empty()
chart_placeholder1 = st.empty()
chart_placeholder2 = st.empty()

while True:
    new_data = False
    with buffer_lock:
        if shared_buffer:
            st.session_state.data.extend(shared_buffer)
            shared_buffer.clear()
            new_data = True

    # Live update the status line
    status_placeholder.markdown(f"### 🔄 Status: **{shared_status['value']}**")


    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df[pd.to_numeric(df["timestamp"], errors="coerce").notnull()]

        fig1, ax1 = plt.subplots(figsize=(10, 3))
        ax1.plot(df["timestamp"], df["tds_ppm"], label="TDS (ppm)", color="blue")
        ax1.scatter(df["timestamp"], df["tds_ppm"], s=25, color="blue")
        in_anomaly = False
        start_time = None
        for i, row in df.iterrows():
            if row["tds_anomaly"]:
                if not in_anomaly:
                    start_time = row["timestamp"]
                    in_anomaly = True
            else:
                if in_anomaly:
                    ax1.axvspan(start_time, row["timestamp"], color="red", alpha=0.3, linewidth=0)
                    in_anomaly = False
        if in_anomaly:
            ax1.axvspan(start_time, df.iloc[-1]["timestamp"], color="red", alpha=0.3, linewidth=0)

        ax1.set_ylim(0, 500)
        ax1.set_title("TDS Monitoring")
        ax1.set_xlabel("Time (MM:SS)")
        ax1.set_ylabel("TDS (ppm)")
        ax1.grid(True)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        chart_placeholder1.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(10, 3))
        ax2.plot(df["timestamp"], df["ph"], label="pH", color="green")
        ax2.scatter(df["timestamp"], df["ph"], s=25, color="green")
        in_ph_anomaly = False
        ph_start = None
        for i, row in df.iterrows():
            if row["ph_anomaly"]:
                if not in_ph_anomaly:
                    ph_start = row["timestamp"]
                    in_ph_anomaly = True
            else:
                if in_ph_anomaly:
                    ax2.axvspan(ph_start, row["timestamp"], color="orange", alpha=0.3, linewidth=0)
                    in_ph_anomaly = False
        if in_ph_anomaly:
            ax2.axvspan(ph_start, df.iloc[-1]["timestamp"], color="orange", alpha=0.3, linewidth=0)

        ax2.set_ylim(0, 14)
        ax2.set_title("pH Monitoring")
        ax2.set_xlabel("Time (MM:SS)")
        ax2.set_ylabel("pH Value")
        ax2.grid(True)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        chart_placeholder2.pyplot(fig2)

    else:
        chart_placeholder1.info("No data yet.")
        chart_placeholder2.info("No data yet.")

    time.sleep(1)
