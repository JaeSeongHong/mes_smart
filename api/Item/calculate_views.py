from django.db import models
from django.db.models.expressions import RawSQL
from django.db.models.functions import Coalesce, Cast

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter

from KPI.kpi_views import kpi_log
from api.models import ItemMaster, ItemIn, ItemOut, ItemRein
from api.pagination import PostPageNumberPagination5, PostPageNumberPagination15
from api.permission import MesPermission
from api.serializers import ItemAmountCalculateSerializer, ItemAmountCalculateNonZeroSerializer
from django.db.models import Sum, F, FloatField, Prefetch, Q, Subquery, OuterRef, IntegerField, Case, When, Value, \
    QuerySet


class ItemCalculateViewSet(viewsets.ModelViewSet):
    class ItemCalculateFilter(FilterSet):  # replaced with manual filtering
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemMaster
            fields = ['created_at', 'name', 'code', 'brand', 'item_group', 'nice_number']

    queryset = ItemMaster.objects.all()
    # serializer_class = ItemAmountCalculateSerializer
    serializer_class = ItemAmountCalculateNonZeroSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']  # to remove 'put'
    filter_backends = [DjangoFilterBackend, OrderingFilter, filters.SearchFilter]
    ordering_fields = ["name", "code", "nice_number"]
    search_fields = ["name", "code", "nice_number", "brand__name", "item_group__name"]
    filterset_fields = ['id', 'purchase_from', 'item_division', 'code', 'name', 'type', 'model']
    pagination_class = PostPageNumberPagination15

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemCalculateViewSet", "get_queryset", False)
        # qs = ItemMaster.objects.filter(enterprise=self.request.user.enterprise).all().order_by('-id')

        # stockzero = self.request.query_params['stockzero']

        if 'stockzero' in self.request.query_params:
            stockzero = self.request.query_params['stockzero']
        else :
            stockzero = "False"

        itemin_subquery = Subquery(
            ItemIn.objects.filter(
                item_id=OuterRef('id')

            ).filter(~Q(etc='재고조정')
                     ).values('item_id').annotate(
                in_receive_amount=Sum('receive_amount')
            ).values('in_receive_amount')[:1]
        )
        in_faulty_amount_subquery = Subquery(
            ItemIn.objects.filter(
                item_id=OuterRef('id')
            ).values('item_id').annotate(
                in_faulty_amount=Sum('in_faulty_amount')
            ).values('in_faulty_amount')
        )
        out_amount_subquery = Subquery(
            ItemOut.objects.filter(
                item_id=OuterRef('id')
            ).filter(~Q(purpose='재고조정')
                     ).values('item_id').annotate(
                out_amount=Sum('out_amount')
            ).values('out_amount')[:1]
        )
        in_rein_amount_subquery = Subquery(
            ItemRein.objects.filter(
                item_id=OuterRef('id')
            ).values('item_id').annotate(
                in_rein_amount=Sum('rein_amount') - Sum('out_faulty_amount')
            ).values('in_rein_amount')
        )
        in_adjust_amount_subquery = Subquery(
            ItemIn.objects.filter(
                item_id=OuterRef('id'),
                etc='재고조정'
            ).values('item_id').annotate(
                in_adjust_amount=Sum('receive_amount')
            ).values('in_adjust_amount')
        ) - Subquery(
            ItemOut.objects.filter(
                item_id=OuterRef('id'),
                purpose='재고조정'
            ).values('item_id').annotate(
                out_adjust_amount=Sum('out_amount')
            ).values('out_adjust_amount')
        )

        qs = (
            ItemMaster.objects.filter(enterprise_id=self.request.user.enterprise)
            .annotate(
                in_receive_amount=Coalesce(itemin_subquery, Value(0), output_field=IntegerField()),
                in_faulty_amount=Coalesce(in_faulty_amount_subquery, Value(0), output_field=IntegerField()),
                in_out_amount=Coalesce(out_amount_subquery, Value(0), output_field=IntegerField()),
                in_rein_amount=Coalesce(in_rein_amount_subquery, Value(0), output_field=IntegerField()),
                in_adjust_amount=Coalesce(in_adjust_amount_subquery, Value(0), output_field=IntegerField())
            ).all().order_by('-id')
        )

        if stockzero != "False":
            qs = qs.exclude(
                Q(in_receive_amount__isnull=True) | Q(in_receive_amount=0),
                Q(in_faulty_amount__isnull=True) | Q(in_faulty_amount=0),
                Q(in_out_amount__isnull=True) | Q(in_out_amount=0),
                Q(in_rein_amount__isnull=True) | Q(in_rein_amount=0),
                Q(in_adjust_amount__isnull=True) | Q(in_adjust_amount=0)
            ).all().order_by('-id')


        # if 'customer' in self.request.query_params:
        #     customer = self.request.query_params['customer']
        #     qs = qs.filter(customer__id=customer)

        if 'brand' in self.request.query_params:
            brand = self.request.query_params['brand']
            qs = qs.filter(brand=brand)

        if 'item_group' in self.request.query_params:
            item_group = self.request.query_params['item_group']
            qs = qs.filter(item_group=item_group)

        if 'item_code' in self.request.query_params:
            item_code = self.request.query_params['item_code']
            qs = qs.filter(id=item_code)
        elif 'nice_number' in self.request.query_params:
            nice_number = self.request.query_params['nice_number']
            qs = qs.filter(id=nice_number)

        if 'safe_amount' in self.request.query_params:
            qs = qs.exclude(safe_amount=0)
            qs = qs.annotate(amount=Sum(F("safe_amount") - F('stock'), output_field=FloatField())).order_by("amount")

        if 'item_division' in self.request.query_params:
            item_division = self.request.query_params['item_division']
            qs = qs.filter(item_division_id=item_division)

        # if 'detail' in self.request.query_params:
        #     detail = self.request.query_params['detail']
        #     qs = qs.filter(detail__contains=detail)
        #
        # if 'shape' in self.request.query_params:
        #     shape = self.request.query_params['shape']
        #     qs = qs.filter(shape__contains=shape)

        return qs


