import uuid
from uuid import UUID
from app.models import LedgerEntry
from app.schemas import EntryOut, TransactionCreate
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy import func, select, text
from app.database import get_db,Base,engine
from app import models

from app.models import LedgerEntry,EntryDirection
from app.schemas import EntryOut, TransactionCreate ,BalanceOut

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


@app.get("/entries", response_model=list[EntryOut])
def list_entries(payment_id: UUID, db: Session = Depends(get_db)):
    stmt = (
        select(LedgerEntry)
        .where(LedgerEntry.payment_id == payment_id)
        .order_by(LedgerEntry.created_at, LedgerEntry.id)
    )
    return db.scalars(stmt).all()


@app.get("/accounts/{account}/balance", response_model=BalanceOut)
def get_balance(account: str, db: Session = Depends(get_db)):
    def total(direction: EntryDirection) -> int:
        stmt = select(func.coalesce(func.sum(LedgerEntry.amount), 0)).where(
            LedgerEntry.account == account,
            LedgerEntry.direction == direction,
        )
        return int(db.scalar(stmt))

    debits = total(EntryDirection.DEBIT)
    credits = total(EntryDirection.CREDIT)
    return BalanceOut(account=account, total_debits=debits, total_credits=credits, net=debits - credits)




