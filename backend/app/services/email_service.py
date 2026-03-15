import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str) -> bool:
    """
    Synchronous Gmail SMTP sender.
    Raises exception loudly so errors are visible in logs.
    """
    # ── Hard check — credentials missing hain to seedha error ──
    if not settings.MAIL_FROM or not settings.MAIL_PASSWORD:
        raise ValueError(
            "EMAIL NOT CONFIGURED: MAIL_FROM aur MAIL_PASSWORD .env mein set karo"
        )
    if not to:
        raise ValueError("Recipient email (to) empty hai")

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Local Mart <{settings.MAIL_FROM}>"
        msg["To"]      = to
        msg.attach(MIMEText(html_body, "html"))

        # SSL connection — timeout 15 seconds
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.set_debuglevel(0)
            server.login(settings.MAIL_FROM, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, to, msg.as_string())

        print(f"[EMAIL OK] Sent to {to} — {subject}")
        return True

    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "Gmail authentication failed. "
            "App Password galat hai ya 2-Step Verification off hai. "
            "https://myaccount.google.com/apppasswords"
        )
    except smtplib.SMTPException as e:
        raise RuntimeError(f"SMTP error: {e}")
    except Exception as e:
        raise RuntimeError(f"Email send failed: {e}")


# ─────────────────────────────────────────────────────────
# TEMPLATE 1 — Admin ko naya order alert
# ─────────────────────────────────────────────────────────
def send_new_order_alert_to_admin(
    order_id: int,
    customer_name: str,
    customer_phone: str,
    total: float,
    items: list,
    address: str,
    block_name: str,
    payment_method: str,
):
    items_rows = "".join([
        f"<tr>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #f0f0f0;'>{i['name']}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:center;'>{i['qty']}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:right;'>&#8377;{i['total']}</td>"
        f"</tr>"
        for i in items
    ])

    payment_badge = (
        "<span style='background:#dcfce7;color:#16a34a;padding:3px 10px;"
        "border-radius:99px;font-size:12px;'>&#128179; Online Paid</span>"
        if payment_method == "online"
        else "<span style='background:#fef9c3;color:#92400e;padding:3px 10px;"
             "border-radius:99px;font-size:12px;'>&#128181; Cash on Delivery</span>"
    )

    # Frontend URL
    frontend_url = settings.CORS_ORIGINS.split(",")[0].strip()

    html = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,sans-serif;">
<div style="max-width:560px;margin:30px auto;background:#fff;border-radius:12px;
            overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

  <div style="background:#2563eb;padding:24px 28px;">
    <h1 style="margin:0;color:#fff;font-size:22px;">&#128722; New Order Received!</h1>
    <p style="margin:6px 0 0;color:#bfdbfe;font-size:14px;">
      Order #{order_id} is waiting for your confirmation
    </p>
  </div>

  <div style="padding:24px 28px;">

    <div style="background:#f1f5f9;border-radius:8px;padding:14px 16px;margin-bottom:16px;">
      <p style="margin:0 0 4px;font-size:12px;color:#64748b;text-transform:uppercase;">Customer</p>
      <p style="margin:0;font-size:16px;font-weight:700;color:#1e293b;">{customer_name}</p>
      <p style="margin:4px 0 0;font-size:14px;color:#475569;">&#128222; {customer_phone}</p>
    </div>

    <div style="background:#f1f5f9;border-radius:8px;padding:14px 16px;margin-bottom:16px;">
      <p style="margin:0 0 4px;font-size:12px;color:#64748b;text-transform:uppercase;">Delivery Address</p>
      <p style="margin:0;font-size:14px;font-weight:600;color:#2563eb;">{block_name}</p>
      <p style="margin:4px 0 0;font-size:14px;color:#475569;">&#128205; {address}</p>
    </div>

    <table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
      <thead>
        <tr style="background:#f8fafc;">
          <th style="padding:8px 12px;text-align:left;font-size:12px;color:#64748b;
                     border-bottom:2px solid #e2e8f0;">ITEM</th>
          <th style="padding:8px 12px;text-align:center;font-size:12px;color:#64748b;
                     border-bottom:2px solid #e2e8f0;">QTY</th>
          <th style="padding:8px 12px;text-align:right;font-size:12px;color:#64748b;
                     border-bottom:2px solid #e2e8f0;">AMOUNT</th>
        </tr>
      </thead>
      <tbody>{items_rows}</tbody>
    </table>

    <div style="background:#eff6ff;border-radius:8px;padding:12px 16px;
                margin-bottom:12px;display:flex;justify-content:space-between;">
      <span style="font-weight:600;color:#1e293b;font-size:15px;">Total Amount</span>
      <span style="font-size:20px;font-weight:700;color:#2563eb;">&#8377;{total:.2f}</span>
    </div>

    <p style="margin:0 0 20px;">Payment: {payment_badge}</p>

    <a href="{frontend_url}/admin/orders"
       style="display:block;background:#2563eb;color:#fff;text-align:center;
              padding:14px;border-radius:8px;font-weight:700;text-decoration:none;
              font-size:15px;">
      &#128065; View &amp; Confirm Order in Admin Panel
    </a>
  </div>

  <div style="padding:14px;background:#f8fafc;text-align:center;">
    <p style="margin:0;font-size:12px;color:#94a3b8;">Local Mart Admin Notification</p>
  </div>
