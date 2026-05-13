from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    image = models.ImageField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        db_index=True,
    )

    def __str__(self):
        return f"{self.title} ({self.sku})"
