from fastapi import FastAPI,Depends
from pydantic import BaseModel,Field
from app.database import get_db,engine,Base
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.scehmas import PaymentCreate,PaymentOut
from app.models import Payment


Base.metadata.create_all(bind=engine)

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



@app.post("/payments")
def createPayment(body:PaymentCreate,db:Session = Depends(get_db)):
    payment = Payment(**body.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@app.get("/payments/{payment_id}")
def getPayment(payment_id:str):
    pass

