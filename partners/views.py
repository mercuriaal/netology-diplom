import yaml
import os
from pprint import pprint

from django.db.models import Sum, F
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from clients.models import Order
from clients.serializers import OrderSerializer
from partners.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from partners.serializers import ShopSerializer

from users.permissions import Partner, Owner


class PartnerStateView(ListAPIView, UpdateModelMixin):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, Owner, Partner]
    serializer_class = ShopSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = Shop.objects.filter(user=user)
        return queryset


@api_view(["POST"])
@permission_classes([IsAuthenticated, Partner])
def upload_products(request):

    user_shop = Shop.objects.filter(user=request.user)
    import_file = request.data['file']
    if user_shop.exists():
        shop = user_shop.get()
        os.remove(str(shop.file))
        shop.file = import_file
        shop.save()
        with open(str(shop.file),  encoding='utf-8') as file:
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

        ProductInfo.objects.filter(shop_id=shop.id).delete()
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

    else:
        raise ValidationError('Пользователь не привязан к магазину')
    return Response('Товары загружены в базу данных')


class PartnerOrders(ListAPIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, Partner]
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.filter(
            ordered_items__product_info__shop__user_id=self.request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        return queryset
