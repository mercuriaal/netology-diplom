import yaml
from pprint import pprint

from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from partners.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from partners.serializers import ShopSerializer
from users.permissions import Partner


class ShopViewSet(ModelViewSet):

    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated, Partner])
def upload_products(request):

    user_shop = Shop.objects.filter(user=request.user)
    if user_shop.exists():
        path = Shop.objects.get(user=request.user).file
    else:
        raise ValidationError('Пользователь не привязан к магазину')

    with open(str(path), encoding='utf-8') as file:
        upload = yaml.load(file, Loader=yaml.FullLoader)
        pprint(upload)

    if not all([upload.get('categories'), upload.get('goods'), upload.get('shop')]):
        raise ValidationError('В файле отсутствуют необходимые поля')

    if not all([upload.get('categories')[0].get('id'), upload.get('categories')[0].get('name'),
                upload.get('goods')[0].get('id'), upload.get('goods')[0].get('category'),
                upload.get('goods')[0].get('model'), upload.get('goods')[0].get('name'),
                upload.get('goods')[0].get('parameters'), upload.get('goods')[0].get('price'),
                upload.get('goods')[0].get('price_rrc'), upload.get('goods')[0].get('quantity')]):
        raise ValidationError('В файле отсутствуют необходимые поля')

    shop = Shop.objects.get(user=request.user)
    for item in upload['categories']:
        category, _ = Category.objects.get_or_create(special_id=item['id'], name=item['name'])
        category.shops.add(shop.id)
        category.save()

    for item in upload['goods']:
        category = Category.objects.get(special_id=item['category'])
        product, _ = Product.objects.get_or_create(name=item['name'], category=category, special_id=item['id'])
        product_info, _ = ProductInfo.objects.get_or_create(model=item['model'], quantity=item['quantity'],
                                                            price=item['price'], price_rrc=item['price_rrc'],
                                                            product=product, shop=shop)

        for name, value in item['parameters'].items():
            parameter, _ = Parameter.objects.get_or_create(name=name)
            prod_param, _ = ProductParameter.objects.get_or_create(product_info=product_info, parameter=parameter,
                                                                   value=value)

    return Response('Товары загружены в базу данных')