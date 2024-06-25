from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import CustomerMaster
from api.permission import MesPermission
from api.serializers import CustomerMasterSerializer, CustomerMasterSelectSerializer, CustomerMasterPartSerializer
from rest_framework.pagination import PageNumberPagination


class CustomerMasterViewSet(viewsets.ModelViewSet):
    queryset = CustomerMaster.objects.all()
    serializer_class = CustomerMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['division', 'name']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "get_queryset", False)
        return CustomerMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "create", False)
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)


class CustomerMasterSelectView(viewsets.ModelViewSet):
    queryset = CustomerMaster.objects.all()
    serializer_class = CustomerMasterSelectSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['division', 'name']
    pagination_class = None

    def get_queryset(self):
        return CustomerMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')


class CustomerMasterPartView(viewsets.ModelViewSet):
    queryset = CustomerMaster.objects.all()
    serializer_class = CustomerMasterPartSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['division', 'name']
    pagination_class = None

    def get_queryset(self):
        return CustomerMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')
