from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from decimal import Decimal
import re
from app.db.database import get_db
from app.core.dependencies import get_current_admin
from app.core.cloudinary import upload_image
from app.models.category import Category
from app.models.product import Product
from app.schemas.schemas import CategoryCreate, CategoryOut, CategoryUpdate, ProductCreate, ProductUpdate, ProductOut

router = APIRouter(prefix="/products", tags=["Products"])
cat_router = APIRouter(prefix="/categories", tags=["Categories"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text


# ── CATEGORIES ──────────────────────────────────────────
@cat_router.get("", response_model=List[CategoryOut])
def get_categories(show_all: bool = False, db: Session = Depends(get_db)):
    q = db.query(Category)
    if not show_all:
        q = q.filter(Category.is_active == True)
    return q.all()


@cat_router.post("", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    slug = slugify(data.name)
    existing = db.query(Category).filter(Category.slug == slug).first()
    if existing:
        raise HTTPException(400, "Category with this name already exists")
    cat = Category(name=data.name, slug=slug, image_url=data.image_url)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@cat_router.put("/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    if data.name is not None:
        cat.name = data.name
        cat.slug = slugify(data.name)
    if data.image_url is not None:
        # empty string clears the image, any other value sets it
        cat.image_url = data.image_url if data.image_url != "" else None
    if data.is_active is not None:
        cat.is_active = data.is_active
    db.commit()
    db.refresh(cat)
    return cat


@cat_router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    cat.is_active = False
    db.commit()
    return {"message": "Category deactivated"}


# ── PRODUCTS ────────────────────────────────────────────
@router.get("", response_model=dict)
def get_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Product).filter(Product.is_active == True)
    if category:
        cat = db.query(Category).filter(Category.slug == category).first()
        if cat:
            q = q.filter(Product.category_id == cat.id)
    if search:
        q = q.filter(or_(Product.name.ilike(f"%{search}%"), Product.description.ilike(f"%{search}%")))
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    total = q.count()
    products = q.offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "products": [ProductOut.model_validate(p) for p in products],
    }


@router.get("/featured", response_model=List[ProductOut])
def get_featured(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_featured == True, Product.is_active == True).limit(10).all()


@router.get("/{slug}", response_model=ProductOut)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == slug, Product.is_active == True).first()
    if not product:
        raise HTTPException(404, "Product not found")
    return product


# ── ADMIN PRODUCT CRUD ───────────────────────────────────
@router.post("", response_model=ProductOut, status_code=201)
async def create_product(
    name: str = Form(...),
    category_id: int = Form(...),
    price: Decimal = Form(...),
    description: Optional[str] = Form(None),
    mrp: Optional[Decimal] = Form(None),
    stock_qty: int = Form(0),
    unit: Optional[str] = Form(None),
    is_featured: bool = Form(False),
    return_policy: Optional[int] = Form(2),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    slug = slugify(name)
    counter = 0
    base_slug = slug
    while db.query(Product).filter(Product.slug == slug).first():
        counter += 1
        slug = f"{base_slug}-{counter}"

    image_url = None
    if image:
        contents = await image.read()
        image_url = upload_image(contents, folder="products")

    product = Product(
        name=name, slug=slug, category_id=category_id, price=price,
        description=description, mrp=mrp, stock_qty=stock_qty,
        unit=unit, is_featured=is_featured, return_policy=return_policy,
        image_url=image_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    price: Optional[Decimal] = Form(None),
    description: Optional[str] = Form(None),
    mrp: Optional[Decimal] = Form(None),
    stock_qty: Optional[int] = Form(None),
    unit: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    is_featured: Optional[bool] = Form(None),
    return_policy: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    if name: product.name = name
    if category_id: product.category_id = category_id
    if price is not None: product.price = price
    if description is not None: product.description = description
    if mrp is not None: product.mrp = mrp
    if stock_qty is not None: product.stock_qty = stock_qty
    if unit is not None: product.unit = unit
    if is_active is not None: product.is_active = is_active
    if return_policy is not None: product.return_policy = return_policy
    if is_featured is not None: product.is_featured = is_featured
    if image:
        contents = await image.read()
        product.image_url = upload_image(contents, folder="products")

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    product.is_active = False
    db.commit()
    return {"message": "Product deactivated"}
