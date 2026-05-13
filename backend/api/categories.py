from django.db.utils import IntegrityError
from django.db.models.deletion import ProtectedError
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Router, Status
from ninja.pagination import paginate

from api.schemas import ItemCreateOut, DetailError
from ecommapp.models import Category

router = Router(tags=["Categories"])


class CategoryIn(ModelSchema):
    parent_id: int | None = None
    class Meta:
        model = Category
        fields = ["name"]


class CategoryOut(ModelSchema):
    class Meta:
        model = Category
        fields = ["id", "name", "parent"]


@router.get("/", response=list[CategoryOut], auth=None)
@paginate
def list_categories(request: HttpRequest):
    return Category.objects.all()


@router.get("/{category_id}", response=CategoryOut, auth=None)
def get_category(request: HttpRequest, category_id: int):
    return get_object_or_404(Category, id=category_id)


@router.post("/", response={201: ItemCreateOut, 400: DetailError})
def create_category(request: HttpRequest, payload: CategoryIn):
    try:
        category = Category.objects.create(**payload.dict())
        return Status(201, ItemCreateOut(id=category.pk))
    except IntegrityError:
        return Status(400, DetailError(detail="Invalid parent ID"))


@router.patch("/{category_id}", response={204: None, 400: DetailError})
def update_category(request: HttpRequest, category_id: int, payload: CategoryIn):
    category = get_object_or_404(Category, id=category_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(category, attr, value)
    
    try:
        category.save()
        return Status(204, None)
    except IntegrityError:
        return Status(400, DetailError(detail="Invalid parent ID"))


@router.delete("/{category_id}", response={204: None, 400: DetailError})
def delete_category(request: HttpRequest, category_id: int):
    category = get_object_or_404(Category, id=category_id)

    try:
        category.delete()
        return Status(204, None)
    except ProtectedError as e:
        return Status(400, DetailError(detail="Cannot delete category as it is still referenced by other categories or products."))
