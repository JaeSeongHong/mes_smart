from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.Item.calculate_views import ItemCalculateViewSet
from api.models import ItemAdjust, ItemIn, ItemMaster
from api.permission import MesPermission
from api.serializers import ItemWarehouseAmountCalculateSerializer


class ItemWarehouseCalculateViewSet(ItemCalculateViewSet):

    class ItemCalculateFilter(FilterSet):       # replaced with manual filtering
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemMaster
            fields = ['created_at']

    serializer_class = ItemWarehouseAmountCalculateSerializer

    def get_serializer_context(self):
        """Serializer에게 어떤 warehouse 정보를 가져와야 하는지 전달하기 위함."""
        context = super().get_serializer_context()
        context['warehouse_code'] = self.request.query_params.get('warehouse_code', 0)
        return context

    def list(self, request, *args, **kwargs):
        """
        창고관리의 자재현황 - 자재 현황 조회

        .
        """
        return super().list(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        창고관리의 자재현황 - 자재 현황 조회 (개별)

        .
        """
        return super().retrieve(request, request, *args, **kwargs)
