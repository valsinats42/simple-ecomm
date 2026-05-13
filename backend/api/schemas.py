from ninja import Schema


class ItemCreateOut(Schema):
    id: int


class DetailError(Schema):
    detail: str


class FormError(Schema):
    message: str
    code: str


class FormErrorResponse(Schema):
    errors: dict[str, list[FormError]]
