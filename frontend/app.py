import streamlit as st
import requests

BACKEND_URL = "https://payment-gateway-backend-vmtw.onrender.com"
st.set_page_config(
    page_title="Payment Gateway",
    page_icon="💳",
    layout="centered"
)

st.title("💳 Payment Gateway")
st.caption("Razorpay Test Mode Payment System")

st.divider()

# -------------------------
# Product
# -------------------------

st.subheader("🎓 Premium Course")

st.write("Complete Python & Backend Development Course")

st.markdown("### ₹500")

st.divider()

# -------------------------
# Create Payment
# -------------------------

st.subheader("💰 Make Payment")

if st.button(
    "💳 Create Payment Order",
    use_container_width=True
):

    try:
        response = requests.post(
            f"{BACKEND_URL}/payment/create",
            json={
                "amount": 500,
                "currency": "INR"
            },
            timeout=30
        )

        if response.status_code == 200:

            data = response.json()

            order_id = data["order_id"]

            st.session_state["order_id"] = order_id

            st.success("Payment order created successfully!")

            st.code(order_id)

            checkout_url = (
                f"{BACKEND_URL}/checkout/{order_id}"
            )

            st.link_button(
                "💳 Open Razorpay Checkout",
                checkout_url,
                use_container_width=True
            )

        else:

            st.error("Failed to create payment order.")
            st.write(response.text)

    except Exception as e:

        st.error(
            f"Backend connection error: {e}"
        )


# -------------------------
# Development Test Payment
# -------------------------

st.divider()

st.subheader("🧪 Development Testing")

st.caption(
    "Use this only to test the database/payment-history flow."
)

if "order_id" in st.session_state:

    if st.button(
        "✅ Simulate Test Payment",
        use_container_width=True
    ):

        try:

            order_id = st.session_state["order_id"]

            response = requests.post(
                f"{BACKEND_URL}/payment/test-success/{order_id}",
                timeout=30
            )

            if response.status_code == 200:

                data = response.json()

                if data["status"] == "test_paid":

                    st.success(
                        "Development payment recorded successfully!"
                    )

                else:

                    st.error(
                        "Test payment failed."
                    )

            else:

                st.error(
                    "Unable to simulate payment."
                )

                st.write(response.text)

        except Exception as e:

            st.error(
                f"Error: {e}"
            )

else:

    st.info(
        "Create a payment order first."
    )


# -------------------------
# Payment History
# -------------------------

st.divider()

st.subheader("📜 Payment History")

if st.button(
    "🔄 Refresh Payment History",
    use_container_width=True
):

    try:

        response = requests.get(
            f"{BACKEND_URL}/payments",
            timeout=30
        )

        if response.status_code == 200:

            data = response.json()

            payments = data["payments"]

            if payments:

                st.dataframe(
                    payments,
                    use_container_width=True
                )

            else:

                st.info(
                    "No payments found."
                )

        else:

            st.error(
                "Unable to load payment history."
            )

    except Exception as e:

        st.error(
            f"Error: {e}"
        )