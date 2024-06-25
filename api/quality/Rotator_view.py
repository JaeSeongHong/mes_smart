from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import Rotator
from api.permission import MesPermission
from api.serializers import RotatorSerializer
from api.pagination import PostPageNumberPagination5


class RotatorViewSet(viewsets.ModelViewSet):
    class RotatorFilter(FilterSet):

        class Meta:
            model = Rotator
            fields = ['id']

    queryset = Rotator.objects.all()
    serializer_class = RotatorSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RotatorFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "RotatorViewSet", "get_queryset", False)
        qs = Rotator.objects.filter(enterprise=self.request.user.enterprise)

        if 'item_name' in self.request.query_params:
            item_name = self.request.query_params['item_name']
            if item_name != '':
                qs = qs.filter(item_name__contains=item_name)

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(test_date__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(test_date__lte=to_date)

        qs = qs.order_by('-id')
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "RotatorViewSet", "create", False)
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "RotatorViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "RotatorViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)