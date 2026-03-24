# receiver.py
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

latest_data = {}
status_flag = {"running": False}

@app.post("/tds_push")
async def receive_data(request: Request):
    global latest_data
    latest_data = await request.json()
    print("📥 Received:", latest_data)
    return {"status": "received"}

@app.get("/get_latest")
def get_latest():
    return latest_data

@app.post("/control")
async def control_cmd(request: Request):
    global status_flag
    status_flag = await request.json()
    print("🔁 Control updated:", status_flag)
    return {"ok": True}

@app.get("/control")
def get_control():
    return status_flag

if __name__ == "__main__":
    # ensures logs are printed and service is available on all interfaces
    uvicorn.run(
        "receiver:app",         # Module name : app name
        host="0.0.0.0",
        port=8500,
        reload=False,           # Use reload=True only during dev
        access_log=True
    )