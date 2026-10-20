from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import PaymentStatus



class PaymentCreate(BaseModel):
    merchant_id: str = Field(min_length=1, max_length=64)
    amount: int = Field(gt=0, description="Amount in paise (₹1 = 100)")
    currency: str = Field(default="INR", pattern="^[A-Z]{3}$")

class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    merchant_id: str
    amount: int
    currency: str
    status: PaymentStatus
    created_at: datetime
