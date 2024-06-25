from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import SubprocessTemplet
from api.permission import MesPermission
from api.serializers import SubprocesstempletSerializer
from api.pagination import PostPageNumberPagination5


class SubprocessTempletViewSet(viewsets.ModelViewSet):
    queryset = SubprocessTemplet.objects.all()
    serializer_class = SubprocesstempletSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['master']
    pagination_class = PostPageNumberPagination5

    # Todo hjlim : 주석 변경 > Templet 으로

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessTempletViewSet", "get_queryset", False)
        return SubprocessTemplet.objects.filter(enterprise=self.request.user.enterprise)

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessTempletViewSet", "create", False)
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessTempletViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessTempletViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)
