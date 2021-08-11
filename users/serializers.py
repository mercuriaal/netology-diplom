from rest_framework import serializers

from .models import Account, Contact


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'email', 'company', 'position']
        read_only_fields = ('id',)


class ContactSerializer(serializers.ModelSerializer):

    user = AccountSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class RegisterSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'password', 'password2', 'company', 'position']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        user = Account(first_name=self.validated_data.get('first_name'), last_name=self.validated_data.get('last_name'),
                       email=self.validated_data.get('email'), company=self.validated_data.get('company'))
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError('Пароли не совпадают между собой')

        user.set_password(password)
        user.save()
        return user

    def validate(self, data):
        if not all([data.get('first_name'), data.get('last_name'), data.get('email'), data.get('company')]):
            raise serializers.ValidationError('Заполните необходимые данные для регистрации')
        return data
