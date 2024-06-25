from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models import CodeMaster, CustomerMaster, RentalMaster, Rental, Sensor, SensorValue
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, RentalMasterSerializer, RentalSerializer, SensorSerializer, \
    SensorValueSerializer


class SensorValueViewSet(viewsets.ModelViewSet):
    class SensorValueFilter(FilterSet):
        fetch_datetime = DateFromToRangeFilter()

        class Meta:
            model = SensorValue
            fields = ['master__factory__id', 'master__facilities__id', 'master__type__id']

    queryset = SensorValue.objects.all()
    serializer_class = SensorValueSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = SensorValueFilter
    pagination_class = None

    def get_queryset(self):
        return SensorValue.objects.filter(master__enterprise=self.request.user.enterprise).all()
