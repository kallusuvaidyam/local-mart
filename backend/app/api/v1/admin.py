from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, case, Date, distinct
from typing import Optional
from datetime import datetime, timedelta, date, timezone
from app.db.database import get_db
from app.core.dependencies import get_current_admin
from app.models.order import Order, OrderItem
from app.models.return_request import ReturnRequest
from app.models.product import Product
from app.models.user import User
from app.schemas.schemas import OrderStatusUpdate, ReturnStatusUpdate
from app.services.email_service import send_status_update_to_customer

router = APIRouter(prefix="/admin", tags=["Admin"])

VALID_TRANSITIONS = {
    "pending":          ["confirmed", "cancelled"],
    "confirmed":        ["out_for_delivery", "cancelled"],
    "out_for_delivery": ["delivered"],
    "delivered":        [],
    "cancelled":        [],
}
NOTIFY_STATUSES = ["confirmed", "out_for_delivery", "delivered", "cancelled"]

RETURN_TRANSITIONS = {
    "return_requested": ["return_approved", "return_rejected"],
    "return_approved":  ["return_picked_up"],
    "return_picked_up": ["return_completed"],
    "return_rejected":  [],
    "return_completed": [],
}


# ── DASHBOARD (enhanced) ─────────────────────────────────
@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _=Depends(get_current_admin)):

    # Basic counts
    total_orders   = db.query(Order).count()
    total_users    = db.query(User).filter(User.role == "customer").count()
    total_products = db.query(Product).filter(Product.is_active == True).count()

    # Revenue
    revenue_row    = db.query(func.sum(Order.total_amount)).filter(Order.status == "delivered").scalar()
    total_revenue  = float(revenue_row or 0)

    # Orders by status
    status_counts = {}
    for row in db.query(Order.status, func.count(Order.id)).group_by(Order.status).all():
        status_counts[row[0]] = row[1]

    # Users who placed at least 1 order
    users_with_orders = db.query(func.count(distinct(Order.user_id))).scalar()

    # New users last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    new_users_7d   = db.query(User).filter(
        User.role == "customer",
        User.created_at >= seven_days_ago
    ).count()

    # Orders last 7 days (single query instead of 14)
    seven_days_start = date.today() - timedelta(days=6)
    day_rows = (
        db.query(
            cast(Order.ordered_at, Date).label("day"),
            func.count(Order.id).label("count"),
            func.sum(case((Order.status != "cancelled", Order.total_amount), else_=0)).label("revenue"),
        )
        .filter(cast(Order.ordered_at, Date) >= seven_days_start)
        .group_by(cast(Order.ordered_at, Date))
        .all()
    )
    day_map = {row.day: {"orders": row.count, "revenue": float(row.revenue or 0)} for row in day_rows}
    orders_by_day = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        info = day_map.get(d, {"orders": 0, "revenue": 0})
        orders_by_day.append({
            "date":    d.strftime("%d %b"),
            "orders":  info["orders"],
            "revenue": info["revenue"],
        })

    # Top products
    top_products = (
        db.query(
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.line_total).label("revenue"),
        )
        .group_by(OrderItem.product_id, OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5).all()
    )

    # Recent 5 orders
    recent_orders = (
        db.query(Order)
        .order_by(Order.ordered_at.desc())
        .limit(5).all()
    )

    return {
        # Stats
        "total_orders":      total_orders,
        "total_users":       total_users,
        "total_products":    total_products,
        "total_revenue":     total_revenue,
        "users_with_orders": users_with_orders,
        "new_users_7d":      new_users_7d,

        # Status breakdown
        "status_counts": {
            "pending":          status_counts.get("pending", 0),
            "confirmed":        status_counts.get("confirmed", 0),
            "out_for_delivery": status_counts.get("out_for_delivery", 0),
            "delivered":        status_counts.get("delivered", 0),
            "cancelled":        status_counts.get("cancelled", 0),
        },

        # Charts
        "orders_by_day": orders_by_day,

        # Tables
        "top_products": [
            {"name": t.product_name, "sold": int(t.total_sold), "revenue": float(t.revenue)}
            for t in top_products
        ],
        "recent_orders": [
            {
                "id":           o.id,
                "user_name":    o.user.name if o.user else "",
                "user_phone":   o.user.phone if o.user else "",
                "total_amount": float(o.total_amount),
                "status":       o.status,
                "payment_method": o.payment_method,
                "ordered_at":   o.ordered_at.isoformat() if o.ordered_at else None,
            }
            for o in recent_orders
        ],
    }


