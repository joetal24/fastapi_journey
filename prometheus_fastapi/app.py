from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from kafka_producer import publish_fraud_check
from pydantic import BaseModel
import random
import time
import uuid

app = FastAPI()
Instrumentator().instrument(app).expose(app)

class VerifyRequest(BaseModel):
    land_id: str
    owner_name: str
    national_id: str
    amount: float
    date: str

@app.get("/")
def read_root():
    return {"message": "PlotSure API — Land Title Verification"}

@app.post("/verify")
def verify_title(request: VerifyRequest):
    """
    Hybrid verification:
    1. Basic instant checks
    2. Async deep fraud detection via Kafka
    """
    # Simulate basic DB check (fast)
    processing_time = random.uniform(0.1, 0.3)
    time.sleep(processing_time)

    # Simulate occasional system errors
    if random.random() < 0.1:
        raise HTTPException(
            status_code=500, 
            detail="Verification failed"
        )

    # Generate verification ID for tracking
    verification_id = str(uuid.uuid4())

    # Publish to Kafka for async deep fraud check
    publish_fraud_check(
        verification_id=verification_id,
        land_id=request.land_id,
        owner_name=request.owner_name,
        national_id=request.national_id,
        amount=request.amount,
        date=request.date
    )

    # Return immediately — don't wait for fraud check
    return {
        "verification_id": verification_id,
        "land_id": request.land_id,
        "status": "preliminary_verified",
        "message": "Basic checks passed. Deep fraud analysis in progress.",
        "processing_time_ms": round(processing_time * 1000, 2)
    }

@app.get("/verification/{verification_id}/status")
def check_status(verification_id: str):
    """
    Check the status of a verification.
    In production this would query Supabase for the updated status.
    """
    return {
        "verification_id": verification_id,
        "status": "processing",
        "message": "Fraud detection in progress — check back shortly"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting PlotSure API on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)