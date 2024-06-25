from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import MyInfoMaster
from api.permission import MesPermission
from api.serializers import MyInfoSerializer
from rest_framework.pagination import PageNumberPagination


class MyInfoViewSet(viewsets.ModelViewSet):
    class MyInfoFilter(FilterSet):

        class Meta:
            model = MyInfoMaster
            fields = ['id']

    queryset = MyInfoMaster.objects.all()
    serializer_class = MyInfoSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = MyInfoFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "MyInfoViewSet", "get_queryset", False)
        return MyInfoMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('id')

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "MyInfoViewSet", "create", False)

        company_division = request.POST['company_division']
        my_qs = MyInfoMaster.objects.filter(enterprise=self.request.user.enterprise, company_division=company_division)
        if my_qs.exists():
            raise ValidationError("사업장 명은 중복될 수 없습니다.")

        qs = super().create(request, request, *args, **kwargs)
        return qs

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "MyInfoViewSet", "partial_update", False)

        my_qs = MyInfoMaster.objects.filter(enterprise=self.request.user.enterprise)
        my_qs = my_qs.filter(~Q(id=kwargs["pk"]))

        company_division = request.POST['company_division']
        my_qs = my_qs.filter(company_division=company_division)
        if my_qs.exists():
            raise ValidationError("사업장 명은 중복될 수 없습니다.")

        qs = super().partial_update(request, request, *args, **kwargs)
        return qs

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "MyInfoViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)
