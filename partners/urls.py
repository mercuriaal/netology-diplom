from django.urls import path


from .views import PartnerStateView, upload_products, PartnerOrders

urlpatterns = [
    path('upload/', upload_products, name='upload'),
    path('shop/', PartnerStateView.as_view(), name='shop'),
    path('shop/<int:pk>', PartnerStateView.as_view(), name='shop'),
    path('order/', PartnerOrders.as_view(), name='order')
]
