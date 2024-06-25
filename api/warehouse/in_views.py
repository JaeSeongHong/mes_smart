from datetime import date

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from api.Item.in_views import ItemInViewSet
from api.models import ItemIn, ItemWarehouseStock
from api.permission import MesPermission
from api.serializers import ItemInSerializer, ItemWarehouseInSerializer


class ItemWarehouseInViewSet(viewsets.ModelViewSet):

    queryset = ItemIn.objects.all()
    serializer_class = ItemWarehouseInSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['num', 'item_warehouse_in_item_in__warehouse__code']
    pagination_class = None

    def get_queryset(self):
        return ItemIn.objects.filter(enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        """
        창고관리의 자재입고 - 입고 자재 조회

        자재입고와 동일하나, 창고가 추가로 존재합니다.
        창고의 재자를 확인하고 싶다면 filter를 이용합니다.
        """
        return super(ItemWarehouseInViewSet, self).list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        창고관리의 자재입고 - 입고 자재 생성 (입고 등록)

        .
        """
        return super(ItemWarehouseInViewSet, self).create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        창고관리의 자재입고 - 입고 자재 조회 (개별)

        .
        """
        return super(ItemWarehouseInViewSet, self).retrieve(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """
        창고관리의 자재입고 - 입고 자재 수정

        .
        """
        return super(ItemWarehouseInViewSet, self).partial_update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        창고관리의 자재입고 - 입고 자재 삭제

        .
        """
        previous = self.get_object()
        if previous.created_at != date.today():
            raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        # ItemWarehouseStock stock 계산
        iws = get_object_or_404(ItemWarehouseStock, item=previous.item,
                                warehouse=previous.item_warehouse_in_item_in.warehouse)
        iws.update_stock(iws.stock - previous.in_amount)

        return super(ItemWarehouseInViewSet, self).destroy(request, *args, **kwargs)
