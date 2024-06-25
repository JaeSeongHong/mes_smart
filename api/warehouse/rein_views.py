from datetime import date

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter, FilterSet
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from api.Item.rein_views import ItemReinViewSet
from api.models import ItemOut, ItemMaster, ItemRein, ItemWarehouseStock
from api.permission import MesPermission
from api.serializers import ItemOutSerializer, ItemReinSerializer, ItemWarehouseReinSerializer


class ItemWarehouseReinViewSet(viewsets.ModelViewSet):
    class ItemReinFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemRein
            fields = ['item__item_division', 'item__code', 'item__name', 'item__type', 'item__model', 'item',
                      'item_warehouse_rein_item_rein__warehouse__code']

    queryset = ItemRein.objects.all()
    serializer_class = ItemWarehouseReinSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']  # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemReinFilter
    pagination_class = None

    def get_queryset(self):
        return ItemRein.objects.filter(enterprise=self.request.user.enterprise).all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(ItemWarehouseReinViewSet, self).create(request, args, kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super(ItemWarehouseReinViewSet, self).partial_update(request, args, kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        previous = self.get_object()
        if previous.created_at != date.today():
            raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        # ItemWarehouseStock stock 계산
        iws = get_object_or_404(ItemWarehouseStock, item=previous.item,
                                warehouse=previous.item_warehouse_rein_item_rein.warehouse)
        iws.update_stock(iws.stock - (previous.rein_amount - previous.out_faulty_amount))

        return super(ItemWarehouseReinViewSet, self).destroy(request, *args, **kwargs)
