import json
import logging
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.address import Address
from app.models.user import User
from app.models.review import Review  # ✅ Import karo
from app.schemas.schemas import CheckoutRequest
from app.services.cart_service import get_or_create_cart, get_cart_subtotal
from app.services.delivery_service import calculate_delivery
from app.services.email_service import (
    send_new_order_alert_to_admin,
    send_order_confirmation_to_customer,
)

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger(__name__)


# ✅ user_id optional rakha — list view mein bhi kaam kare, detail mein bhi
def serialize_order(order: Order, reviewed_product_ids: set = None) -> dict:
    reviewed_product_ids = reviewed_product_ids or set()
    ret = order.return_request
    return_data = None
    if ret:
        return_data = {
            "id": ret.id,
            "reason": ret.reason,
            "status": ret.status,
            "admin_note": ret.admin_note,
            "created_at": ret.created_at.isoformat() if ret.created_at else None,
            "updated_at": ret.updated_at.isoformat() if ret.updated_at else None,
        }
    return {
        "id": order.id,
        "status": order.status,
        "payment_method": order.payment_method,
        "subtotal": float(order.subtotal),
        "delivery_charge": float(order.delivery_charge),
        "total_amount": float(order.total_amount),
        "snap_address": order.snap_address,
        "snap_block_name": order.snap_block_name,
        "snap_zone_name": order.snap_zone_name,
        "notes": order.notes,
        "ordered_at": order.ordered_at.isoformat() if order.ordered_at else None,
        "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
        "return_window_days": settings.RETURN_WINDOW_DAYS,
        "return_request": return_data,
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "product_name": i.product_name,
                "product_image": i.product_image,
                "unit_price": float(i.unit_price),
                "quantity": i.quantity,
                "line_total": float(i.line_total),
                "already_reviewed": i.product_id in reviewed_product_ids,
            }
            for i in order.items
        ],
    }


def _items_list(order_items) -> list:
    return [{"name": i.product_name, "qty": i.quantity, "total": float(i.line_total)}
            for i in order_items]


def _address_str(snap_json: str) -> str:
    try:
        a = json.loads(snap_json)
        parts = [
            a.get("address_line1", ""),
            a.get("address_line2", ""),
            f"Near {a['landmark']}" if a.get("landmark") else "",
            a.get("pincode", ""),
        ]
        return ", ".join(p for p in parts if p)
    except Exception:
        return "Address on file"


# ── CHECKOUT ─────────────────────────────────────────────
@router.post("/checkout", status_code=201)
def checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    address = db.query(Address).filter(
        Address.id == data.address_id,
        Address.user_id == current_user.id
    ).first()
    if not address:
        raise HTTPException(404, "Address not found")

    cart = get_or_create_cart(current_user.id, db)
    if not cart.items:
        raise HTTPException(400, "Cart is empty")

    subtotal       = get_cart_subtotal(cart)
    delivery_info  = calculate_delivery(data.address_id, subtotal, db)

    if not delivery_info["is_deliverable"]:
        raise HTTPException(400, delivery_info["message"])

    delivery_charge = delivery_info["delivery_charge"]
    total           = subtotal + delivery_charge

    snap = {
        "label":         address.label,
        "address_line1": address.address_line1,
        "address_line2": address.address_line2,
        "landmark":      address.landmark,
        "pincode":       address.pincode,
    }

    order = Order(
        user_id         = current_user.id,
        address_id      = address.id,
        subtotal        = subtotal,
        delivery_charge = delivery_charge,
        total_amount    = total,
        snap_address    = json.dumps(snap),
        snap_block_name = address.block.name if address.block else None,
        snap_zone_name  = address.zone.zone_name if address.zone else None,
        notes           = data.notes,
    )
    db.add(order)
    db.flush()

    for item in cart.items:
        oi = OrderItem(
            order_id      = order.id,
            product_id    = item.product_id,
            product_name  = item.product.name,
            product_image = item.product.image_url,
            unit_price    = item.product.price,
            quantity      = item.quantity,
            line_total    = Decimal(str(item.product.price)) * item.quantity,
        )
        item.product.stock_qty = max(0, item.product.stock_qty - item.quantity)
        db.add(oi)

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(order)

    # ── Emails ────────────────────────────────────────────
    items_list  = _items_list(order.items)
    address_str = _address_str(order.snap_address)

    try:
        send_new_order_alert_to_admin(
            order_id       = order.id,
            customer_name  = current_user.name,
            customer_phone = current_user.phone,
            total          = float(total),
            items          = items_list,
            address        = address_str,
            block_name     = order.snap_block_name or "",
            payment_method = "cod",
        )
        logger.info(f"Admin email sent for order #{order.id}")
    except Exception as e:
        logger.error(f"Admin email FAILED for order #{order.id}: {e}")

    try:
        send_order_confirmation_to_customer(
            customer_email = current_user.email,
            customer_name  = current_user.name,
            order_id       = order.id,
            total          = float(total),
            items          = items_list,
            address        = address_str,
            payment_method = "cod",
            status         = "pending",
        )
        logger.info(f"Customer email sent for order #{order.id}")
    except Exception as e:
        logger.error(f"Customer email FAILED for order #{order.id}: {e}")

    # ✅ Naya order mein koi review nahi hoga — empty set pass karo
    return {"message": "Order placed successfully", "order": serialize_order(order, set())}


# ── MY ORDERS ─────────────────────────────────────────────
@router.get("")
def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = (db.query(Order)
         .filter(Order.user_id == current_user.id)
         .order_by(Order.ordered_at.desc()))
    total  = q.count()
    orders = q.offset((page - 1) * limit).limit(limit).all()

    # ✅ Saare orders ke liye ek hi query mein reviewed products fetch karo
    order_ids = [o.id for o in orders]
    reviews = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.order_id.in_(order_ids),
    ).all()

    # { order_id: {product_id, product_id, ...} }
    reviewed_map: dict[int, set] = {}
    for r in reviews:
        reviewed_map.setdefault(r.order_id, set()).add(r.product_id)

    return {
        "total": total,
        "orders": [
            serialize_order(o, reviewed_map.get(o.id, set()))
            for o in orders
        ],
    }


# ── ORDER DETAIL ──────────────────────────────────────────
@router.get("/{order_id}")
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(404, "Order not found")

    # ✅ Is order ke reviewed products fetch karo
    reviewed_product_ids = {
        r.product_id
        for r in db.query(Review).filter(
            Review.user_id == current_user.id,
            Review.order_id == order_id,
        ).all()
    }

    return serialize_order(order, reviewed_product_ids)