import uuid
from app.models import LedgerEntry
from app.schemas import EntryOut, TransactionCreate
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db,Base,engine
from app import models

from app.models import LedgerEntry
from app.schemas import EntryOut, TransactionCreate

app = FastAPI(title="ledger-service")


Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"msg": "ledger-service is running"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}

@app.post("/transactions", response_model=list[EntryOut], status_code=201)
def create_transaction(body: TransactionCreate, db: Session = Depends(get_db)):
    transaction_id = uuid.uuid4()
    entries = [
        LedgerEntry(
            transaction_id=transaction_id,
            payment_id=body.payment_id,
            account=e.account,
            direction=e.direction,
            amount=e.amount,
            currency=body.currency,
        )
        for e in body.entries
    ]
    db.add_all(entries)
    db.commit()
    for entry in entries:
        db.refresh(entry)
    return entries




