import pytest
from rest_framework.test import APIClient
from model_bakery import baker


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def user_factory():
    def factory(**kwargs):
        return baker.make("Account", **kwargs)
    return factory


@pytest.fixture()
def contact_factory():
    def factory(**kwargs):
        return baker.make("Contact", **kwargs)

    return factory


@pytest.fixture()
def shop_factory():
    def factory(**kwargs):
        return baker.make("Shop", **kwargs)

    return factory


@pytest.fixture()
def order_factory():
    def factory(**kwargs):
        return baker.make("Order", **kwargs)

    return factory


@pytest.fixture()
def product_factory():
    def factory(**kwargs):
        return baker.make("Product", **kwargs)

    return factory


@pytest.fixture()
def category_factory():
    def factory(**kwargs):
        return baker.make("Category", **kwargs)

    return factory


@pytest.fixture()
def product_info_factory():
    def factory(**kwargs):
        return baker.make("ProductInfo", **kwargs)

    return factory


@pytest.fixture()
def order_item_factory():
    def factory(**kwargs):
        return baker.make("OrderItem", **kwargs)

    return factory