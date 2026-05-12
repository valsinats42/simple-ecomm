from django.contrib import admin
from django.utils.html import format_html

from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_tag', 'sku', 'title', 'price', 'category')
    list_display_links = ('image_tag', 'sku', 'title',)

    @admin.display(description="Image")
    def image_tag(self, obj):
        return format_html(
            '<img src="{}" width="50" height="50" style="object-fit: contain;" />',
            obj.image.url if obj.image else '#')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')
    list_display_links = ('id', 'name')


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
