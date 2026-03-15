from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.order import Order
from app.models.return_request import ReturnRequest
from app.models.user import User
from app.schemas.schemas import ReturnRequestCreate

router = APIRouter(prefix="/returns", tags=["Returns"])


@router.post("/{order_id}", status_code=201)
def request_return(
    order_id: int,
    data: ReturnRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "delivered":
        raise HTTPException(400, "Return can only be requested for delivered orders")

    # Return window check
    if order.delivered_at:
        deadline = order.delivered_at + timedelta(days=settings.RETURN_WINDOW_DAYS)
        if datetime.now(timezone.utc) > deadline.replace(tzinfo=timezone.utc):
            raise HTTPException(400, f"Return window of {settings.RETURN_WINDOW_DAYS} day(s) has expired")

    existing = db.query(ReturnRequest).filter(ReturnRequest.order_id == order_id).first()
    if existing:
        raise HTTPException(400, "Return request already submitted for this order")

    if not data.reason.strip():
        raise HTTPException(400, "Please provide a reason for return")

    ret = ReturnRequest(
        order_id=order_id,
        user_id=current_user.id,
        reason=data.reason.strip(),
    )
    db.add(ret)
    db.commit()
    db.refresh(ret)

    return {
        "message": "Return request submitted successfully",
        "return": _serialize(ret),
    }


@router.get("/{order_id}")
def get_return(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(404, "Order not found")

    ret = db.query(ReturnRequest).filter(ReturnRequest.order_id == order_id).first()
    if not ret:
        raise HTTPException(404, "No return request found")

    return _serialize(ret)


def _serialize(ret: ReturnRequest) -> dict:
    return {
        "id": ret.id,
        "order_id": ret.order_id,
        "reason": ret.reason,
        "status": ret.status,
        "admin_note": ret.admin_note,
        "created_at": ret.created_at.isoformat() if ret.created_at else None,
        "updated_at": ret.updated_at.isoformat() if ret.updated_at else None,
    }
