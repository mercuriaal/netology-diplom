import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.parametrize(
    ["auth", "http_response", "client_status"],
    (
        (True, status.HTTP_200_OK, True),
        (True, status.HTTP_403_FORBIDDEN, False),
        (False, status.HTTP_401_UNAUTHORIZED, False)
    )
)
@pytest.mark.django_db
def test_list_partner_state(api_client, user_factory, shop_factory, product_factory, auth, http_response,
                            client_status, product_info_factory, category_factory):

    open_partner_user = user_factory(type='partner')
    close_partner_user = user_factory(type='partner')
    client_user = user_factory(type='client')

    open_shop = shop_factory(user=open_partner_user, state=True)
    closed_shop = shop_factory(user=close_partner_user, state=False)

    category = category_factory()
    product = product_factory(category=category)

    open_product_info = product_info_factory(shop=open_shop, product=product)
    close_product_info = product_info_factory(shop=closed_shop, product=product)

    url = reverse('productinfo')
    if auth and client_status:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + client_user.auth_token.key)

    if auth and not client_status:
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + open_partner_user.auth_token.key)

    response = api_client.get(url)
    resp_json = response.json()
    assert response.status_code == http_response
    if auth:
        assert len(resp_json) == 1


@pytest.mark.django_db
def test_category_filter(api_client, category_factory, product_info_factory, product_factory, user_factory,
                         shop_factory):

    open_partner_user = user_factory(type='partner')
    client_user = user_factory(type='client')

    open_shop = shop_factory(user=open_partner_user, state=True)

    target_category = category_factory(special_id=10)
    other_category = category_factory(special_id=15)

    target_product = product_factory(category=target_category)
    other_product = product_factory(category=other_category)

    target_product_info = product_info_factory(shop=open_shop, product=target_product)
    other_product_info = product_info_factory(shop=open_shop, product=other_product)

    payload = {
        'category': target_category.special_id
    }

    url = reverse('productinfo')

    api_client.credentials(HTTP_AUTHORIZATION='Token ' + client_user.auth_token.key)
    response = api_client.get(url, payload)
    resp_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(resp_json) == 1


@pytest.mark.django_db
def test_shop_filter(api_client, category_factory, product_info_factory, product_factory, user_factory,
                         shop_factory):

    open_partner_user = user_factory(type='partner')
    client_user = user_factory(type='client')

    target_shop = shop_factory(user=open_partner_user, state=True)
    other_shop = shop_factory(state=True)

    category = category_factory(special_id=10)

    target_product = product_factory(category=category)
    other_product = product_factory(category=category)

    target_product_info = product_info_factory(shop=target_shop, product=target_product)
    other_product_info = product_info_factory(shop=other_shop, product=other_product)

    payload = {
        'shop': target_shop.id
    }

    url = reverse('productinfo')

    api_client.credentials(HTTP_AUTHORIZATION='Token ' + client_user.auth_token.key)
    response = api_client.get(url, payload)
    resp_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(resp_json) == 1


@pytest.mark.django_db
def test_list_basket(api_client, user_factory, order_factory):

    target_user = user_factory(type='client')
    other_user = user_factory(type='client')

    target_basket = order_factory(state='basket', user=target_user)
    other_basket = order_factory(state='basket', user=other_user)

    not_a_basket = order_factory(state='new', user=other_user)

    url = reverse('basket-list')

    api_client.credentials(HTTP_AUTHORIZATION='Token ' + target_user.auth_token.key)
    response = api_client.get(url)
    resp_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(resp_json) == 1


@pytest.mark.parametrize(
    ["request_quantity", "http_response"],
    (
        (3, status.HTTP_201_CREATED),
        (4, status.HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_create_basket(api_client, user_factory, product_info_factory, product_factory, category_factory, shop_factory,
                       request_quantity, http_response):

    user = user_factory(type='client')

    category = category_factory()
    shop = shop_factory()
    product = product_factory(category=category)
    product_info = product_info_factory(product=product, shop=shop, quantity=3)

    url = reverse('basket-list')

    payload = {
        'product_info': product_info.id,
        'quantity': request_quantity
    }

    api_client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
    response = api_client.post(url, payload)

    assert response.status_code == http_response


@pytest.mark.parametrize(
    ["request_quantity", "http_response"],
    (
        (3, status.HTTP_200_OK),
        (4, status.HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_update_basket(api_client, user_factory, product_info_factory, product_factory, category_factory, shop_factory,
                       request_quantity, http_response, order_factory, order_item_factory):
    user = user_factory(type='client')

    basket = order_factory(state='basket', user=user)
    category = category_factory()
    shop = shop_factory()
    product = product_factory(category=category)
    product_info = product_info_factory(product=product, shop=shop, quantity=3)
    order_item = order_item_factory(product_info=product_info, order=basket)

    url = reverse('basket-detail', args=[order_item.id])

    payload = {
        'quantity': request_quantity
    }

    api_client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
    response = api_client.patch(url, payload)

    assert response.status_code == http_response


@pytest.mark.django_db
def test_destroy_basket(api_client, user_factory, product_info_factory, product_factory, category_factory, shop_factory,
                        order_factory, order_item_factory):
    user = user_factory(type='client')

    basket = order_factory(state='basket', user=user)
    category = category_factory()
    shop = shop_factory()
    product = product_factory(category=category)
    product_info = product_info_factory(product=product, shop=shop, quantity=3)
    order_item = order_item_factory(product_info=product_info, order=basket)

    url = reverse('basket-detail', args=[order_item.id])

    api_client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.parametrize(
    ["order_state", "expected_quantity"],
    (
        ('basket', 0),
        ('new', 1),
        ('confirmed', 1),
        ('assembled', 1),
        ('sent', 1),
        ('delivered', 1),
        ('canceled', 1),
    )
)
@pytest.mark.django_db
def test_list_orders(api_client, user_factory, order_factory, order_state, expected_quantity):

    user = user_factory(type='client')
    other_user = user_factory(type='client')

    target_order = order_factory(user=user, state=order_state)
    other_orders = order_factory(user=other_user, _quantity=5)

    url = reverse('orders-list')

    api_client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
    response = api_client.get(url)
    resp_json = response.json()

    assert len(resp_json) == expected_quantity


@pytest.mark.parametrize(
    ["contact", "http_response"],
    (
        (True, status.HTTP_200_OK),
        (False, status.HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_create_order(api_client, user_factory, order_factory, contact_factory, contact, http_response):

    user = user_factory(type='client')
    contacts = contact_factory(user=user)

    basket = order_factory(user=user, state='basket')
    order = order_factory(user=user)

    url = reverse('orders-detail', args=[basket.id])

    payload = {
        'contact': contacts.id
    }

    api_client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
    if contact:
        response = api_client.patch(url, payload)
    else:
        response = api_client.patch(url)

    assert response.status_code == http_response
