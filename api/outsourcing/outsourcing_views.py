from django.db import transaction
from django.db.models import Max
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import re

from KPI.kpi_views import kpi_log
from django.http import JsonResponse
from api.models import OutsourcingItem, ItemIn, OutsourcingInItems, ItemMaster, ItemOut
from api.permission import MesPermission
from api.serializers import OutsourcingItemSerializer, OutsourcingInItemsSerializer, generate_code
from api.pagination import PostPageNumberPagination5


class OutsourcingItemViewSet(viewsets.ModelViewSet):
    class OutsourcingItemFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = OutsourcingItem
            fields = ['id', ]

    queryset = OutsourcingItem.objects.all()
    serializer_class = OutsourcingItemSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OutsourcingItemFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OutsourcingItemViewSet", "get_queryset", False)
        qs = OutsourcingItem.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')

        if 'out_from' in self.request.query_params:
            out_from = self.request.query_params['out_from']
            if out_from != '':
                qs = qs.filter(out_date__gte=out_from)

        if 'out_to' in self.request.query_params:
            out_to = self.request.query_params['out_to']
            if out_to != '':
                qs = qs.filter(out_date__lte=out_to)

        if 'customer' in self.request.query_params:
            customer = self.request.query_params['customer']
            if customer != '':
                qs = qs.filter(customer=customer)

        if 'item_name' in self.request.query_params:
            item = self.request.query_params['item_name']
            if item != '':
                qs = qs.filter(item=item)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OutsourcingItemViewSet", "create", False)
        res = super().create(request, request, *args, **kwargs)

        return res

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OutsourcingItemViewSet", "partial_update", False)
        res = super().partial_update(request, request, *args, **kwargs)

        outsourcing = OutsourcingItem.objects.get(pk=request.data['id'])

        # Outsourcing 입고여부 변경
        if outsourcing.in_ed_quantity == 0:
            outsourcing.in_status = ''

        elif outsourcing.quantity <= outsourcing.in_ed_quantity:
            outsourcing.in_status = '입고완료'

        else:
            outsourcing.in_status = '일부입고'

        outsourcing.save()

        return res

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OutsourcingItemViewSet", "destroy", False)

        deleted = OutsourcingItem.objects.get(pk=request.data['id'])

        out_id = deleted.item_out.id
        item_id = deleted.item.id
        quantity = deleted.quantity

        # 출고 삭제 / 외주항목이 삭제가 되지 않는 문제가 있어 SET_NULL로 설정하니 해결되었음,, 추후에 문제가 발생한다면 수정 필요
        ItemOut.objects.get(pk=out_id).delete()

        # ItemMaster 재고 계산
        item = ItemMaster.objects.get(pk=item_id)
        item.stock = round(float(item.stock) + float(quantity), 2)
        item.save()

        return super().destroy(request, request, *args, **kwargs)


class OutsourcingInItemsViewSet(viewsets.ModelViewSet):
    class OutsourcingInItemsFilter(FilterSet):
        class Meta:
            model = OutsourcingInItems
            fields = ['id', 'outsourcing_item']

    queryset = OutsourcingInItems.objects.all()
    serializer_class = OutsourcingInItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OutsourcingInItemsFilter
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OutsourcingInItemsViewSet", "get_queryset", False)
        qs = OutsourcingInItems.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')

        if 'outsourcing_item_id' in self.request.query_params:
            outsourcing_item_id = self.request.query_params['outsourcing_item_id']
            if outsourcing_item_id != '':
                qs = qs.filter(outsourcing_item_id=outsourcing_item_id)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OutsourcingInItemsViewSet", "create", False)

        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "partial_update", False)
        res = super().partial_update(request, request, *args, **kwargs)

        return res

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "destroy", False)
        deleted = OutsourcingInItems.objects.get(pk=request.data['id'])

        out_id = deleted.item_in.id
        item_id = deleted.item.id
        outsourcing_id = deleted.outsourcing_item.id
        quantity = deleted.in_quantity

        # 입고 삭제
        ItemIn.objects.get(pk=out_id).delete()

        # Outsourcing 입고될 수량, 입고된 수량 update
        outsourcing = OutsourcingItem.objects.get(pk=outsourcing_id)
        outsourcing.in_will_quantity = round(float(outsourcing.in_will_quantity) + float(quantity), 2)
        outsourcing.in_ed_quantity = round(float(outsourcing.in_ed_quantity) - float(quantity), 2)
        # Outsourcing 입고일자 변경
        try:
            lastest_date = OutsourcingInItems.objects.exclude(pk=request.data['id']).filter(outsourcing_item_id=request.data['master_id']).latest('in_date')
            outsourcing.in_date = lastest_date.in_date
        except:
            outsourcing.in_date = None

        # Outsourcing 입고여부 변경
        if outsourcing.in_ed_quantity == 0:
            outsourcing.in_status = ''

        elif outsourcing.quantity <= outsourcing.in_ed_quantity:
            outsourcing.in_status = '입고완료'

        else:
            outsourcing.in_status = '일부입고'

        outsourcing.save()

        # ItemMaster 재고 계산
        item = ItemMaster.objects.get(pk=item_id)
        item.stock = item.stock - quantity
        item.save()

        return super().destroy(request, request, *args, **kwargs)

