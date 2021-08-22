from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from clients.filters import ProductInfoFilter, ListOrderFilterBackEnd, PostOrderFilterBackEnd, BasketOwnerFilterBackEnd, \
    ListBasketFilterBackEnd
from clients.models import OrderItem, Order
from clients.serializers import OrderSerializer, OrderItemSerializer, OrderItemUpdateSerializer, CreateOrderSerializer
from partners.models import ProductInfo
from partners.serializers import ProductInfoSerializer
from users.permissions import Client
from users.signals import new_order, order_confirmation


class ProductInfoView(ListAPIView):

    """
    Класс для просмотра актуальных товаров покупателями
    """

    queryset = ProductInfo.objects.filter(shop__state=True).select_related(
        'shop', 'product__category').prefetch_related(
        'product_parameters__parameter').distinct()

    serializer_class = ProductInfoSerializer
    permission_classes = [IsAuthenticated, Client]
    authentication_classes = [TokenAuthentication]
    filterset_class = ProductInfoFilter
    filter_backends = [DjangoFilterBackend]


class BasketView(GenericViewSet, ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):

    """
    Класс для просмотра корзины и добавления в неё товаров
    """

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
        basket, created = Order.objects.get_or_create(user_id=request.user.id, state='basket')
        _mutable = self.request.data._mutable
        self.request.data._mutable = True
        self.request.data['order'] = basket.id
        self.request.data._mutable = _mutable
        return super().create(request, *args, **kwargs)


class OrderView(GenericViewSet, ListModelMixin, UpdateModelMixin):

    """
    Класс для просмотра и оформления заказов покупателями
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, Client]
    filter_backends = [ListOrderFilterBackEnd]

    def get_queryset(self):
        queryset = Order.objects.filter(user_id=self.request.user.id)
        return queryset

    def filter_queryset(self, queryset):
        filter_backends = [ListOrderFilterBackEnd]

        if self.action in ['update', 'partial_update']:
            filter_backends = [PostOrderFilterBackEnd]

        for backend in list(filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)

        return queryset

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CreateOrderSerializer
        return OrderSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.get_queryset().update(state='new')
        new_order.send(sender=self.__class__, user_id=request.user.id)
        order_confirmation.send(sender=self.__class__, user_id=request.user.id)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


