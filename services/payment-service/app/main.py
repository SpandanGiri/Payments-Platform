from uuid import UUID
import httpx
import logging

from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel,Field
from app.database import get_db,engine,Base
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.scehmas import PaymentCreate,PaymentOut
from app.models import Payment
from app.config import settings
from app import ledger_client
from app.models import Payment, PaymentStatus




Base.metadata.create_all(bind=engine)
logger = logging.getLogger("payment-service")

app=FastAPI(title="payment-service")

class PaymentCreate(BaseModel):
    merchant_id: str = Field(min_length=1, max_length=64)
    amount: int = Field(gt=0, description="Amount in paise (₹1 = 100)")
    currency: str = Field(default="INR", pattern="^[A-Z]{3}$")


@app.get("/health")
def test():
    return {'msg':'payment-service is running'}

@app.get("/health/db")
def testDb(db:Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}

@app.get("/debug/ledger")
def debug_ledger():
    response = httpx.get(f"{settings.ledger_url}/health", timeout=3.0)
    return {"ledger_status_code": response.status_code, "ledger_said": response.json()}


@app.post("/payments")
def createPayment(body:PaymentCreate,db:Session = Depends(get_db)):
    payment = Payment(**body.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@app.get("/payments/{payment_id}")
def getPayment(payment_id:UUID,db:Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
    

@app.post("/payments/{payment_id}/capture", response_model=PaymentOut)
def capture_payment(payment_id: UUID, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != PaymentStatus.CREATED:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot capture a payment in status {payment.status.value}",
        )

    try:
        ledger_client.record_capture(payment.id, payment.merchant_id, payment.amount, payment.currency)
    except httpx.HTTPError as exc:
        logger.error("ledger call failed for payment %s: %s", payment.id, exc)
        raise HTTPException(
            status_code=503,
            detail="Ledger service unavailable. The payment was not captured, please retry.",
        )

    payment.status = PaymentStatus.CAPTURED
    db.commit()
    db.refresh(payment)
    return payment
