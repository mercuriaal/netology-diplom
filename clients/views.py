from django.db.models import F, Sum
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from clients.filters import ProductInfoFilter
from clients.models import OrderItem, Order
from clients.serializers import OrderSerializer, OrderItemSerializer, OrderItemUpdateSerializer
from partners.models import ProductInfo
from partners.serializers import ProductInfoSerializer
from users.permissions import Client, Owner


class ProductInfoView(ListAPIView):

    queryset = ProductInfo.objects.filter(shop__state=True).select_related(
        'shop', 'product__category').prefetch_related(
        'product_parameters__parameter').distinct()

    serializer_class = ProductInfoSerializer
    permission_classes = [IsAuthenticated, Client]
    authentication_classes = [TokenAuthentication]
    filterset_class = ProductInfoFilter


class BasketView(GenericViewSet, ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):

    permission_classes = [IsAuthenticated, Client ]
    authentication_classes = [TokenAuthentication]
    queryset = OrderItem.objects.all()

    def get_queryset(self):
        if self.action in ['list']:
            queryset = Order.objects.filter(user_id=self.request.user.id, state='basket').prefetch_related(
                                            'ordered_items__product_info__product__category',
                                            'ordered_items__product_info__product_parameters__parameter').annotate(
                                            total_sum=Sum(F(
                                                'ordered_items__quantity') * F(
                                                'ordered_items__product_info__price'))).distinct()
        else:
            queryset = OrderItem.objects.filter(order__user=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list']:
            return OrderSerializer
        if self.action in ['update', 'partial_update']:
            return OrderItemUpdateSerializer
        return OrderItemSerializer

    def create(self, request, *args, **kwargs):
        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
        _mutable = self.request.data._mutable
        self.request.data._mutable = True
        self.request.data['order'] = basket.id
        self.request.data._mutable = _mutable
        return super().create(request, *args, **kwargs)


