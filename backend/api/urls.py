from ninja import NinjaAPI

from .categories import router as categories_router
from .products import router as products_router

ninjaAPI = NinjaAPI(title="Simple ECommerce App Demo")
ninjaAPI.add_router("/categories", categories_router)
ninjaAPI.add_router("/products", products_router)
