from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from clients.filters import ProductInfoFilter, ListOrderFilterBackEnd, PostOrderFilterBackEnd, BasketOwnerFilterBackEnd, \
    ListBasketFilterBackEnd
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
    filter_backends = [DjangoFilterBackend]


class BasketView(GenericViewSet, ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):

    permission_classes = [IsAuthenticated, Client]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if self.action in ['list']:
            queryset = Order.objects.all()
        else:
            queryset = OrderItem.objects.all()
        return queryset

    def filter_queryset(self, queryset):
        filter_backends = [BasketOwnerFilterBackEnd]

        if self.action in ['list']:
            filter_backends = [ListBasketFilterBackEnd]

        for backend in list(filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)

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


class OrderView(ListCreateAPIView):

    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, Client]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user.id)
        return queryset

    def filter_queryset(self, queryset):
        filter_backends = [ListOrderFilterBackEnd]

        if 'contact' in self.request.data:
            filter_backends = [PostOrderFilterBackEnd]

        for backend in list(filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)

        return queryset
