from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import registration_view, logout_view, ContactViewSet
from rest_framework.authtoken.views import obtain_auth_token

contact_router = DefaultRouter()

contact_router.register('contact', ContactViewSet, basename='contact')

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('logout/', logout_view, name='logout')
]
