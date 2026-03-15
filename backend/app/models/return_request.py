from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class ReturnRequest(Base):
    __tablename__ = "order_returns"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(
        Enum(
            "return_requested",
            "return_approved",
            "return_rejected",
            "return_picked_up",
            "return_completed",
            name="return_status_enum",
        ),
        default="return_requested",
        nullable=False,
    )
    admin_note = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    order = relationship("Order", back_populates="return_request")
    user = relationship("User")
