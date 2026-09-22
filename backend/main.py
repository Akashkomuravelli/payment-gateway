import os

import razorpay
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from backend.database import engine, Base
from backend import models
from fastapi.responses import HTMLResponse
load_dotenv()

app = FastAPI()
Base.metadata.create_all(bind=engine)
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)


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

    order_data = {
        "amount": amount_in_paise,
        "currency": payment.currency,
        "receipt": "receipt_001"
    }

    order = client.order.create(data=order_data)

    return {
        "message": "Razorpay order created successfully",
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"]
    }

@app.get("/checkout/{order_id}", response_class=HTMLResponse)
def checkout(order_id: str):

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Razorpay Payment</title>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    </head>

    <body>

        <h2>💳 Payment Gateway</h2>
        <button id="pay-button">Pay ₹500</button>

        <script>

            var options = {{
                "key": "{RAZORPAY_KEY_ID}",
                "amount": 50000,
                "currency": "INR",
                "name": "Payment Gateway Demo",
                "description": "Premium Course",
                "order_id": "{order_id}",

                "handler": function (response) {{

                    alert(
                        "Payment successful!\\n\\n" +
                        "Payment ID: " + response.razorpay_payment_id
                    );

                    console.log(response);
                }},

                "theme": {{
                    "color": "#3399cc"
                }}
            }};

            var rzp = new Razorpay(options);

            document.getElementById("pay-button").onclick = function(e) {{
                rzp.open();
                e.preventDefault();
            }};

        </script>

    </body>
    </html>
    """