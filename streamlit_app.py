import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from multiprocessing import Queue, Process
from ph_streamer import stream_ph_data

# Start data streaming process only once
if "ph_data_queue" not in st.session_state:
    st.session_state.ph_data_queue = Queue()
    st.session_state.data = []
    p = Process(target=stream_ph_data, args=(st.session_state.ph_data_queue,))
    p.daemon = True
    p.start()

st.title("🧪 Real-Time pH Sensor Dashboard")

placeholder = st.empty()

# Continuously update plot
while True:
    # Collect data from queue
    while not st.session_state.ph_data_queue.empty():
        st.session_state.data.append(st.session_state.ph_data_queue.get())

    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

        with placeholder.container():
            st.subheader("📊 pH Time Series")
            fig, ax = plt.subplots()
            ax.plot(df["timestamp"], df["pH"], marker="o", linestyle="-", color="green")
            ax.set_title("Live pH Readings")
            ax.set_xlabel("Time")
            ax.set_ylabel("pH Level")
            ax.grid(True)
            st.pyplot(fig)

    time.sleep(1)  # Limit refresh rate
