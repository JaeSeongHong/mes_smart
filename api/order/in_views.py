from datetime import date

from django.db import transaction
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from api.models import ItemIn, ItemMaster, OrderIn
from api.permission import MesPermission
from api.serializers import ItemInSerializer, OrderInSerializer


class OrderInViewSet(viewsets.ModelViewSet):

    class OrderFilter(FilterSet):
        created_at = DateFromToRangeFilter('created_at')

        class Meta:
            model = OrderIn
            fields = ['created_at', 'master__customer', 'master__item__code', 'master__item__name', 'master', 'is_in']

    queryset = OrderIn.objects.all()
    serializer_class = OrderInSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    pagination_class = None

    def get_queryset(self):
        return OrderIn.objects.filter(enterprise=self.request.user.enterprise).all()
