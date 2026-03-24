# remote_server.py (Windows laptop)
from fastapi import FastAPI, Request
import subprocess
import uvicorn
import os
import signal

app = FastAPI()
sender_process = None

@app.post("/start_sender")
def start_sender():
    global sender_process
    if sender_process is None or sender_process.poll() is not None:
        print("▶️ Starting tds_sender.py...")
        sender_process = subprocess.Popen(["python", "tds_sender.py"])
        return {"status": "started"}
    else:
        return {"status": "already running"}

@app.post("/stop_sender")
def stop_sender():
    global sender_process
    if sender_process and sender_process.poll() is None:
        print("🛑 Stopping tds_sender.py...")
        sender_process.terminate()
        try:
            sender_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            sender_process.kill()
        sender_process = None
        return {"status": "stopped"}
    return {"status": "not running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8600)
