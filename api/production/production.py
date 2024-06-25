from django.db import transaction
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import Device
from api.permission import MesPermission
from api.serializers import DeviceSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "DeviceViewSet", "get_queryset", False)
        return Device.objects.filter(enterprise=self.request.user.enterprise).all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "DeviceViewSet", "create", False)
        device = request.POST['device']
        qs = Device.objects.filter(enterprise=self.request.user.enterprise).all()
        if qs.filter(device=device).count() != 0:
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "DeviceViewSet", "create", True)
            raise ValidationError('장비명이 이미 사용중입니다.')

        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "DeviceViewSet", "partial_update", False)
        device = request.POST['device']
        qs = Device.objects.filter(enterprise=self.request.user.enterprise).all()

        pk = kwargs['pk']
        qs = qs.filter(~Q(id=int(pk)))

        if qs.filter(device=device).count() != 0:
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "DeviceViewSet", "partial_update", True)
            raise ValidationError('장비명이 이미 사용중입니다.')

        return super().partial_update(request, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "DeviceViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)
