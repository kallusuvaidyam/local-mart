from fastapi import APIRouter
from app.api.v1 import auth, products, cart, orders, blocks, addresses, reviews, admin, delivery, payments, returns

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(products.cat_router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
api_router.include_router(blocks.router)
api_router.include_router(addresses.router)
api_router.include_router(reviews.router)
api_router.include_router(admin.router)
api_router.include_router(delivery.router)
api_router.include_router(payments.router)
api_router.include_router(returns.router)
