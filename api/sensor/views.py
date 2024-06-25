import requests

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import CodeMaster, CustomerMaster, RentalMaster, Rental, Sensor
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, RentalMasterSerializer, RentalSerializer, SensorSerializer


class SensorViewSet(viewsets.ModelViewSet):

    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['factory__id', 'facilities__id', 'type__id']
    pagination_class = None

    def get_queryset(self):
        return Sensor.objects.filter(enterprise=self.request.user.enterprise).all()

    def connection_check(self, request, *args, **kwargs):
        # 업체 하드코딩
        try:
            sensor = get_object_or_404(Sensor, pk=kwargs.get('pk'))
            res = requests.get(sensor.api_url)
            if self.request.user.enterprise.name == '시온테크놀러지':
                items = res.text[1:-1].replace('\"', '').split(',')
            elif self.request.user.enterprise.name == 'JA푸드':
                items = res.json()
            else:
                raise ValidationError('허가된 업체가 아닙니다.')

            return Response(items, status=status.HTTP_200_OK)

        except Exception:
            raise ValidationError('연결 실패')
