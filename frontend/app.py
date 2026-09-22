import streamlit as st
import requests

st.set_page_config(
    page_title="Payment Gateway",
    page_icon="💳",
    layout="centered"
)

st.title("💳 Payment Gateway Demo")

st.write(
    "A payment application built using "
    "Python, FastAPI and Streamlit."
)

st.divider()

st.subheader("🛒 Product")

st.write("Premium Course")
st.write("Learn Python, FastAPI and Generative AI.")

st.markdown("### Price: ₹500")

if st.button("💰 Pay ₹500", use_container_width=True):

    try:
        response = requests.post(
            "https://payment-gateway-0jov.onrender.com/payment/create",
            json={
                "amount": 500,
                "currency": "INR"
            }
        )

        if response.status_code == 200:

            data = response.json()

            st.success("Payment order created!")

            st.write("Amount:", data["amount"], "paise")
            st.write("Currency:", data["currency"])

        else:
            st.error("Unable to create payment order.")

    except requests.exceptions.ConnectionError:
        st.error(
            "FastAPI backend is not running."
        )

st.divider()

st.caption(
    "Test payment application — no real payment is processed yet."
)