from rest_framework import serializers

from .models import Shop, Category, Product, ProductInfo
from users.serializers import AccountSerializer


class ShopSerializer(serializers.ModelSerializer):

    user = AccountSerializer(read_only=True)

    class Meta:
        model = Shop
        fields = ['user', 'name', 'file']

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        user = self.context["request"].user
        shop_name = data.get('name')
        check_user_duplicate = Shop.objects.filter(user=user)
        check_name_duplicate = Shop.objecta.filter(name=shop_name)
        if any([check_user_duplicate.exists(), check_name_duplicate.exists()]):
            raise serializers.ValidationError('Магазин с данным пользователем или именем уже существует.')
        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['name', 'special_id']


class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'category', 'special_id']


class ProductInfoSerializer(serializers.ModelSerializer):

    shop = ShopSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['model', 'quantity', 'price', 'price_rrc', 'shop', 'product']
