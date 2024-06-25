import traceback

import django_filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets,  filters
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import BomMaster, ItemMaster, Bom, Process, SubprocessTemplet
from api.pagination import PostPageNumberPagination5
from api.permission import MesPermission
from api.serializers import BomMasterSerializer, BomMasterSelectSerializer
from django.db.models import Q


class BomMasterViewSet(viewsets.ModelViewSet):
    class BomMasterFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = BomMaster
            fields = ['bom_number', 'product_name', 'model_name', 'master_customer__name', 'created_at',
                      'item', 'required_amount']

    queryset = BomMaster.objects.all()
    serializer_class = BomMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']  # to remove 'put'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['nice_number', 'bom_number', 'product_name', "brand__name", "item_group__name"]
    filterset_class = BomMasterFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "get_queryset", False)
        qs = BomMaster.objects.all().filter(enterprise=self.request.user.enterprise).all().order_by("-id")

        if 'nice' in self.request.query_params:
            nice = self.request.query_params['nice']
            qs = qs.filter(nice_number=nice)

        if 'item_code' in self.request.query_params:
            item_code = self.request.query_params[  'item_code']
            qs = qs.filter(bom_number=item_code)

        if 'brand' in self.request.query_params:
            brand = self.request.query_params['brand']
            qs = qs.filter(brand__name=brand)

        if 'item_group' in self.request.query_params:
            item_group = self.request.query_params['item_group']
            qs = qs.filter(item_group__name=item_group)

        return qs

    # def list(self, request, *args, **kwargs):
    #     return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "create", False)
        res = super().create(request, request, *args, **kwargs)

        user = request.user

        if res.data['detail']:
            detail = res.data['detail']
        else:
            detail = None

        if res.data['item_division']:
            item_division_id = res.data['item_division']['id']
        else:
            item_division_id = None

        if res.data['model_name']:
            model_name_id = res.data['model_name']['id']
        else:
            model_name_id = None

        if res.data['container']:
            container_id = res.data['container']['id']
        else:
            container_id = None

        if res.data['color']:
            color_id = res.data['color']['id']
        else:
            color_id = None

        if res.data['type']:
            type_id = res.data['type']['id']
        else:
            type_id = None

        if res.data['brand']:
            brand = res.data['brand']['id']
        else:
            brand = None
        if res.data['item_group']:
            item_group = res.data['item_group']['id']
        else:
            item_group = None
        if res.data['nice_number']:
            nice_number = res.data['nice_number']
        else:
            nice_number = None
        if res.data['shape']:
            shape = res.data['shape']
        else:
            shape = None
        if res.data['master_customer']:
            customer = res.data['master_customer']['id']
        else:
            customer = None
        if res.data['amount']:
            amount = res.data['amount']
        else:
            amount = 0
        if res.data['price']:
            price = res.data['price']
        else:
            price = 0

        try:
            item_master = ItemMaster.objects.create(code=res.data['bom_number'],  # 품번 - BOM 코드
                                                    name=res.data['product_name'],  # 품명 - 생산제품명
                                                    detail=detail,  # 품명상세 - 품명상세
                                                    item_division_id=item_division_id,  # 자재분류 - 자재분류
                                                    model_id=model_name_id,  # 모델 - 모델
                                                    container_id=container_id,  # 용기타입 - 용기타입
                                                    color_id=color_id,  # 칼라구분 - 칼라구분
                                                    type_id=type_id,  # 품종 - 품종
                                                    brand_id=brand,
                                                    item_group_id=item_group,
                                                    nice_number=nice_number,
                                                    shape=shape,
                                                    purchase_from_id=customer,
                                                    bom_division_id=res.data['id'],
                                                    safe_amount=amount,
                                                    standard_price=price,

                                                    created_by=user,
                                                    updated_by=user,
                                                    created_at=user,
                                                    updated_at=user,
                                                    enterprise=request.user.enterprise
                                                    )

            from api.QRCode.QRCodeManager import QRCodeGen_Code
            filename = QRCodeGen_Code(res.data['bom_number'], 'ItemMaster')

            print(filename)

            # instance['qr_path'] = filename
            item_master.qr_path = filename
            item_master.save()

        except Exception as e:
            print('에러', e)
            print(traceback.format_exc())

            if e.args[0] == 1062:  # 중복값 에러
                raise ValidationError('품목 번호가 이미 존재합니다.')

            raise ValidationError('품목 생성시 예외가 발생했습니다.')

        return res

    def retrieve(self, request, *args, **kwargs):

        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "partial_update",
                False)
        res = super().partial_update(request, request, *args, **kwargs)

        if res.data['detail']:
            detail = res.data['detail']
        else:
            detail = None

        if res.data['item_division']:
            item_division_id = res.data['item_division']['id']
        else:
            item_division_id = None

        if res.data['model_name']:
            model_name_id = res.data['model_name']['id']
        else:
            model_name_id = None

        if res.data['container']:
            container_id = res.data['container']['id']
        else:
            container_id = None

        if res.data['color']:
            color_id = res.data['color']['id']
        else:
            color_id = None

        if res.data['type']:
            type_id = res.data['type']['id']
        else:
            type_id = None

        if res.data['brand']:
            brand = res.data['brand']['id']
        else:
            brand = None
        if res.data['item_group']:
            item_group = res.data['item_group']['id']
        else:
            item_group = None
        if res.data['nice_number']:
            nice_number = res.data['nice_number']
        else:
            nice_number = None
        if res.data['shape']:
            shape = res.data['shape']
        else:
            shape = None
        if res.data['master_customer']:
            customer = res.data['master_customer']['id']
        else:
            customer = None
        if res.data['amount']:
            amount = res.data['amount']
        else:
            amount = 0
        if res.data['price']:
            price = res.data['price']
        else:
            price = 0

        row = ItemMaster.objects.get(bom_division_id=res.data['id'])

        row.code = res.data['bom_number']  # 품번 - BOM 코드
        row.name = res.data['product_name']  # 품명 - 생산제품명
        row.detail = detail  # 품명상세 - 품명상세
        row.brand_id = brand
        row.item_group_id = item_group
        row.nice_number = nice_number
        row.shape = shape
        row.item_division_id = item_division_id  # 자재분류 - 자재분류
        row.model_id = model_name_id  # 모델 - 모델
        row.container_id = container_id  # 용기타입 - 용기타입
        row.color_id = color_id  # 칼라구분 - 칼라구분
        row.type_id = type_id  # 품종구분 - 품종구분
        row.customer_id = customer
        row.safe_amount = amount
        row.standard_price = price

        qs_boms = Bom.objects.filter(item_id=row.id)
        if qs_boms:
            for bom in qs_boms:
                bom.item_name = row.name
                bom.save()

        qs_pros = Process.objects.filter(bom_master_id=res.data['id'])
        if qs_pros:
            for process in qs_pros:
                process.name = res.data['product_name']
                process.save()

        row.save()

        return res

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "destroy", False)
        pk = kwargs['pk']

        qs = ItemMaster.objects.filter(bom_division_id=pk)
        if qs:
            row = qs.get(bom_division_id=pk)
            row.delete()

        return super().destroy(request, request, *args, **kwargs)


