from fastapi import FastAPI,Response
from pydantic import BaseModel,Field
from app.config import settings
import httpx

app = FastAPI(title="api-gateway")

@app.get("/health")
def test():
    return {'msg':'api-gateway is running'}


@app.get("/payments/{payment_id}")
def get_payment(payment_id: str):
    reply = httpx.get(f"{settings.payment_url}/payments/{payment_id}", timeout=5.0)
    return Response(
        content=reply.content,
        status_code=reply.status_code,
        media_type="application/json",
    )


