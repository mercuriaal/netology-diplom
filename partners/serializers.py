from rest_framework import serializers

from .models import Shop, Category, Product, ProductInfo, ProductParameter, Parameter


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ('id', 'name', 'state')
        read_only_fields = ('id', )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'special_id']
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'special_id']
        read_only_fields = ('id',)


class ProductInfoSerializer(serializers.ModelSerializer):

    shop = ShopSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['id', 'model', 'quantity', 'price', 'price_rrc', 'shop', 'product']
        read_only_fields = ('id',)


class ProductParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductParameter
        fields = ['id', 'value']
        read_only_fields = ('id',)


class ParameterSerializer(serializers.ModelSerializer):

    product_params = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = Parameter
        fields = ['id', 'name', 'product_params']
        read_only_fields = ('id',)
