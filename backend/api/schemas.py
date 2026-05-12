from ninja import Schema


class ItemCreateOut(Schema):
    id: int


class FormError(Schema):
    message: str
    code: str


class FormErrorResponse(Schema):
    errors: dict[str, list[FormError]]
