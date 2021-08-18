from django.db.models import F, Sum
from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend

from partners.models import ProductInfo


class ProductInfoFilter(filters.FilterSet):

    category = filters.NumberFilter(field_name='product', method='products_filter')

    class Meta:
        model = ProductInfo
        fields = ('category', 'shop',)

    def products_filter(self, queryset, name, value):
        query = queryset.filter(product__category_id=value)
        return query


class ListOrderFilterBackEnd(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        return queryset.exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).select_related(
            'contact'
        ).annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()


class PostOrderFilterBackEnd(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(state='basket')


class ListBasketFilterBackEnd(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()


class BasketOwnerFilterBackEnd(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(order__user=request.user.id)
