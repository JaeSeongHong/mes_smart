from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import ItemMaster
from api.pagination import PostPageNumberPagination5
from api.permission import MesPermission
from api.serializers import ItemCostCalculateSerializer


class ItemCostCalculateViewSet(viewsets.ModelViewSet):

    class ItemCostCalculateFilter(FilterSet):       # replaced with manual filtering
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemMaster
            fields = ['created_at']

    queryset = ItemMaster.objects.all()
    serializer_class = ItemCostCalculateSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'purchase_from', 'item_division', 'code', 'name', 'type', 'model']
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemCostCalculateViewSet", "get_queryset", False)
        qs =ItemMaster.objects.filter(enterprise=self.request.user.enterprise).all().order_by('id')

        for row in qs:
            if row.bom_division:
                qs = qs.filter(~Q(bom_division=row.bom_division))

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)
