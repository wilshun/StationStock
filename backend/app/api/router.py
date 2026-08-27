from fastapi import APIRouter

from app.api.routes.alerts import router as alerts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.categories import router as categories_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.inventory_counts import router as inventory_counts_router
from app.api.routes.products import router as products_router
from app.api.routes.users import router as users_router
from app.api.routes.vendors import router as vendors_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(categories_router)
api_router.include_router(vendors_router)
api_router.include_router(products_router)
api_router.include_router(inventory_counts_router)
api_router.include_router(alerts_router)
api_router.include_router(dashboard_router)
