from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Router, Status
from ninja.pagination import paginate

from api.schemas import ItemCreateOut
from ecommapp.models import Category

router = Router(tags=["categories"])


class CategoryIn(ModelSchema):
    class Meta:
        model = Category
        fields = ["name", "parent"]


class CategoryOut(ModelSchema):
    class Meta:
        model = Category
        fields = ["id", "name", "parent"]


@router.get("/", response=list[CategoryOut])
@paginate
def list_categories(request: HttpRequest):
    return Category.objects.all()


@router.get("/{category_id}", response=CategoryOut)
def get_category(request: HttpRequest, category_id: int):
    return get_object_or_404(Category, id=category_id)


@router.post("/", response={201: ItemCreateOut})
def create_category(request: HttpRequest, payload: CategoryIn):
    category = Category.objects.create(**payload.dict())
    return Status(201, ItemCreateOut(id=category.pk))


@router.put("/{category_id}")
def update_category(request: HttpRequest, category_id: int, payload: CategoryIn):
    category = get_object_or_404(Category, id=category_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(category, attr, value)
    category.save()

    return Status(204, None)


@router.delete("/{category_id}")
def delete_category(request: HttpRequest, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    category.delete()

    return Status(204, None)
