from datetime import datetime

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from KPI.kpi_views import kpi_log
from api.models import SubprocessFaultReason, Subprocess
from api.permission import MesPermission
from api.serializers import SubprocessFaultManageSerializer


class SubprocessFaultManagementViewSet(viewsets.ModelViewSet):
    queryset = SubprocessFaultReason.objects.all()
    serializer_class = SubprocessFaultManageSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']  # to remove 'put'
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessFaultManageSerializer", "get_queryset", False)
        return SubprocessFaultReason.objects.filter(enterprise=self.request.user.enterprise)

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessFaultManageSerializer", "create", False)

        ret = super().create(request, request, *args, **kwargs)

        return ret

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessFaultManageSerializer", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessFaultManageSerializer", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)