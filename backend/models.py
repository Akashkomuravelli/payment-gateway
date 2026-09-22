from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from .database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(String, unique=True, nullable=True)
    payment_id = Column(String, unique=True, nullable=True)

    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")

    status = Column(String, default="created")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )