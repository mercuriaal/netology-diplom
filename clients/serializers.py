from rest_framework import serializers

from clients.models import OrderItem, Order
from partners.models import ProductInfo
from partners.serializers import ProductInfoSerializer
from users.serializers import ContactSerializer


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }

    def validate(self, data):

        product_quantity = ProductInfo.objects.filter(id=data['product_info'].id).get().quantity
        if data['quantity'] > product_quantity:
            raise serializers.ValidationError('Указанное количество превышает количество товара в магазине')
        return data


class OrderItemUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('quantity',)

    def validate(self, data):

        product_quantity = ProductInfo.objects.filter(id=self.instance.id).get().quantity
        if data['quantity'] > product_quantity:
            raise serializers.ValidationError('Указанное количество превышает количество товара в магазине')
        return data


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact',)
        read_only_fields = ('id',)


class CreateOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('contact',)

    def validate(self, data):
        if data.get('contact') is None:
            raise serializers.ValidationError('Для оформления заказа необходимы контакты')
        return data