# ── USER ANALYTICS ───────────────────────────────────────
@router.get("/users")
def get_all_users(
    page:   int = Query(1, ge=1),
    limit:  int = Query(20),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    q = db.query(User).filter(User.role == "customer")
    if search:
        q = q.filter(
            User.name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            User.phone.ilike(f"%{search}%")
        )
    total = q.count()
    users = q.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    user_ids = [u.id for u in users]

    # Single aggregated query instead of 3 queries per user (N+1 fix)
    order_stats = {}
    if user_ids:
        stats_rows = (
            db.query(
                Order.user_id,
                func.count(Order.id).label("order_count"),
                func.sum(
                    case((Order.status == "delivered", Order.total_amount), else_=0)
                ).label("total_spent"),
                func.max(Order.ordered_at).label("last_order_at"),
            )
            .filter(Order.user_id.in_(user_ids))
            .group_by(Order.user_id)
            .all()
        )
        for row in stats_rows:
            order_stats[row.user_id] = {
                "order_count":  row.order_count or 0,
                "total_spent":  float(row.total_spent or 0),
                "last_order_at": row.last_order_at.isoformat() if row.last_order_at else None,
            }

    result = []
    for u in users:
        s = order_stats.get(u.id, {})
        result.append({
            "id":           u.id,
            "name":         u.name,
            "email":        u.email,
            "phone":        u.phone,
            "is_active":    u.is_active,
            "joined_at":    u.created_at.isoformat() if u.created_at else None,
            "order_count":  s.get("order_count", 0),
            "total_spent":  s.get("total_spent", 0),
            "last_order_at": s.get("last_order_at"),
        })

    return {"total": total, "users": result}


# ── ORDER ANALYTICS ──────────────────────────────────────
@router.get("/analytics/orders")
def order_analytics(
    from_date: Optional[str] = Query(None),  # YYYY-MM-DD
    to_date:   Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    q = db.query(Order)
    if from_date:
        q = q.filter(Order.ordered_at >= datetime.strptime(from_date, "%Y-%m-%d"))
    if to_date:
        q = q.filter(Order.ordered_at <= datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1))

    orders = q.order_by(Order.ordered_at.desc()).all()

    # Group by date
    by_date = {}
    for o in orders:
        d = o.ordered_at.strftime("%Y-%m-%d") if o.ordered_at else "unknown"
        if d not in by_date:
            by_date[d] = {"date": d, "count": 0, "revenue": 0, "orders": []}
        by_date[d]["count"] += 1
        if o.status != "cancelled":
            by_date[d]["revenue"] += float(o.total_amount)
        by_date[d]["orders"].append({
            "id":           o.id,
            "user_name":    o.user.name if o.user else "",
            "user_phone":   o.user.phone if o.user else "",
            "status":       o.status,
            "total_amount": float(o.total_amount),
            "payment_method": o.payment_method,
            "ordered_at":   o.ordered_at.isoformat() if o.ordered_at else None,
        })

    return {
        "total_orders":  len(orders),
        "total_revenue": sum(float(o.total_amount) for o in orders if o.status != "cancelled"),
        "by_date":       sorted(by_date.values(), key=lambda x: x["date"], reverse=True),
    }


# ── ORDERS LIST ──────────────────────────────────────────
@router.get("/orders")
def get_all_orders(
    status: Optional[str] = Query(None),
    page:   int = Query(1, ge=1),
    limit:  int = Query(20),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    q = db.query(Order).order_by(Order.ordered_at.desc())
    if status:
        q = q.filter(Order.status == status)
    total  = q.count()
    orders = q.offset((page - 1) * limit).limit(limit).all()

    result = []
    for o in orders:
        result.append({
            "id":             o.id,
            "user_id":        o.user_id,
            "user_name":      o.user.name if o.user else "",
            "user_phone":     o.user.phone if o.user else "",
            "status":         o.status,
            "total_amount":   float(o.total_amount),
            "delivery_charge":float(o.delivery_charge),
            "snap_block_name":o.snap_block_name,
            "snap_zone_name": o.snap_zone_name,
            "snap_address":   o.snap_address,
            "payment_method": o.payment_method,
            "notes":          o.notes,
            "ordered_at":     o.ordered_at.isoformat() if o.ordered_at else None,
            "item_count":     len(o.items),
            "allowed_next":   VALID_TRANSITIONS.get(o.status, []),
        })
    return {"total": total, "page": page, "orders": result}


@router.get("/orders/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    return {
        "id": order.id,
        "user": {"id": order.user.id, "name": order.user.name, "phone": order.user.phone, "email": order.user.email},
        "status":           order.status,
        "payment_method":   order.payment_method,
        "subtotal":         float(order.subtotal),
        "delivery_charge":  float(order.delivery_charge),
        "total_amount":     float(order.total_amount),
        "snap_address":     order.snap_address,
        "snap_block_name":  order.snap_block_name,
        "snap_zone_name":   order.snap_zone_name,
        "notes":            order.notes,
        "ordered_at":       order.ordered_at.isoformat() if order.ordered_at else None,
        "allowed_next":     VALID_TRANSITIONS.get(order.status, []),
        "items": [
            {
                "product_name":  i.product_name,
                "product_image": i.product_image,
                "unit_price":    float(i.unit_price),
                "quantity":      i.quantity,
                "line_total":    float(i.line_total),
            }
            for i in order.items
        ],
    }


@router.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    allowed = VALID_TRANSITIONS.get(order.status, [])
    if data.status not in allowed:
        if not allowed:
            raise HTTPException(400, f"Order is in final state: '{order.status}'. No further updates.")
        raise HTTPException(400, f"Cannot move '{order.status}' → '{data.status}'. Allowed: {allowed}")

    old_status   = order.status
    order.status = data.status
    if data.status == "delivered":
        order.delivered_at = datetime.now(timezone.utc)
    db.commit()

    if data.status in NOTIFY_STATUSES:
        customer = db.query(User).filter(User.id == order.user_id).first()
        if customer:
            background_tasks.add_task(
                send_status_update_to_customer,
                customer_email=customer.email,
                customer_name=customer.name,
                order_id=order.id,
                new_status=data.status,
                total=float(order.total_amount),
            )

    return {
        "message":      f"Order #{order_id}: {old_status} → {data.status}",
        "allowed_next": VALID_TRANSITIONS.get(data.status, []),
    }


# ── RETURNS LIST ──────────────────────────────────────────
@router.get("/returns")
def get_all_returns(
    status: Optional[str] = Query(None),
    page:   int = Query(1, ge=1),
    limit:  int = Query(20),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    q = db.query(ReturnRequest).order_by(ReturnRequest.created_at.desc())
    if status:
        q = q.filter(ReturnRequest.status == status)
    total   = q.count()
    returns = q.offset((page - 1) * limit).limit(limit).all()

    result = []
    for r in returns:
        order = r.order
        result.append({
            "id":           r.id,
            "order_id":     r.order_id,
            "user_name":    r.user.name if r.user else "",
            "user_phone":   r.user.phone if r.user else "",
            "reason":       r.reason,
            "status":       r.status,
            "admin_note":   r.admin_note,
            "total_amount": float(order.total_amount) if order else 0,
            "created_at":   r.created_at.isoformat() if r.created_at else None,
            "allowed_next": RETURN_TRANSITIONS.get(r.status, []),
        })
    return {"total": total, "returns": result}


# ── RETURN STATUS UPDATE ──────────────────────────────────
@router.patch("/returns/{return_id}/status")
def update_return_status(
    return_id: int,
    data: ReturnStatusUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    ret = db.query(ReturnRequest).filter(ReturnRequest.id == return_id).first()
    if not ret:
        raise HTTPException(404, "Return request not found")

    allowed = RETURN_TRANSITIONS.get(ret.status, [])
    if data.status not in allowed:
        if not allowed:
            raise HTTPException(400, f"Return is in final state: '{ret.status}'.")
        raise HTTPException(400, f"Cannot move '{ret.status}' → '{data.status}'. Allowed: {allowed}")

    old_status = ret.status
    ret.status = data.status
    if data.admin_note is not None:
        ret.admin_note = data.admin_note
    db.commit()

    return {
        "message":      f"Return #{return_id}: {old_status} → {data.status}",
        "allowed_next": RETURN_TRANSITIONS.get(data.status, []),
    }
