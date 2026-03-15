from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    status = Column(
        Enum("pending", "confirmed", "out_for_delivery", "delivered", "cancelled", name="order_status_enum"),
        default="pending",
        nullable=False,
    )
    payment_method = Column(
        Enum("cod", "online", name="payment_method_enum"),
        default="cod"
    )
    subtotal = Column(Numeric(10, 2), nullable=False)
    delivery_charge = Column(Numeric(8, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    snap_address = Column(Text, nullable=False)  # JSON snapshot
    snap_block_name = Column(String(100))
    snap_zone_name = Column(String(100))
    notes = Column(Text)
    razorpay_order_id = Column(String(100))
    razorpay_payment_id = Column(String(100))
    ordered_at = Column(DateTime, server_default=func.now())
    delivered_at = Column(DateTime)
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="orders")
    address = relationship("Address", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    return_request = relationship("ReturnRequest", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_image = Column(String(500))
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    line_total = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
