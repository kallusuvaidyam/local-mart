from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum("customer", "admin", name="user_role_enum"),
        default="customer",
        nullable=False
    )
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    verify_otp = Column(String(6), nullable=True)
    verify_otp_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
