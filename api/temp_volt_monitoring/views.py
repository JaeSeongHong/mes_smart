import requests

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import CodeMaster, CustomerMaster, RentalMaster, Rental, Sensor, SensorPC
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, RentalMasterSerializer, RentalSerializer, SensorSerializer, \
    SensorPCSerializer


class SensorPCViewSet(viewsets.ModelViewSet):

    queryset = SensorPC.objects.all()
    serializer_class = SensorPCSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company__id', 'factory__id', 'name']
    pagination_class = None

    def get_queryset(self):
        if self.request.user.order_company and self.request.user.enterprise.name == "(주)아이뉴텍":  # 유저에게 발주기업 정보가 있으면
            return SensorPC.objects.filter(order_company=self.request.user.order_company).all()
        
        return SensorPC.objects.filter(enterprise=self.request.user.enterprise).all()
