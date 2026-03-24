# local_server.py
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/tds_alert")
async def receive_tds_alert(request: Request):
    data = await request.json()
    print("📬 Received TDS anomaly:", data)
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
