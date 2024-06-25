from django.db import transaction, models
from django.db.models import Subquery, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from datetime import date, datetime
from KPI.kpi_views import kpi_log
from api.models import ItemAdjust, ItemMaster, ItemIn, ItemOut
from api.pagination import PostPageNumberPagination15
from api.permission import MesPermission
from api.serializers import ItemAdjustSerializer, ItemMasterAdjustSerializer, generate_code


class ItemMasterAdjustViewSet(viewsets.ModelViewSet):
    queryset = ItemMaster.objects.all()
    serializer_class = ItemMasterAdjustSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']  # to remove 'put'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['purchase_from', 'item_division', 'code', 'name', 'model']  # TODO RANGE Query
    search_fields = ["name", "code", "nice_number", "brand__name", "item_group__name"]
    pagination_class = PostPageNumberPagination15

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemMasterAdjustViewSet", "get_queryset",
                False)

        subquery = Subquery(
            ItemAdjust.objects.filter(item_id=OuterRef('id'))
            .order_by('-id')
            .values('current_amount')[:1]
        )
        subquery_previous = Subquery(
            ItemAdjust.objects.filter(item_id=OuterRef('id'))
            .order_by('-id')
            .values('previous_amount')[:1]
        )

        subquery_created = Subquery(
            ItemAdjust.objects.filter(item_id=OuterRef('id'))
            .order_by('-id')
            .values('created_at')[:1]
        )

        subquery_location = Subquery(
            ItemAdjust.objects.filter(item_id=OuterRef('id'))
            .order_by('-id')
            .values('location')[:1]
        )

        qs = ItemMaster.objects.annotate(
            current_amount=subquery,
            previous_amount=subquery_previous,
            adjust_created_at=subquery_created,
            location=subquery_location
        ).filter(enterprise=self.request.user.enterprise).order_by('-id')

        if 'brand' in self.request.query_params:
            brand = self.request.query_params['brand']
            qs = qs.filter(brand=brand)

        if 'item_group' in self.request.query_params:
            item_group = self.request.query_params['item_group']
            qs = qs.filter(item_group=item_group)

        if 'item_name' in self.request.query_params:
            item_name = self.request.query_params['item_name']
            qs = qs.filter(id=item_name)
        elif 'item_code' in self.request.query_params:
            item_code = self.request.query_params['item_code']
            qs = qs.filter(id=item_code)
        elif 'nice_number' in self.request.query_params:
            nice_number = self.request.query_params['nice_number']
            qs = qs.filter(id=nice_number)

        if 'detail' in self.request.query_params:
            detail = self.request.query_params['detail']
            qs = qs.filter(detail__contains=detail)

        if 'shape' in self.request.query_params:
            shape = self.request.query_params['shape']
            qs = qs.filter(shape__contains=shape)

        return qs


class ItemAdjustViewSet(viewsets.ModelViewSet):
    queryset = ItemAdjust.objects.all()
    serializer_class = ItemAdjustSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post']  # to remove 'put'
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['item_in']  # TODO RANGE Query
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "code", "nice_number", "brand__name", "item_group__name"]
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemAdjustViewSet", "get_queryset", False)

        itemId = self.request.query_params['item_id']

        qs = ItemAdjust.objects.filter(enterprise=self.request.user.enterprise, item=itemId).order_by('-id')

        return qs

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemAdjustViewSet", "create", False)
        """
        자재입고 - 입고 자재 생성 (입고 등록)

        자재입고의 입고 등록을 위한 입고 자재 생성 함수로,
        3.1.1 자재입고 설계화면에서 내용 채운 뒤 "입고" 버튼 클릭 -> "저장"을 클릭하면 호출됩니다.
        상단의 검색된 품목 (ItemMaster)이 품번/품명/품종/모델/자재구분/단위를 대체하므로, 품목의 코드를 이용하여 생성하시면 됩니다.
        """

        ret = super().create(request, request, *args, **kwargs)
        item_id = request.data.get('item')
        location = request.data.get("location")
        today = date.today()

        current_amount = int(request.data.get('current_amount'))
        # warehouse_id = request.data.get('warehouse_keep_location')
        # warehouse_obj = ItemMaster.objects.get(id=warehouse_id)
        previous_amount = ItemMaster.objects.get(id=item_id).stock
        item = get_object_or_404(ItemMaster, id=item_id)
        if current_amount > 0:
            num = generate_code("I", ItemIn, "num", self.request.user)
            ItemIn.objects.create(
                num=num,
                item_id=item_id,
                item_created_at=today,
                in_at=today,
                location_id=location,
                package_amount=current_amount,
                receive_amount=current_amount,
                in_faulty_amount=0,
                created_by=self.request.user,
                updated_by=self.request.user,
                created_at=today,
                updated_at=today,
                enterprise=self.request.user.enterprise,
                qr_path='',
                etc="재고조정",  # 출고목적
            )
        else:
            num = generate_code("O", ItemOut, "num", self.request.user)
            ItemOut.objects.create(
                num=num,  # 출하번호
                item_id=item_id,  # 품번
                out_at=today,  # 출하일자
                current_amount=item.stock,  # 현재재고
                out_amount=abs(current_amount),  # 출고수량
                purpose="재고조정",  # 출고목적
                location_id=location,

                created_by=self.request.user,
                updated_by=self.request.user,
                created_at=today,
                updated_at=today,
                enterprise=self.request.user.enterprise
            )
        # item = ItemMaster.objects.get(pk=item_id)
        item.stock = previous_amount + current_amount
        # item.warehouse_keep_location = warehouse_obj
        item.save()

        return ret
