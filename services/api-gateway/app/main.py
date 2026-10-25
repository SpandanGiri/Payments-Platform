from fastapi import FastAPI,Response
from pydantic import BaseModel,Field
from app.config import settings
import httpx

app = FastAPI(title="api-gateway")

@app.get("/health")
def test():
    return {'msg':'api-gateway is running'}

def relay(reply: httpx.Response) -> Response:
    return Response(
        content=reply.content,
        status_code=reply.status_code,
        media_type="application/json",
    )

@app.get("/payments/{payment_id}")
def get_payment(payment_id: str):
    reply = httpx.get(f"{settings.payment_url}/payments/{payment_id}", timeout=5.0)
    return Response(
        content=reply.content,
        status_code=reply.status_code,
        media_type="application/json",
    )

@app.post("/payments")
def create_payment(body: dict):
    reply = httpx.post(f"{settings.payment_url}/payments", json=body, timeout=5.0)
    return relay(reply)

@app.post("/payments/{payment_id}/capture")
def capture_payment(payment_id: str):
    reply = httpx.post(f"{settings.payment_url}/payments/{payment_id}/capture", timeout=5.0)
    return relay(reply)