</div>
</body>
</html>"""

    send_email(
        to=settings.MAIL_ADMIN,
        subject=f"[LOCAL MART] New Order #{order_id} — {customer_name} — ₹{total:.2f}",
        html_body=html,
    )


# ─────────────────────────────────────────────────────────
# TEMPLATE 2 — Customer ko order confirmation
# ─────────────────────────────────────────────────────────
def send_order_confirmation_to_customer(
    customer_email: str,
    customer_name: str,
    order_id: int,
    total: float,
    items: list,
    address: str,
    payment_method: str,
    status: str = "pending",
):
    items_rows = "".join([
        f"<tr>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #f0f0f0;'>{i['name']}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:center;'>{i['qty']}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:right;'>&#8377;{i['total']}</td>"
        f"</tr>"
        for i in items
    ])

    frontend_url = settings.CORS_ORIGINS.split(",")[0].strip()

    html = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,sans-serif;">
<div style="max-width:560px;margin:30px auto;background:#fff;border-radius:12px;
            overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

  <div style="background:#2563eb;padding:24px 28px;">
    <h1 style="margin:0;color:#fff;font-size:22px;">&#128230; Order Received!</h1>
    <p style="margin:6px 0 0;color:#bfdbfe;font-size:14px;">Order #{order_id}</p>
  </div>

  <div style="padding:24px 28px;">
    <p style="color:#475569;font-size:15px;">
      Hi <strong>{customer_name}</strong>, your order has been received
      and is pending confirmation. We will update you shortly!
    </p>

    <table style="width:100%;border-collapse:collapse;margin:16px 0;">
      <thead>
        <tr style="background:#f8fafc;">
          <th style="padding:8px 12px;text-align:left;font-size:12px;color:#64748b;
                     border-bottom:2px solid #e2e8f0;">ITEM</th>
          <th style="padding:8px 12px;text-align:center;font-size:12px;color:#64748b;
                     border-bottom:2px solid #e2e8f0;">QTY</th>
          <th style="padding:8px 12px;text-align:right;font-size:12px;color:#64748b;
                     border-bottom:2px solid #e2e8f0;">AMOUNT</th>
        </tr>
      </thead>
      <tbody>{items_rows}</tbody>
    </table>

    <div style="background:#eff6ff;border-radius:8px;padding:12px 16px;margin-bottom:16px;">
      <div style="display:flex;justify-content:space-between;">
        <span style="font-weight:600;color:#1e293b;">Total</span>
        <span style="font-size:18px;font-weight:700;color:#2563eb;">&#8377;{total:.2f}</span>
      </div>
    </div>

    <div style="background:#f1f5f9;border-radius:8px;padding:12px 16px;margin-bottom:20px;">
      <p style="margin:0 0 4px;font-size:12px;color:#64748b;">DELIVERY ADDRESS</p>
      <p style="margin:0;font-size:14px;color:#1e293b;">&#128205; {address}</p>
    </div>

    <a href="{frontend_url}/orders/{order_id}"
       style="display:block;background:#2563eb;color:#fff;text-align:center;
              padding:13px;border-radius:8px;font-weight:700;text-decoration:none;
              font-size:15px;">
      Track Your Order &#8594;
    </a>
  </div>

  <div style="padding:14px;background:#f8fafc;text-align:center;">
    <p style="margin:0;font-size:12px;color:#94a3b8;">
      Thank you for shopping at Local Mart &#128722;
    </p>
  </div>
</div>
</body>
</html>"""

    send_email(
        to=customer_email,
        subject=f"[LOCAL MART] Order #{order_id} Received — ₹{total:.2f}",
        html_body=html,
    )


