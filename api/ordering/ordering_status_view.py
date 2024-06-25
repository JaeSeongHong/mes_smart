from datetime import date

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import Ordering, OrderingItems
from api.permission import MesPermission
from api.serializers import OrderingStatusSerializer, OrderingItemsStatusSerializer


class OrderingStatusViewSet(viewsets.ModelViewSet):

    queryset = Ordering.objects.all()
    serializer_class = OrderingStatusSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'code']
    pagination_class = None


    def get_queryset(self):
        qs = Ordering.objects.filter(enterprise=self.request.user.enterprise)

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            qs = qs.filter(Q(due_date__gte=fr_date) | Q(due_date=None))

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            qs = qs.filter(Q(due_date__lte=to_date) | Q(due_date=None))

        return qs


    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)


class OrderingItemsStatusViewSet(viewsets.ModelViewSet):

    queryset = OrderingItems.objects.all()
    serializer_class = OrderingItemsStatusSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'patch']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'ordering']
    pagination_class = None


    def get_queryset(self):
        return OrderingItems.objects.filter(enterprise=self.request.user.enterprise)


    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)


    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, request, *args, **kwargs)