from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from api.base.item_views import ItemMasterViewSet
from api.models import ItemMaster
from api.permission import MesPermission
from api.serializers import ItemMasterSerializer, ItemMasterWarehouseSerializer


class ItemMasterWarehouseViewSet(ItemMasterViewSet):

    serializer_class = ItemMasterWarehouseSerializer

    def get_serializer_context(self):
        """Serializer에게 어떤 warehouse 정보를 가져와야 하는지 전달하기 위함."""
        context = super().get_serializer_context()
        context['warehouse_code'] = self.request.query_params.get('warehouse_code', 0)
        return context