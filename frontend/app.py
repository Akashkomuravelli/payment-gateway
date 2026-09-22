import streamlit as st

st.set_page_config(
    page_title="Akash Payment Gateway",
    page_icon="💳",
    layout="centered"
)

st.title("💳 Payment Gateway Demo")

st.write(
    "A payment application built using Python, "
    "FastAPI and Streamlit."
)

st.divider()

st.subheader("🛒 Product")

st.write("Premium Course")
st.write("Learn Python, FastAPI and Generative AI.")

st.markdown("### Price: ₹500")

if st.button("💰 Pay ₹500", use_container_width=True):
    st.info(
        "Payment checkout will be connected here."
    )

st.divider()

st.caption(
    "Test payment application — no real payment is processed yet."
)