class ItemCalculateZeroViewSet(viewsets.ModelViewSet):
    class ItemCalculateFilter(FilterSet):  # replaced with manual filtering
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemMaster
            fields = ['created_at', 'name', 'code', 'brand', 'item_group', 'nice_number']

    queryset = ItemMaster.objects.all()
    # serializer_class = ItemAmountCalculateSerializer
    serializer_class = ItemAmountCalculateNonZeroSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']  # to remove 'put'
    filter_backends = [DjangoFilterBackend, OrderingFilter, filters.SearchFilter]
    # ordering_fields = ["name", "code", "nice_number"]
    search_fields = ["name", "code", "nice_number", "brand__name", "item_group__name"]
    # filterset_fields = ['id', 'purchase_from', 'item_division', 'code', 'name', 'type', 'model']
    pagination_class = PostPageNumberPagination15

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemCalculateViewSet", "get_queryset", False)

        qs = ItemMaster.objects.filter(enterprise_id=self.request.user.enterprise).annotate(
                in_receive_amount=Sum('itemin__receive_amount',
                                      filter=Q(itemin__etc__isnull=True) | ~Q(itemin__etc='재고조정')),
                in_faulty_amount=Sum('itemin__in_faulty_amount'),
                in_out_amount=Sum('itemout_related__out_amount',
                                  filter=~Q(itemout_related__purpose='재고조정', itemout_related__purpose__isnull=False)),
                in_rein_amount=Sum('itemrein_related__rein_amount') - Sum('itemrein_related__out_faulty_amount'),
                in_adjust_amount=(
                            Sum('itemin__receive_amount', filter=Q(itemin__etc='재고조정'))
                            - Sum('itemout_related__out_amount', filter=Q(itemout_related__purpose='재고조정')))
            ).exclude(
                Q(in_receive_amount__isnull=True) | Q(in_receive_amount=0),
                Q(in_faulty_amount__isnull=True) | Q(in_faulty_amount=0),
                Q(in_out_amount__isnull=True) | Q(in_out_amount=0),
                Q(in_rein_amount__isnull=True) | Q(in_rein_amount=0),
                Q(in_adjust_amount__isnull=True) | Q(in_adjust_amount=0)
            ).all().order_by('-id')


        return qs


class ItemCalculateAlertViewSet(viewsets.ModelViewSet):
    class ItemCalculateFilter(FilterSet):  # replaced with manual filtering
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemMaster
            fields = ['created_at']

    queryset = ItemMaster.objects.all()
    serializer_class = ItemAmountCalculateSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']  # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'purchase_from', 'item_division', 'code', 'name', 'type', 'model']
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemCalculateViewSet", "get_queryset", False)
        qs = ItemMaster.objects.filter(enterprise=self.request.user.enterprise).all().order_by('-id')

        for query in qs:
            if query.moq < query.stock or query.moq == query.stock:
                qs = qs.exclude(id=query.id)

        return qs
