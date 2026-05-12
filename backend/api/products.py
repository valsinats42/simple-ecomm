from decimal import Decimal
from typing import Annotated

from django import forms
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, FilterSchema, ModelSchema, Query, Router, Status
from ninja.files import UploadedFile
from ninja.pagination import paginate
from pydantic import Field

from api.schemas import FormErrorResponse, ItemCreateOut
from ecommapp.models import Product

router = Router(tags=["products"])


class ProductOut(ModelSchema):
    price: Decimal = Field(examples=["19.99"])

    class Meta:
        model = Product
        fields = ["id", "sku", "title", "description", "image", "category"]


class ProductIn(ModelSchema):
    category_id: int
    price: Decimal = Field(examples=["19.99"])

    class Meta:
        model = Product
        fields = ["sku", "title", "description"]


class ProductPatch(ModelSchema):
    category_id: int | None = None

    class Meta:
        model = Product
        fields = ["sku", "title", "description", "price"]
        fields_optional = "__all__"


class ProductFilter(FilterSchema):
    category_id: int | None = None
    sku__icontains: str | None = Field(None, alias="sku") 
    title__icontains: str | None = Field(None, alias="title")
    price__gte: float | None = Field(None, alias="price_min")
    price__lte: float | None = Field(None, alias="price_max")


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["image"]


@router.get("/", response=list[ProductOut], 
            summary="List, Search & Filter Products",
            auth=None)
@paginate
def list_products(request: HttpRequest, filters: Query[ProductFilter]):
    return filters.filter(Product.objects.all().select_related("category"))


@router.get("/{product_id}", response=ProductOut, auth=None)
def get_product(request: HttpRequest, product_id: int):
    return get_object_or_404(Product, pk=product_id)


@router.post("/", response={201: ItemCreateOut})
def create_product(request: HttpRequest, payload: ProductIn):
    product = Product.objects.create(**payload.dict())
    return Status(201, ItemCreateOut(id=product.pk))


@router.put("/{product_id}/image", response={200: ProductOut, 400: FormErrorResponse})
def set_product_image(
    request: HttpRequest,
    product_id: int,
    image: File[UploadedFile],
):
    product = get_object_or_404(Product, pk=product_id)

    form = ProductImageForm(files=request.FILES, instance=product)
    if not form.is_valid():
        return Status(400, FormErrorResponse(errors=form.errors.get_json_data()))

    form.save()

    return Status(200, product)


@router.put("/{product_id}", response=ProductOut)
def update_product(request: HttpRequest, product_id: int, payload: ProductPatch):
    product = get_object_or_404(Product, pk=product_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(product, attr, value)
    product.save()

    return product


@router.delete("/{product_id}")
def delete_product(request: HttpRequest, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()

    return Status(204, None)
