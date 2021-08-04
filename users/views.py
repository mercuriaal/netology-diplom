from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .serializers import RegisterSerializer


@api_view(['POST'])
def registration_view(request):

    serializer = RegisterSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        user = serializer.save()
        data['response'] = 'Пользователь успешно создан'
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['email'] = user.email
        token = Token.objects.get(user=user).key
        data['token'] = token
    else:
        data = serializer.errors
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logout_view(request):

    request.user.auth_token.delete()
    return Response('Пользователь успешно вышел из системы')
