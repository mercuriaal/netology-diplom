import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from users.models import Account


@pytest.mark.parametrize(
    ["auth", "http_response"],
    (
        (True, status.HTTP_200_OK),
        (False, status.HTTP_401_UNAUTHORIZED)
    )
)
@pytest.mark.django_db
def test_list(api_client, user_factory, contact_factory, auth, http_response):
    user = user_factory(_quantity=5)
    test_user = user_factory()
    contact = contact_factory(user=test_user)
    url = reverse('contact-list')
    if auth:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + test_user.auth_token.key)
    response = api_client.get(url)
    resp_json = response.json()
    assert response.status_code == http_response
    if auth:
        assert len(resp_json) == 1


@pytest.mark.parametrize(
    ["auth", "http_response"],
    (
        (True, status.HTTP_201_CREATED),
        (False, status.HTTP_401_UNAUTHORIZED)
    )
)
@pytest.mark.django_db
def test_create(api_client, user_factory, auth, http_response):
    user = user_factory()
    url = reverse('contact-list')
    if auth:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)

    payload = {
        'city': 'city',
        'street': 'street',
        'house': 'house',
        'structure': 'structure',
        'building': 'building',
        'apartment': 'apartment',
        'phone': 91234567890
    }

    resp = api_client.post(url, payload)
    assert resp.status_code == http_response


@pytest.mark.parametrize(
    ["auth", "http_response", "user_owner"],
    (
        (True, status.HTTP_200_OK, True),
        (True, status.HTTP_404_NOT_FOUND, False),
        (False, status.HTTP_401_UNAUTHORIZED, False)
    )
)
@pytest.mark.django_db
def test_update(api_client, user_factory, contact_factory, auth, http_response, user_owner):
    owner_user = user_factory()
    random_user = user_factory()
    contact = contact_factory(user=owner_user)
    url = reverse('contact-detail', args=[contact.id])
    if auth and user_owner:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + owner_user.auth_token.key)

    if auth and not user_owner:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + random_user.auth_token.key)

    payload = {
        'phone': 91234567890
    }

    resp = api_client.patch(url, payload)
    assert resp.status_code == http_response


@pytest.mark.parametrize(
    ["auth", "http_response", "user_owner"],
    (
        (True, status.HTTP_204_NO_CONTENT, True),
        (True, status.HTTP_404_NOT_FOUND, False),
        (False, status.HTTP_401_UNAUTHORIZED, False)
    )
)
@pytest.mark.django_db
def test_delete(api_client, user_factory, contact_factory, auth, http_response, user_owner):
    owner_user = user_factory()
    random_user = user_factory()
    contact = contact_factory(user=owner_user)
    url = reverse('contact-detail', args=[contact.id])
    if auth and user_owner:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + owner_user.auth_token.key)

    if auth and not user_owner:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + random_user.auth_token.key)

    resp = api_client.delete(url)
    assert resp.status_code == http_response
