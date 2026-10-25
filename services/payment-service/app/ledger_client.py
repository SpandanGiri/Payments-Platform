from uuid import UUID

import httpx

from app.config import settings


def record_capture(payment_id: UUID, merchant_id: str, amount: int, currency: str) -> None:
    body = {
        "payment_id": str(payment_id),
        "idempotency_key": f"capture:{payment_id}",
        "currency": currency,
        "entries": [
            {"account": "gateway_cash", "direction": "DEBIT", "amount": amount},
            {"account": f"merchant_payable:{merchant_id}", "direction": "CREDIT", "amount": amount},
        ],
    }
    response = httpx.post(f"{settings.ledger_url}/transactions", json=body, timeout=3.0)
    response.raise_for_status()