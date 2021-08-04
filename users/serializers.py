from rest_framework import serializers

from .models import Account


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
