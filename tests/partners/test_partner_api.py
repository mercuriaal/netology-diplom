import pytest
import os
from django.urls import reverse
from rest_framework import status


@pytest.mark.parametrize(
    ["auth", "http_response", "partner_status"],
    (
        (True, status.HTTP_200_OK, True),
        (True, status.HTTP_403_FORBIDDEN, False),
        (False, status.HTTP_401_UNAUTHORIZED, False)
    )
)
@pytest.mark.django_db
def test_list_partner_state(api_client, user_factory, shop_factory, auth, http_response, partner_status):
    other_shops = shop_factory(_quantity=10)
    test_partner_user = user_factory(type='partner')
    client_user = user_factory(type='client')
    test_shop = shop_factory(user=test_partner_user)
    url = reverse('shop')
    if auth and partner_status:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + test_partner_user.auth_token.key)

    if auth and not partner_status:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + client_user.auth_token.key)

    response = api_client.get(url)
    resp_json = response.json()
    assert response.status_code == http_response
    if auth:
        assert len(resp_json) == 1


@pytest.mark.parametrize(
    ["auth", "http_response", "partner_status"],
    (
        (True, status.HTTP_200_OK, True),
        (True, status.HTTP_403_FORBIDDEN, False),
        (False, status.HTTP_401_UNAUTHORIZED, False)
    )
)
@pytest.mark.django_db
def test_update_partner_state(api_client, user_factory, shop_factory, auth, http_response, partner_status):
    test_partner_user = user_factory(type='partner')
    shop = shop_factory(user=test_partner_user)
    client_user = user_factory(type='client')
    url = reverse('shop', args=[shop.id])

    if auth and partner_status:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + test_partner_user.auth_token.key)

    if auth and not partner_status:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + client_user.auth_token.key)

    payload = {
        'state': False
    }

    response = api_client.patch(url, payload)
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["auth", "partner_status", "file_name", "http_response"],
    (
        (True, True, 'good_import.yaml', status.HTTP_200_OK),
        (True, True, 'bad_import.yaml', status.HTTP_400_BAD_REQUEST),
        (True, False, 'good_import.yaml', status.HTTP_403_FORBIDDEN),
        (False, False, 'good_import.yaml', status.HTTP_401_UNAUTHORIZED)
    )
)
@pytest.mark.django_db
def test_upload(api_client, user_factory, shop_factory, auth, partner_status, file_name, http_response):
    user = user_factory(type='partner')
    client_user = user_factory(type='client')
    shop = shop_factory(user=user)
    url = reverse('upload')

    payload = {
        'file': os.path.join('tests/partners/test_files/', file_name)
    }

    if auth and partner_status:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)

    if auth and not partner_status:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + client_user.auth_token.key)

    response = api_client.post(url, payload, format='json')
    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["auth", "http_response"],
    (
        (True, status.HTTP_200_OK),
        (False, status.HTTP_401_UNAUTHORIZED)
    )
)
@pytest.mark.django_db
def test_list_orders(api_client, user_factory, order_factory, auth, http_response, product_factory, category_factory):
    user = user_factory(type='partner')
    client_user = user_factory(type='client')
    other_client_user = user_factory(type='client')
    category = category_factory()
    product = product_factory(category=category)
    related_order = order_factory(ordered_items__product_info__shop__user_id=user.id, user=client_user,
                                  ordered_items__product_info__product=product, state='new', ordered_items__quantity=1,
                                  ordered_items__product_info__price=100)
    non_related_orders = order_factory(_quantity=5, user=other_client_user)
    url = reverse('order')

    if auth:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)

    response = api_client.get(url)
    resp_json = response.json()
    assert response.status_code == http_response
    if auth:
        assert len(resp_json) == 1
