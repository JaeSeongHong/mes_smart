from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models import BomMaster
from api.pagination import PostPageNumberPagination5
from api.permission import MesPermission
from api.serializers import BomMasterCostSerializer


class CostProductViewSet(viewsets.ModelViewSet):

    class CostProduct(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = BomMaster
            fields = ['id', 'master_customer', 'bom_number', 'bom_name', 'version', 'created_at',
                      'product_name', 'item', 'required_amount']

    queryset = BomMaster.objects.all()
    serializer_class = BomMasterCostSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_class = CostProduct
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        return BomMaster.objects.filter(enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)
