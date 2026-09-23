import os
import razorpay

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.database import engine, Base, SessionLocal
from backend import models


load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)


# -----------------------------
# Request Models
# -----------------------------

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "INR"


class PaymentVerification(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Payment Gateway Backend is running!"
    }


# -----------------------------
# Create Razorpay Order
# -----------------------------

@app.post("/payment/create")
def create_payment(payment: PaymentRequest):

    amount_in_paise = int(payment.amount * 100)

    order_data = {
        "amount": amount_in_paise,
        "currency": payment.currency,
        "receipt": "receipt_001"
    }

    order = client.order.create(data=order_data)

    # Save order as created
    db = SessionLocal()

    new_payment = models.Payment(
        order_id=order["id"],
        amount=payment.amount,
        currency=payment.currency,
        status="created"
    )

    db.add(new_payment)
    db.commit()
    db.close()

    return {
        "message": "Razorpay order created successfully",
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"]
    }


# -----------------------------
# Razorpay Checkout
# -----------------------------

@app.get("/checkout/{order_id}", response_class=HTMLResponse)
def checkout(order_id: str):

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Razorpay Payment</title>

        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>

        <style>

            body {{
                font-family: Arial;
                text-align: center;
                margin-top: 100px;
            }}

            button {{
                padding: 15px 30px;
                font-size: 18px;
                cursor: pointer;
            }}

        </style>

    </head>

    <body>

        <h2>💳 Payment Gateway</h2>

        <p>Premium Course</p>

        <h3>₹500</h3>

        <button id="pay-button">
            Pay ₹500
        </button>


        <script>

            var options = {{

                "key": "{RAZORPAY_KEY_ID}",

                "amount": 50000,

                "currency": "INR",

                "name": "Payment Gateway Demo",

                "description": "Premium Course",

                "order_id": "{order_id}",


                "handler": async function(response) {{

                    try {{

                        const verification = await fetch(
                            "/payment/verify",
                            {{

                                method: "POST",

                                headers: {{
                                    "Content-Type": "application/json"
                                }},

                                body: JSON.stringify({{

                                    razorpay_payment_id:
                                        response.razorpay_payment_id,

                                    razorpay_order_id:
                                        response.razorpay_order_id,

                                    razorpay_signature:
                                        response.razorpay_signature

                                }})

                            }}
                        );


                        const result =
                            await verification.json();


                        if (result.status === "paid") {{

                            alert(
                                "Payment verified successfully!\\n\\n" +
                                "Payment ID: " +
                                result.payment_id
                            );

                        }} else {{

                            alert(
                                "Payment verification failed."
                            );

                        }}

                    }} catch (error) {{

                        alert(
                            "Something went wrong while verifying payment."
                        );

                    }}

                }}

            }};


            var rzp = new Razorpay(options);


            document.getElementById(
                "pay-button"
            ).onclick = function(e) {{

                rzp.open();

                e.preventDefault();

            }};

        </script>

    </body>

    </html>
    """


# -----------------------------
# Verify Payment
# -----------------------------

@app.post("/payment/verify")
def verify_payment(payment: PaymentVerification):

    db = SessionLocal()

    try:

        # Verify Razorpay signature
        client.utility.verify_payment_signature({

            "razorpay_payment_id":
                payment.razorpay_payment_id,

            "razorpay_order_id":
                payment.razorpay_order_id,

            "razorpay_signature":
                payment.razorpay_signature

        })


        # Fetch payment information
        payment_details = client.payment.fetch(
            payment.razorpay_payment_id
        )


        # Find existing order
        db_payment = (
            db.query(models.Payment)
            .filter(
                models.Payment.order_id ==
                payment.razorpay_order_id
            )
            .first()
        )


        if db_payment:

            db_payment.payment_id = (
                payment.razorpay_payment_id
            )

            db_payment.amount = (
                payment_details["amount"] / 100
            )

            db_payment.currency = (
                payment_details["currency"]
            )

            db_payment.status = "paid"


        else:

            db_payment = models.Payment(

                order_id=payment.razorpay_order_id,

                payment_id=payment.razorpay_payment_id,

                amount=payment_details["amount"] / 100,

                currency=payment_details["currency"],

                status="paid"

            )

            db.add(db_payment)


        db.commit()

        return {

            "message":
                "Payment verified and saved successfully",

            "status": "paid",

            "payment_id":
                payment.razorpay_payment_id,

            "order_id":
                payment.razorpay_order_id

        }


    except Exception as e:

        db.rollback()

        return {

            "message":
                "Payment verification failed",

            "status": "failed"

        }


    finally:

        db.close()


# -----------------------------
# Payment History
# -----------------------------

@app.get("/payments")
def payment_history():

    db = SessionLocal()

    payments = (
        db.query(models.Payment)
        .order_by(
            models.Payment.created_at.desc()
        )
        .all()
    )


    result = []

    for payment in payments:

        result.append({

            "id": payment.id,

            "order_id": payment.order_id,

            "payment_id": payment.payment_id,

            "amount": payment.amount,

            "currency": payment.currency,

            "status": payment.status,

            "created_at": payment.created_at

        })


    db.close()

    return {

        "payments": result

    }


# -----------------------------
# Razorpay Webhook
# -----------------------------

@app.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):

    body = await request.body()

    signature = request.headers.get(
        "X-Razorpay-Signature"
    )


    if not signature:

        raise HTTPException(
            status_code=400,
            detail="Missing webhook signature"
        )


    try:

        client.utility.verify_webhook_signature(

            body.decode("utf-8"),

            signature,

            RAZORPAY_WEBHOOK_SECRET

        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature"
        )


    data = await request.json()

    event = data.get("event")


    if event == "payment.captured":

        payment_entity = (
            data["payload"]["payment"]["entity"]
        )

        order_id = payment_entity.get(
            "order_id"
        )

        payment_id = payment_entity.get(
            "id"
        )


        db = SessionLocal()

        db_payment = (
            db.query(models.Payment)
            .filter(
                models.Payment.order_id ==
                order_id
            )
            .first()
        )


        if db_payment:

            db_payment.payment_id = payment_id

            db_payment.status = "paid"

            db.commit()


        db.close()


    elif event == "payment.failed":

        payment_entity = (
            data["payload"]["payment"]["entity"]
        )

        order_id = payment_entity.get(
            "order_id"
        )


        db = SessionLocal()

        db_payment = (
            db.query(models.Payment)
            .filter(
                models.Payment.order_id ==
                order_id
            )
            .first()
        )


        if db_payment:

            db_payment.status = "failed"

            db.commit()


        db.close()


    return {
        "status": "ok"
    }

@app.post("/payment/test-success/{order_id}")
def test_success(order_id: str):

    db = SessionLocal()

    payment = (
        db.query(models.Payment)
        .filter(models.Payment.order_id == order_id)
        .first()
    )

    if not payment:
        db.close()
        return {
            "status": "failed",
            "message": "Order not found"
        }

    payment.status = "test_paid"

    db.commit()
    db.refresh(payment)
    db.close()

    return {
        "status": "test_paid",
        "message": "Development payment simulated successfully",
        "order_id": order_id
    }