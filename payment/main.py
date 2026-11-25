from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Демонстрационная оплата")


class Payment(BaseModel):
    amount: Decimal = Field(gt=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/pay")
def pay(payment: Payment):
    return {"status": "ok", "transaction_id": str(uuid4())}
