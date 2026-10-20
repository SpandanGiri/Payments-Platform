from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import EntryDirection


class EntryIn(BaseModel):
    account: str = Field(min_length=1, max_length=128)
    direction: EntryDirection
    amount: int = Field(gt=0, description="Amount in paise")

class TransactionCreate(BaseModel):
    payment_id: UUID
    currency: str = Field(default="INR", pattern="^[A-Z]{3}$")
    entries: list[EntryIn] = Field(min_length=2)

    @model_validator(mode="after")
    def check_balanced(self):
        debits = sum(e.amount for e in self.entries if e.direction == EntryDirection.DEBIT)
        credits = sum(e.amount for e in self.entries if e.direction == EntryDirection.CREDIT)
        if debits != credits:
            raise ValueError(f"debits ({debits}) must equal credits ({credits})")
        return self


class EntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_id: UUID
    payment_id: UUID
    account: str
    direction: EntryDirection
    amount: int
    currency: str
    created_at: datetime

class BalanceOut(BaseModel):
    account: str
    total_debits: int
    total_credits: int
    net: int  # debits minus credits