# Water Quality Monitoring System

## 🔍 Project Description
Water Quality Monitoring System is a Python-based solution to continuously monitor water quality using pH and Total Dissolved Solids (TDS) sensors. A remote Jetson-powered device publishes TDS data to a server, which feeds a Streamlit dashboard and triggers anomaly detection. When dangerous levels are detected, the system sends instant notifications through LINE Messaging API.

Key features:
- real-time TDS data ingestion and display
- anomaly detection (threshold-based and/or model-driven)
- LINE alerts for water quality incidents
- modular architecture with local and remote server modes

## 🏗️ Architecture

1. **Remote device** (e.g., Jetson)
   - `tds_sender.py`: Samples TDS (and optionally pH) and sends to remote server endpoint.
   - `remote_server.py`: Endpoint to receive sensor payload and forward to receiver/store.

2. **Receiver & local server**
   - `receiver.py`: Receives and logs incoming sensor data; may publish to a message queue or DB.
   - `local_server.py`: Optional local API endpoint for Streamlit and for local data collection.

3. **Streamlit dashboard**
   - `streamlit_app.py`: Streamlit UI for plotting sensor values, showing recent history, status, and alerts.
   - anomaly detection logic in the Streamlit app (or separate module) identifies threshold crossings or unusual trends.

4. **Notifier**
   - `line_notifier.py`: Sends LINE messages via LINE Messaging API when anomalies occur.

Data flow:
`Jetson sensor -> remote_server -> receiver/local_server -> streamlit_app -> anomaly detection -> line_notifier`

## ⚙️ Tech Stack
- Python 3.8+
- Streamlit
- Flask / FastAPI / custom HTTP receiver (project-specific)
- LINE Messaging API
- Jetson (edge device)
- pH & TDS sensor data

## 🛠️ Installation

1. Clone repository

```bash
git clone https://github.com/<your-org>/water-quality-detection.git
cd water-quality-detection
```

2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Edit `.env` or environment variables as needed (see next section)

## 🔐 Environment Variables

Create a `.env` file in project root with:

```env
# LINE API
LINE_CHANNEL_ACCESS_TOKEN=YOUR_LINE_CHANNEL_ACCESS_TOKEN
LINE_USER_ID=YOUR_LINE_USER_ID_OR_GROUP_ID

# Server settings
REMOTE_SERVER_URL=http://<remote-server-host>:<port>/api/tds
LOCAL_SERVER_URL=http://localhost:8000/api/tds

# Anomaly detection thresholds
TDS_THRESHOLD=500
PH_LOW_THRESHOLD=6.5
PH_HIGH_THRESHOLD=8.5

# Streamlit
STREAMLIT_PORT=8501
```

Optional settings:
- `LOG_LEVEL=INFO` or `DEBUG`
- `DATA_RETENTION_DAYS=7`

## ▶️ How to Run

### 1) Run local receiver API (if used)

```bash
python local_server.py
# or
python receiver.py
```

### 2) Run remote receiving API

```bash
python remote_server.py
```

### 3) Run Streamlit dashboard

```bash
streamlit run streamlit_app.py
```

Then open: `http://localhost:8501`

### 4) Run remote sensor sender (Jetson / device)

```bash
python tds_sender.py
```

### 5) (Optional) Test LINE notifier

```bash
python line_notifier.py --test
```

## 🗂️ Project Structure

```
water-quality-detection/
├── streamlit_app.py        # Main dashboard UI
├── line_notifier.py        # LINE alert sender
├── local_server.py         # Local receiver server
├── remote_server.py        # Remote server ingest endpoint
├── receiver.py             # Sensor data receiver and persistence
├── tds_sender.py           # Sensor data sender (Jetson side)
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── ph and tds data/        # sensor collection scripts and CSV data
│   ├── ph_data_collect.py
│   ├── tds_data_collect.py
│   ├── ph_data.csv
│   ├── tds_data.csv
│   └── sketches/*.ino
└── .env.example (optional) # Example env vars
```

## 🧪 Testing and Validation
- Validate sensor flow by running `tds_sender.py` and reviewing data on Streamlit UI.
- Intentionally exceed thresholds and confirm LINE notifications are delivered.
- Check logs for HTTP 200/500 handshakes between `remote_server`, `receiver`, and Streamlit.

## 📌 Notes
- Adapt pH/TDS thresholds to the targeted water source (tap, river, reservoir, etc.)
- Secure LINE access tokens and never commit `.env` to git
- For production, deploy API endpoints using Docker or cloud VM and enable HTTPS

---

## TEAM

| | |
|------------------------|----------------------|
| Faizah Mappanyompa Rukka | Huynh Truong Tu      |
| Umang Dobhal           | Prerna Jamloki       |
| Kanyarak Klaichit      |                      |

This project was developed as part of coursework in the  **Department of Human Intelligence Systems**, Graduate School of Life Science and Systems Engineering, Kyushu Institute of Technology, Fukuoka, Japan