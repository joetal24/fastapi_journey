from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
import random
import time

app = FastAPI()

Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    return {"message": "FastAPI + Prometheus Lab"}

@app.post("/verify")
def verify_title(land_id: str):
    processing_time = random.uniform(0.1, 2.0)
    time.sleep(processing_time)
    
    # Now returns real HTTP 500 instead of fake 200 error
    if random.random() < 0.1:
        raise HTTPException(status_code=500, detail="Verification failed")
    
    return {
        "land_id": land_id,
        "status": "verified",
        "processing_time_ms": round(processing_time * 1000, 2)
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on http://localhost:8001")
    print("Metrics available at http://localhost:8001/metrics")
    uvicorn.run(app, host="0.0.0.0", port=8001)