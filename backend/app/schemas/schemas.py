from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ─── AUTH ───────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

    @field_validator("email")
    @classmethod
    def gmail_only(cls, v):
        if not v.lower().endswith("@gmail.com"):
            raise ValueError("Only Gmail addresses are allowed")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, v):
        digits = v.replace("+", "").replace("-", "").replace(" ", "")
        if not digits.isdigit() or len(digits) < 10:
            raise ValueError("Invalid phone number")
        return v


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ─── BLOCKS ─────────────────────────────────────────────
class BlockCreate(BaseModel):
    name: str
    description: Optional[str] = None


class BlockOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class ZoneCreate(BaseModel):
    block_id: int
    zone_name: str
    delivery_charge: Decimal
    min_order_value: Decimal = Decimal("0")


class ZoneOut(BaseModel):
    id: int
    block_id: int
    zone_name: str
    delivery_charge: Decimal
    min_order_value: Decimal
    is_active: bool

    class Config:
        from_attributes = True


class ZoneUpdate(BaseModel):
    zone_name: Optional[str] = None
    delivery_charge: Optional[Decimal] = None
    min_order_value: Optional[Decimal] = None
    is_active: Optional[bool] = None


# ─── ADDRESSES ──────────────────────────────────────────
class AddressCreate(BaseModel):
    block_id: int
    zone_id: int
    label: Optional[str] = "Home"
    address_line1: str
    address_line2: Optional[str] = None
    landmark: Optional[str] = None
    pincode: Optional[str] = None
    is_default: bool = False


class AddressOut(BaseModel):
    id: int
    block_id: int
    zone_id: int
    label: Optional[str]
    address_line1: str
    address_line2: Optional[str]
    landmark: Optional[str]
    pincode: Optional[str]
    is_default: bool
    block: Optional[BlockOut]
    zone: Optional[ZoneOut]

    class Config:
        from_attributes = True


# ─── CATEGORIES ─────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str
    image_url: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = ""   # empty string = clear the image
    is_active: Optional[bool] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    image_url: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ─── PRODUCTS ───────────────────────────────────────────
class ProductCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    mrp: Optional[Decimal] = None
    stock_qty: int = 0
    unit: Optional[str] = None
    is_featured: bool = False


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    stock_qty: Optional[int] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    description: Optional[str]
    price: Decimal
    mrp: Optional[Decimal]
    stock_qty: int
    unit: Optional[str]
    return_policy: Optional[int] = None
    image_url: Optional[str]
    is_active: bool
    is_featured: bool
    category: Optional[CategoryOut]

    class Config:
        from_attributes = True


# ─── CART ────────────────────────────────────────────────
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductOut

    class Config:
        from_attributes = True


class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    subtotal: Decimal

    class Config:
        from_attributes = True


# ─── ORDERS ─────────────────────────────────────────────
class CheckoutRequest(BaseModel):
    address_id: int
    notes: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    unit_price: Decimal
    quantity: int
    line_total: Decimal

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    status: str
    payment_method: str
    subtotal: Decimal
    delivery_charge: Decimal
    total_amount: Decimal
    snap_address: str
    snap_block_name: Optional[str]
    snap_zone_name: Optional[str]
    notes: Optional[str]
    ordered_at: Optional[datetime]
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str


# ─── REVIEWS ─────────────────────────────────────────────
class ReviewCreate(BaseModel):
    product_id: int
    order_id: int
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str]
    created_at: Optional[datetime]
    user: Optional[UserOut]

    class Config:
        from_attributes = True


# ─── RETURNS ─────────────────────────────────────────────
class ReturnRequestCreate(BaseModel):
    reason: str


class ReturnStatusUpdate(BaseModel):
    status: str
    admin_note: Optional[str] = None


class ReturnRequestOut(BaseModel):
    id: int
    order_id: int
    reason: str
    status: str
    admin_note: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── DELIVERY ────────────────────────────────────────────
class DeliveryCalcOut(BaseModel):
    is_deliverable: bool
    delivery_charge: Decimal
    zone_name: Optional[str]
    free_delivery_above: Optional[Decimal]
    message: str


# ─── ADMIN DASHBOARD ─────────────────────────────────────
class DashboardOut(BaseModel):
    total_orders: int
    total_revenue: Decimal
    pending_orders: int
    total_products: int
    top_products: List[dict]
