from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import ItemIn
from api.serializers import ItemInMobileSerializer


class ItemInMobileViewSet(viewsets.ModelViewSet):

    queryset = ItemIn.objects.all()
    serializer_class = ItemInMobileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemInMobileViewSet", "get_queryset", False)
        qs = ItemIn.objects.filter(enterprise=self.request.user.enterprise).all()
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)