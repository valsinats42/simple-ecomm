from decimal import Decimal

from django.test import TestCase

from ecommapp.models import Category, Product


class ProductSearchTests(TestCase):
    endpoint = "/api/v1/products/"

    @classmethod
    def setUpTestData(cls):
        cls.clothing = Category.objects.create(name="Clothing")
        cls.electronics = Category.objects.create(name="Electronics")

        cls.shirt = Product.objects.create(
            sku="TSHIRT-001",
            title="Cotton T-Shirt",
            description="Soft cotton shirt",
            price=Decimal("19.99"),
            category=cls.clothing,
        )
        cls.hoodie = Product.objects.create(
            sku="HOODIE-001",
            title="Zip Hoodie",
            description="Warm zip hoodie",
            price=Decimal("49.99"),
            category=cls.clothing,
        )
        cls.headphones = Product.objects.create(
            sku="AUDIO-001",
            title="Wireless Headphones",
            description="Bluetooth over-ear headphones",
            price=Decimal("89.99"),
            category=cls.electronics,
        )

    def get_items(self, query_params=None):
        response = self.client.get(self.endpoint, query_params or {})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("items", payload)
        self.assertIn("count", payload)
        return payload

    def assert_returned_skus(self, query_params, expected_skus):
        payload = self.get_items(query_params)

        self.assertEqual(payload["count"], len(expected_skus))
        self.assertEqual(
            {item["sku"] for item in payload["items"]},
            set(expected_skus),
        )

    def test_search_products_filters_by_sku_case_insensitively(self):
        self.assert_returned_skus(
            {"sku": "hoodie"},
            ["HOODIE-001"],
        )

    def test_search_products_filters_by_title_case_insensitively(self):
        self.assert_returned_skus(
            {"title": "shirt"},
            ["TSHIRT-001"],
        )

    def test_search_products_filters_by_category(self):
        self.assert_returned_skus(
            {"category_id": self.clothing.pk},
            ["TSHIRT-001", "HOODIE-001"],
        )

    def test_search_products_filters_by_price_range(self):
        self.assert_returned_skus(
            {"price_min": "20.00", "price_max": "90.00"},
            ["HOODIE-001", "AUDIO-001"],
        )

    def test_search_products_combines_filters(self):
        self.assert_returned_skus(
            {
                "category_id": self.clothing.pk,
                "price_max": "30.00",
            },
            ["TSHIRT-001"],
        )

    def test_search_products_returns_paginated_response(self):
        payload = self.get_items({"limit": 2, "offset": 0})

        self.assertEqual(payload["count"], 3)
        self.assertEqual(len(payload["items"]), 2)
