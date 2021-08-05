from rest_framework import serializers

from .models import Shop
from users.serializers import AccountSerializer


class ShopSerializer(serializers.ModelSerializer):

    user = AccountSerializer(read_only=True)

    class Meta:
        model = Shop
        fields = ['user', 'name', 'file']

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
