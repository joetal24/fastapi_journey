from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from fraud_detection import check_circular_fraud, register_ownership
from pydantic import BaseModel
import random
import time

app = FastAPI()
Instrumentator().instrument(app).expose(app)

# ── Request Models ─────────────────────────────────────────────────
class VerifyRequest(BaseModel):
    land_id: str
    owner_name: str
    national_id: str
    amount: float
    date: str

# ── Endpoints ──────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "PlotSure API — Land Title Verification"}

@app.post("/verify")
def verify_title(request: VerifyRequest):
    """
    Verify a land title and automatically check for fraud.
    """
    # Simulate processing time (Supabase query)
    processing_time = random.uniform(0.1, 2.0)
    time.sleep(processing_time)

    # Simulate occasional system errors
    if random.random() < 0.1:
        raise HTTPException(status_code=500, detail="Verification failed")

    # Register ownership in Neo4j graph
    register_ownership(
        plot_id=request.land_id,
        owner_name=request.owner_name,
        national_id=request.national_id,
        amount=request.amount,
        date=request.date
    )

    # Run fraud detection
    fraud_result = check_circular_fraud(request.national_id)

    if fraud_result["fraud_detected"]:
        return {
            "land_id": request.land_id,
            "status": "FLAGGED",
            "message": "Circular ownership fraud detected",
            "fraud_details": fraud_result,
            "processing_time_ms": round(processing_time * 1000, 2)
        }

    return {
        "land_id": request.land_id,
        "status": "verified",
        "fraud_check": "passed",
        "processing_time_ms": round(processing_time * 1000, 2)
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting PlotSure API on http://localhost:8001")
    print("Metrics available at http://localhost:8001/metrics")
    uvicorn.run(app, host="0.0.0.0", port=8001)