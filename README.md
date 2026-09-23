# 💳 Payment Gateway

A full-stack payment gateway application built with Python, FastAPI,
Streamlit, Razorpay Test Mode, and SQLite.

## 🚀 Features

- Create Razorpay payment orders
- Razorpay Test Mode integration
- Payment signature verification
- Payment status tracking
- Payment history
- SQLite database storage
- REST APIs using FastAPI
- Streamlit frontend
- Environment-based API credentials
- Cloud deployment using Render and Streamlit Community Cloud

## 🛠️ Technologies Used

- Python
- FastAPI
- Pydantic
- Streamlit
- Razorpay API
- SQLAlchemy
- SQLite
- REST API
- Git & GitHub
- Render

## 🏗️ Architecture

Customer
↓
Streamlit Frontend
↓
FastAPI Backend
↓
Razorpay
↓
Payment Verification
↓
SQLite Database
↓
Payment History

## 📁 Project Structure

payment-gateway/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   └── models.py
│
├── frontend/
│   └── app.py
│
├── requirements.txt
├── .gitignore
└── README.md

## 🔐 Security

- Razorpay credentials are stored using environment variables.
- API secrets are not committed to GitHub.
- Payment signatures are verified on the backend.
- Card numbers, CVV, and UPI PINs are not stored.

## 🧪 Testing

The project uses Razorpay Test Mode for payment testing.

A development-only test endpoint is used to verify the application's
database and payment-history workflow without processing real money.

## 🌐 Deployment

Backend:
Render

Frontend:
Streamlit Community Cloud

## 📌 Project Status

Completed as a payment gateway learning project using Razorpay Test Mode.
