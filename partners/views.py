import yaml

from django.db.models import Sum, F
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clients.models import Order
from clients.serializers import OrderSerializer
from partners.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from partners.serializers import ShopSerializer

from users.permissions import Partner, Owner
from users.signals import products_update


class PartnerStateView(ListAPIView, UpdateModelMixin):

    """
    Класс для просмотра и изменения статуса приёма заказов у поставщиков
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, Owner, Partner]
    serializer_class = ShopSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = Shop.objects.filter(user=user)
        return queryset


class UploadProduct(APIView):

    """
    Класс для загрузки информации о товарах поставщиком
    """

    permission_classes = [IsAuthenticated, Partner]
    authentication_classes = [TokenAuthentication]
    throttle_scope = 'uploads'

    def post(self, request):

        user_shop = Shop.objects.filter(user=request.user)
        import_file = request.data['file']
        if user_shop.exists():
            obj = user_shop.get()
            obj.file = import_file
            obj.save()
            with open(str(user_shop.get().file),  encoding='utf-8') as file:
                upload = yaml.load(file, Loader=yaml.FullLoader)

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
                    prod_param, _ = ProductParameter.objects.get_or_create(product_info=product_info,
                                                                           parameter=parameter,
                                                                           value=value)

            products_update.send(sender=self.__class__, user_id=request.user.id)

        else:
            raise ValidationError('Пользователь не привязан к магазину')
        return Response('Товары загружены в базу данных')


class PartnerOrders(ListAPIView):

    """
    Класс для просмотра заказов, оформленных на поставщика
    """

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
