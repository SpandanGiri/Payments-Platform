from fastapi import FastAPI,Depends
from pydantic import BaseModel,Field
from app.database import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI()

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
def createPayment():
    pass

@app.get("/payments/{payment_id}")
def getPayment(payment_id:str):
    pass

