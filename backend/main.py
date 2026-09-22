from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class PaymentRequest(BaseModel):
    amount: float
    currency: str = "INR"


@app.get("/")
def home():
    return {
        "message": "Payment Gateway Backend is running!"
    }


@app.post("/payment/create")
def create_payment(payment: PaymentRequest):

    amount_in_paise = int(payment.amount * 100)

    return {
        "message": "Payment order request received",
        "amount": amount_in_paise,
        "currency": payment.currency
    }