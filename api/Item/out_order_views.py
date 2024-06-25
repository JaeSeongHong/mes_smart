from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter, FilterSet
from rest_framework.permissions import IsAuthenticated
from api.models import ItemOut, ItemOutOrder
from api.permission import MesPermission
from api.serializers import ItemOutOrderSerializer
from api.pagination import PostPageNumberPagination5
from rest_framework import viewsets


class ItemOutOrderViewSet(viewsets.ModelViewSet):
    class ItemOutOrderFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemOutOrder
            fields = ['item__item_division', 'item__code', 'item__name', 'item__type', 'item__model', 'item']

    queryset = ItemOutOrder.objects.all()
    serializer_class = ItemOutOrderSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemOutOrderFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        return ItemOutOrder.objects.filter(enterprise=self.request.user.enterprise).all().order_by('-id')

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, request, *args, **kwargs)