# ─────────────────────────────────────────────────────────
# TEMPLATE 3 — Customer ko status update
# ─────────────────────────────────────────────────────────
def send_status_update_to_customer(
    customer_email: str,
    customer_name: str,
    order_id: int,
    new_status: str,
    total: float,
):
    status_map = {
        "confirmed":          ("&#9989; Order Confirmed",       "#16a34a", "Your order has been confirmed and is being prepared!", "&#127881;"),
        "out_for_delivery":   ("&#128693; Out for Delivery",    "#7c3aed", "Your order is on the way! Get ready to receive it.",   "&#128757;"),
        "delivered":          ("&#127881; Order Delivered",     "#15803d", "Your order has been delivered. Enjoy!",                "&#128522;"),
        "cancelled":          ("&#10060; Order Cancelled",      "#dc2626", "Your order has been cancelled.",                       "&#128532;"),
    }

    title, color, message, emoji = status_map.get(
        new_status,
        ("&#128230; Order Update", "#2563eb", "Your order status has been updated.", "&#128203;")
    )

    frontend_url = settings.CORS_ORIGINS.split(",")[0].strip()

    html = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,sans-serif;">
<div style="max-width:480px;margin:30px auto;background:#fff;border-radius:12px;
            overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

  <div style="background:{color};padding:28px;text-align:center;">
    <p style="font-size:48px;margin:0;">{emoji}</p>
    <h1 style="margin:10px 0 0;color:#fff;font-size:20px;">{title}</h1>
  </div>

  <div style="padding:24px 28px;text-align:center;">
    <p style="color:#475569;font-size:15px;">Hi <strong>{customer_name}</strong>,</p>
    <p style="color:#475569;font-size:14px;line-height:1.7;">{message}</p>

    <div style="background:#f1f5f9;border-radius:8px;padding:14px 16px;
                margin:20px 0;text-align:left;">
      <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:13px;color:#64748b;">Order ID</span>
        <span style="font-size:13px;font-weight:700;">#{order_id}</span>
      </div>
      <div style="display:flex;justify-content:space-between;">
        <span style="font-size:13px;color:#64748b;">Total</span>
        <span style="font-size:14px;font-weight:700;color:#2563eb;">&#8377;{total:.2f}</span>
      </div>
    </div>

    <a href="{frontend_url}/orders/{order_id}"
       style="display:inline-block;background:#2563eb;color:#fff;padding:12px 32px;
              border-radius:8px;font-weight:700;text-decoration:none;font-size:14px;">
      View Order Details &#8594;
    </a>
  </div>

  <div style="padding:14px;background:#f8fafc;text-align:center;">
    <p style="margin:0;font-size:12px;color:#94a3b8;">
      Local Mart — Your Neighbourhood Store &#128722;
    </p>
  </div>
</div>
</body>
</html>"""

    send_email(
        to=customer_email,
        subject=f"[LOCAL MART] {title.replace('&#9989;','✅').replace('&#128693;','🚴').replace('&#127881;','🎉').replace('&#10060;','❌')} — Order #{order_id}",
        html_body=html,
    )
