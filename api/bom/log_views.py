from datetime import date

from django.db import transaction
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from api.models import BomLog
from api.permission import MesPermission
from api.serializers import BomLogSerializer
from api.pagination import PostPageNumberPagination5

class BomLogViewSet(viewsets.ModelViewSet):

    class OrderFilter(FilterSet):
        created_at = DateFromToRangeFilter('created_at')

        class Meta:
            model = BomLog
            fields = ['master', 'created_at']

    queryset = BomLog.objects.all()
    serializer_class = BomLogSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        qs = BomLog.objects.filter(enterprise=self.request.user.enterprise).all()

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(work_date__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(work_date__lte=to_date)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, request, *args, **kwargs)
