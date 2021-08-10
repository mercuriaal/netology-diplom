from django_filters import rest_framework as filters

from partners.models import ProductInfo


class ProductInfoFilter(filters.FilterSet):

    category = filters.NumberFilter(field_name='product', method='products_filter')

    class Meta:
        model = ProductInfo
        fields = ('category', 'shop',)

    def products_filter(self, queryset, name, value):
        query = queryset.filter(product__category_id=value)
        return query