class BomMasterSelectViewSet(viewsets.ModelViewSet):
    class BomMasterFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = BomMaster
            fields = ['bom_number', 'product_name', 'model_name', 'master_customer__name', 'created_at',
                      'item', 'required_amount']

    queryset = BomMaster.objects.all()
    serializer_class = BomMasterSelectSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_class = BomMasterFilter
    pagination_class = None

    def get_queryset(self):
        return BomMaster.objects.filter(enterprise=self.request.user.enterprise).all().order_by("-id")


from rest_framework.pagination import PageNumberPagination


class BomMasterViewSet10(viewsets.ModelViewSet):
    class BomMasterFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = BomMaster
            fields = ['bom_number', 'product_name', 'model_name', 'master_customer__name', 'created_at',
                      'item', 'required_amount']

    queryset = BomMaster.objects.all()
    serializer_class = BomMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']  # to remove 'put'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['bom_number', 'nice_number', 'product_name', "brand__name", "item_group__name"]
    filterset_class = BomMasterFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "CustomerMasterViewSet", "get_queryset", False)
        qs = BomMaster.objects.filter(enterprise=self.request.user.enterprise).all().order_by("-id")

        if 'item_code' in self.request.query_params:
            item_code = self.request.query_params['item_code']
            qs = qs.filter(bom_number=item_code)
        elif 'nice' in self.request.query_params:
            nice = self.request.query_params['nice']
            qs = qs.filter(nice_number=nice)

        if 'brand' in self.request.query_params:
            brand = self.request.query_params['brand']
            qs = qs.filter(brand_id=brand)
        if 'item_group' in self.request.query_params:
            item_group = self.request.query_params['item_group']
            qs = qs.filter(item_group_id=item_group)

        return qs
