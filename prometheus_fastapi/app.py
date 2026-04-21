from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import random
import time

app = FastAPI()

# Instrument the app with Prometheus metrics
Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    """Basic health check endpoint."""
    return {"message": "FastAPI + Prometheus Lab"}

@app.post("/verify")
def verify_title(land_id: str):
    """
    Simulate a title verification request.
    Randomly takes 0.1 to 2 seconds to mimic real database queries.
    """
    # Simulate processing time
    processing_time = random.uniform(0.1, 2.0)
    time.sleep(processing_time)
    # Simulate occasional errors (10% chance)
    if random.random() < 0.1:
        return {"status": "error", "message": "Verification failed"}

    return {
        "land_id": land_id,
        "status": "verified",
        "processing_time_ms": round(processing_time * 1000, 2)
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on http://0.0.0.0:8001")
    print("Metrics available at http://0.0.0.0:8001/metrics")
    uvicorn.run(app, host="0.0.0.0", port=8001)


    