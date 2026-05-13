from typing import Any
import secrets
import hashlib

from django.http import HttpRequest
from django.conf import settings
from ninja import NinjaAPI
from ninja.security import HttpBearer

from .categories import router as categories_router
from .products import router as products_router

try:
    secret_hash = settings.API_KEY_SHA256
except AttributeError:
    raise ValueError("Please set API_KEY_SHA256 in settings.py")


class AuthBearer(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Any | None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if secrets.compare_digest(secret_hash, token_hash):
            return token


auth = None if secret_hash is None else AuthBearer()

ninjaAPI = NinjaAPI(title="Simple ECommerce App Demo", auth=auth)
ninjaAPI.add_router("/categories", categories_router)
ninjaAPI.add_router("/products", products_router)
