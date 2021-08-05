from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ShopViewSet, upload_products

partners_router = DefaultRouter()

partners_router.register('shop/', ShopViewSet, basename='shops')

urlpatterns = [
    path('upload/', upload_products, name='upload')
]
