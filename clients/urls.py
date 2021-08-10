from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProductInfoView, BasketView

basket_router = DefaultRouter()

basket_router.register('basket', BasketView, basename='basket')

urlpatterns = [
    path('product_info/', ProductInfoView.as_view(), name='productinfo')
]
