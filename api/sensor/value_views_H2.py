from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import SensorH2Value
from api.permission import MesPermission
from api.serializers import SensorH2ValueSerializer


class SensorH2ValueViewSet(viewsets.ModelViewSet):
    class SensorH2ValueFilter(FilterSet):
        fetch_datetime = DateFromToRangeFilter()

        class Meta:
            model = SensorH2Value
            fields = ['mac',]

    queryset = SensorH2Value.objects.all()
    serializer_class = SensorH2ValueSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = SensorH2ValueFilter
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SensorH2ValueViewSet", "get_queryset", False)
        qs = SensorH2Value.objects.filter()

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(created_at__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(created_at__lte=to_date)

        return qs
