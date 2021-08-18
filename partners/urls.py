from django.urls import path


from .views import PartnerStateView, UploadProduct, PartnerOrders

urlpatterns = [
    path('upload/', UploadProduct.as_view(), name='upload'),
    path('shop/', PartnerStateView.as_view(), name='shop'),
    path('shop/<int:pk>', PartnerStateView.as_view(), name='shop'),
    path('order/', PartnerOrders.as_view(), name='order')
]
