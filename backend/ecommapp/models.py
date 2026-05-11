from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='products',
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        primary_key=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.title} ({self.sku})"

