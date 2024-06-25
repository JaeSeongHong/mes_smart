from datetime import date

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter, FilterSet
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from api.Item.out_views import ItemOutViewSet
from api.models import ItemOut, ItemMaster, ItemWarehouseStock
from api.permission import MesPermission
from api.serializers import ItemOutSerializer, ItemWarehouseOutSerializer


class ItemWarehouseOutViewSet(viewsets.ModelViewSet):
    class ItemOutFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemOut
            fields = ['item__item_division', 'item__code', 'item__name', 'item__type', 'item__model', 'item',
                      'item_warehouse_out_item_out__warehouse__code']

    queryset = ItemOut.objects.all()
    serializer_class = ItemWarehouseOutSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemOutFilter
    pagination_class = None

    def get_queryset(self):
        return ItemOut.objects.filter(enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        """
        창고관리의 자재출고 - 출고 자재 조회

        .
        """
        return super(ItemWarehouseOutViewSet, self).list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        창고관리의 자재출고 - 출고 자재 생성 (출고 등록)

        .
        """
        return super(ItemWarehouseOutViewSet, self).create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        창고관리의 자재출고 - 출고 자재 조회 (개별)

        .
        """
        return super(ItemWarehouseOutViewSet, self).retrieve(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """
        창고관리의 자재출고 - 출고 자재 수정

        .
        """
        return super(ItemWarehouseOutViewSet, self).partial_update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        창고관리의 자재출고 - 출고 자재 삭제

        .
        """
        previous = self.get_object()
        if previous.created_at != date.today():
            raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        # ItemWarehouseStock stock 계산
        iws = get_object_or_404(ItemWarehouseStock, item=previous.item,
                                warehouse=previous.item_warehouse_out_item_out.warehouse)
        iws.update_stock(iws.stock + previous.out_amount)

        return super(ItemWarehouseOutViewSet, self).destroy(request, *args, **kwargs)
