from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from api.Item.adjust_views import ItemMasterAdjustViewSet, ItemAdjustViewSet
from api.models import ItemAdjust, ItemIn, ItemMaster
from api.permission import MesPermission
from api.serializers import ItemAdjustSerializer, ItemMasterAdjustSerializer, ItemWarehouseAdjustSerializer, \
    ItemMasterWarehouseAdjustSerializer


class ItemMasterWarehouseAdjustViewSet(ItemMasterAdjustViewSet):

    serializer_class = ItemMasterWarehouseAdjustSerializer

    def get_serializer_context(self):
        """Serializer에게 어떤 warehouse 정보를 가져와야 하는지 전달하기 위함."""
        context = super().get_serializer_context()
        context['warehouse_code'] = self.request.query_params.get('warehouse_code', 0)
        return context


class ItemWarehouseAdjustViewSet(ItemAdjustViewSet):
    serializer_class = ItemWarehouseAdjustSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        창고관리의 자재입고 - 입고 자재 생성 (입고 등록)

        .
        """
        return super(ItemWarehouseAdjustViewSet, self).create(request, args, kwargs)
