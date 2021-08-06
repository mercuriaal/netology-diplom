from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ShopViewSet, CategoryView, upload_products, ProductView

partners_router = DefaultRouter()

partners_router.register('shop/', ShopViewSet, basename='shops')

urlpatterns = [
    path('upload/', upload_products, name='upload'),
    path('categories/', CategoryView, name='categories'),
    path('products/', ProductView, name='products')
]
