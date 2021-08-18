from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProductInfoView, BasketView, OrderView

client_router = DefaultRouter()

client_router.register('basket', BasketView, basename='basket')
client_router.register('orders', OrderView, basename='orders')

urlpatterns = [
    path('product_info/', ProductInfoView.as_view(), name='productinfo')
]
