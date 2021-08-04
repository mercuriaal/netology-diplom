import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from users.models import Account


@pytest.mark.parametrize(
    ["email", "password", "password2", "http_response", "instance_count"],
    (
        ("test@test.com", "password", "password", status.HTTP_200_OK, 2),
        ("test@test.com", "password", "passwords", status.HTTP_400_BAD_REQUEST, 1),
        ("existing@email.com", "password", "password", status.HTTP_200_OK, 1),
    )
)
@pytest.mark.django_db
def test_registration(api_client, user_factory, email, password, password2, http_response, instance_count):
    user = user_factory(email='existing@email.com')
    url = reverse('register')
    payload = {
        "first_name": 'test_name',
        "last_name": 'test_last_name',
        "email": email,
        "company": 'test_company',
        "position": 'test_position',
        "password": password,
        "password2": password2
    }

    response = api_client.post(url, payload, format='json')
    assert response.status_code == http_response
    assert Account.objects.count() == instance_count


@pytest.mark.parametrize(
    ["email", "password", "http_response", "expected_token_count"],
    (
        ("test@test.com", "test_password", status.HTTP_200_OK, 1),
        ("test@test.com", "wrong_password", status.HTTP_400_BAD_REQUEST, 0),
        ("wring@email.com", "password", status.HTTP_400_BAD_REQUEST, 0),
    )
)
@pytest.mark.django_db
def test_login(api_client, email, password, http_response, expected_token_count):
    user = Account.objects.create_user('test_username', 'test@test.com', 'test_password')
    old_token = Token.objects.get(user=user).key
    user.auth_token.delete()
    login_url = reverse('login')
    payload = {
        'username': email,
        'password': password
    }

    response = api_client.post(login_url, payload, format='json')
    token_count = Token.objects.count()
    assert response.status_code == http_response
    assert token_count == expected_token_count

    if token_count == 1:
        new_token = Token.objects.get(user=user).key
        assert new_token != old_token


@pytest.mark.django_db
def test_logout(api_client):
    user = Account.objects.create_user('test_username', 'test@test.com', 'test_password')
    token = Token.objects.get(user=user)
    url = reverse('logout')
    api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    response = api_client.get(url)
    check_token = Token.objects.count()
    assert response.status_code == status.HTTP_200_OK
    assert check_token == 0

