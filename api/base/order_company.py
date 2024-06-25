from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import OrderCompany
from api.permission import MesPermission
from api.serializers import OrderCompanySerializer


class OrderCompanyViewSet(viewsets.ModelViewSet):

    queryset = OrderCompany.objects.all()
    serializer_class = OrderCompanySerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderCompanyViewSet", "get_queryset", False)
        return OrderCompany.objects.filter(enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        """
        발주기업 조회


        """
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderCompanyViewSet", "create", False)
        """
        발주기업 생성

        """
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        발주기업 조회 (개별)

        """
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderCompanyViewSet", "partial_update", False)
        """
        발주기업 수정

        """
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderCompanyViewSet", "destroy", False)
        """
        발주기업 삭제

        """
        return super().destroy(request, request, *args, **kwargs)
