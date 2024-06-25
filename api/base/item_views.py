import datetime

from django.db import transaction
from django.db.models import Sum
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from api.pagination import PostPageNumberPagination5
from api.QRCode.QRCodeManager import QRCodeGen

from KPI.kpi_views import kpi_log
from api.models import ItemMaster, ItemLed, GroupCodeMaster, CodeMaster, ItemIn, ItemOut, ItemRein
from api.permission import MesPermission
from api.serializers import ItemMasterSerializer, ItemMasterSelectSerializer, ItemLedSerializer, generate_code


class ItemMasterViewSet(viewsets.ModelViewSet):
    created_at = DateFromToRangeFilter()

    class ItemMasterFilter(FilterSet):

        class Meta:
            model = ItemMaster
            fields = ['id']

    queryset = ItemMaster.objects.all()
    serializer_class = ItemMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']  # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemMasterFilter

    pagination_class = PageNumberPagination

    def get_queryset(self):
        # print('ItemMasterViewSet를 탄다 111')  # 첫진입, 검색
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemMasterViewSet", "get_queryset", False)

        started = datetime.datetime.now()
        # print(started)
        qs = ItemMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('-id').all()

        if 'code_i' in self.request.query_params:
            code_i = self.request.query_params['code_i']
            qs = qs.filter(code=code_i)

        if 'code' in self.request.query_params:
            code = self.request.query_params['code']
            qs = qs.filter(code__iexact=code)

        if 'name' in self.request.query_params:
            name = self.request.query_params['name']
            qs = qs.filter(name__contains=name)

        if 'division' in self.request.query_params:
            division = self.request.query_params['division']
            qs = qs.filter(item_division_id=division)

        if 'model' in self.request.query_params:
            model = self.request.query_params['model']
            qs = qs.filter(model_id=model)

        if 'purchase_from' in self.request.query_params:
            purchase_from = self.request.query_params['purchase_from']
            qs = qs.filter(purchase_from=purchase_from)

        if 'bom_division' in self.request.query_params:
            bom_division = self.request.query_params['bom_division']
            qs = qs.filter(bom_division_id=bom_division)

        print(datetime.datetime.now() - started)

        return qs

    # def list(self, request, *args, **kwargs):
    #     return super().list(request, request, *args, **kwargs)

    # 추가
    def create(self, request, *args, **kwargs):
        # print('create를 탄다')
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemMasterViewSet", "create", False)

        ret = request

        if ret.data['qr_path'] is '':
            _mutable = ret.data._mutable
            ret.data._mutable = True

            from api.QRCode.QRCodeManager import QRCodeGen_Code
            filename = QRCodeGen_Code(ret.data['code'], 'ItemMaster')

            # instance['qr_path'] = filename
            ret.data['qr_path'] = filename

            ret.data._mutable = _mutable

        res = super().create(ret, ret, *args, **kwargs)

        return res

    def retrieve(self, request, *args, **kwargs):
        print('리트리브 탄다...?')
        return super().retrieve(request, request, *args, **kwargs)

    # 수정
    def partial_update(self, request, *args, **kwargs):
        print('파살 엽데이트 탄다...?')
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemMasterViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    # QR 생성
    def qr_update(self, request, *args, **kwargs):
        print('qr_update를 탄다...?')
        item_id = request.data['id']
        item_master = ItemMaster.objects.filter(id=item_id)

        for items in item_master:
            if items.qr_path:
                raise ValidationError('QR코드가 이미 존재하는 품목입니다.')

            else:
                bom_code = items.code

                from api.QRCode.QRCodeManager import QRCodeGen_Code
                filename = QRCodeGen_Code(bom_code, 'ItemMaster')

                print(filename)

                # instance['qr_path'] = filename
                items.qr_path = filename
                items.save()

        return Response(status=status.HTTP_200_OK)

    # 삭제
    def destroy(self, request, *args, **kwargs):
        print('디스트로이 탄다...?')
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemMasterViewSet", "destroy", False)

        _qr_filename = request.data.get('qr', "")

        from api.QRCode.QRCodeManager import DeleteQRCode
        try:
            DeleteQRCode(_qr_filename)
            print("아이템에 QR코드 이미지 경로 파일 삭제")
        except:
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemMasterViewSet", "destroy", True)
            raise ValidationError('QR Code 삭제시 에러가 발생했습니다.')

        return super().destroy(request, request, *args, **kwargs)

    # 창고별 재고 계산
    def location(self, request, *args, **kwargs):
        item_id = self.request.query_params['item']

        group = GroupCodeMaster.objects.get(name="창고구분", enterprise=self.request.user.enterprise)
        codes = CodeMaster.objects.filter(group=group)

        item = ItemMaster.objects.get(id=item_id)

        item_in = ItemIn.objects.filter(item=item, enterprise=self.request.user.enterprise)
        item_out = ItemOut.objects.filter(item=item, enterprise=self.request.user.enterprise)
        item_rein = ItemRein.objects.filter(item=item, enterprise=self.request.user.enterprise)

        data = {}

        codes = codes.exclude(name="입고창고")

        item_in_sorted = item_in.exclude(location__in=codes).order_by('-id')
        # print(item_in_sorted)
        if item_in_sorted.exists():
            print("it exists!")
            in_sum = item_in_sorted.aggregate(
                amount_sum=Sum('receive_amount') - Sum('in_faulty_amount')
            )
        else:
            print("it doesn't exists...")
            in_sum = {'amount_sum': 0}

        item_out_sorted = item_out.exclude(location__in=codes).order_by('-id')
        if item_out_sorted.exists():
            out_sum = item_out_sorted.aggregate(
                amount_sum=Sum('out_amount')
            )
        else:
            out_sum = {'amount_sum': 0}

        item_rein_sorted = item_rein.exclude(location__in=codes).order_by('-id')
        if item_rein_sorted.exists():
            rein_sum = item_rein_sorted.aggregate(
                amount_sum=Sum('rein_amount') - Sum('out_faulty_amount')
            )
        else:
            rein_sum = {'amount_sum': 0}
        # for sort in item_in_sorted:
        #     data[sort.location.name] = in_sum['amount_sum'] + rein_sum['amount_sum'] - out_sum['amount_sum']
        print(in_sum, rein_sum, out_sum)
        data['입고창고'] = in_sum['amount_sum'] + rein_sum['amount_sum'] - out_sum['amount_sum']

        for code in codes:
            item_in_sorted = item_in.filter(location=code).order_by('-id')
            if item_in_sorted.exists():
                in_sum = item_in_sorted.aggregate(
                    amount_sum=Sum('receive_amount') - Sum('in_faulty_amount')
                )
            else:
                in_sum = {'amount_sum': 0}

            item_out_sorted = item_out.filter(location=code).order_by('-id')
            if item_out_sorted.exists():
                out_sum = item_out_sorted.aggregate(
                    amount_sum=Sum('out_amount')
                )
            else:
                out_sum = {'amount_sum': 0}

            item_rein_sorted = item_rein.filter(location=code).order_by('-id')
            if item_rein_sorted.exists():
                rein_sum = item_rein_sorted.aggregate(
                    amount_sum=Sum('rein_amount') - Sum('out_faulty_amount')
                )
            else:
                rein_sum = {'amount_sum': 0}
            # for sort in item_in_sorted:
            #     data[sort.location.name] = in_sum['amount_sum'] + rein_sum['amount_sum'] - out_sum['amount_sum']
            print(in_sum, rein_sum, out_sum)
            data[code.name] = in_sum['amount_sum'] + rein_sum['amount_sum'] - out_sum['amount_sum']

        print(data)
        return Response(data, status=status.HTTP_200_OK)

    # 창고 이동
    @transaction.atomic
    def location_move(self, request, *args, **kwargs):
        print(request.data)
        location_in = request.data['location_in']
        location_out = request.data['location_out']
        item_amount = request.data['item_amount']
        item = request.data['item']

        location = CodeMaster.objects.filter(enterprise=self.request.user.enterprise)

        location_in_name = location.get(id=location_in)
        location_out_name = location.get(id=location_out)

        item_in = ItemIn.objects.create(
            item_id=item,
            location_id=location_in,
            receive_amount=item_amount,
            in_faulty_amount=0,

            etc="재고이동(" + location_out_name.name + " -> " + location_in_name.name + ")",
            in_at=datetime.date.today(),
            item_created_at=datetime.date.today(),

            enterprise=self.request.user.enterprise,
            created_at=datetime.date.today(),
            created_by=self.request.user,
            updated_at=datetime.date.today(),
            updated_by=self.request.user,
        )
        item_in.num = generate_code('I', ItemIn, 'num', self.request.user)
        item_in.current_amount = ItemMaster.objects.get(pk=item).stock

        dict_qr = {'id': item_in.id, 'item_id': item}
        filename = QRCodeGen(dict_qr, 'ItemIn')
        print(filename)

        item_in.qr_path = filename
        item_in.save()

        item_out = ItemOut.objects.create(
            item_id=item,
            location_id=location_out,
            out_amount=item_amount,

            purpose="재고이동(" + location_out_name.name + " -> " + location_in_name.name + ")",
            out_at=datetime.date.today(),

            enterprise=self.request.user.enterprise,
            created_at=datetime.date.today(),
            created_by=self.request.user,
            updated_at=datetime.date.today(),
            updated_by=self.request.user,
        )
        item_out.num = generate_code('O', ItemOut, 'num', self.request.user)
        item_out.current_amount = ItemMaster.objects.get(pk=item).stock

        dict_qr = {'id': item_out.id, 'item_id': item}
        filename = QRCodeGen(dict_qr, 'ItemOut')
        print(filename)

        item_out.qr_path = filename
        item_out.save()

        data = {
            'location_in': location_in_name.name,
            'location_out': location_out_name.name
        }

        print(data)
        return Response(data, status=status.HTTP_200_OK)


class ItemMasterViewSet5(viewsets.ModelViewSet):
    created_at = DateFromToRangeFilter()

    class ItemMasterFilter(FilterSet):

        class Meta:
            model = ItemMaster
            fields = ['id']

    queryset = ItemMaster.objects.all()
    serializer_class = ItemMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']  # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemMasterFilter

    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        print('ItemMasterViewSet5를 탄다 222')
        qs = ItemMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('-id').all()

        if 'code' in self.request.query_params:
            code = self.request.query_params['code']
            qs = qs.filter(code__iexact=code)

        if 'name' in self.request.query_params:
            name = self.request.query_params['name']
            qs = qs.filter(name__contains=name)

        if 'division' in self.request.query_params:
            division = self.request.query_params['division']
            qs = qs.filter(item_division_id=division)

        if 'model' in self.request.query_params:
            model = self.request.query_params['model']
            qs = qs.filter(model_id=model)

        if 'purchase_from' in self.request.query_params:
            purchase_from = self.request.query_params['purchase_from']
            qs = qs.filter(purchase_from=purchase_from)

        if 'bom_division' in self.request.query_params:
            bom_division = self.request.query_params['bom_division']
            qs = qs.filter(bom_division_id=bom_division)

        return qs


class ItemMasterSelectViewSet(viewsets.ModelViewSet):
    created_at = DateFromToRangeFilter()

    class ItemMasterFilter(FilterSet):
        class Meta:
            model = ItemMaster
            fields = ['id']

    queryset = ItemMaster.objects.all()
    serializer_class = ItemMasterSelectSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemMasterFilter
    pagination_class = None

    def get_queryset(self):
        print('ItemMasterSelectViewSet를 탄다 333')
        qs = ItemMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('-id').all()
        print(qs.values())
        return qs


class ItemMasterPartViewSet(viewsets.ModelViewSet):
    created_at = DateFromToRangeFilter()

    class ItemMasterFilter(FilterSet):
        class Meta:
            model = ItemMaster
            fields = ['id']

    queryset = ItemMaster.objects.all()
    serializer_class = ItemMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemMasterFilter
    pagination_class = None

    def get_queryset(self):
        print('ItemMasterPartViewSet 탄다 444')
        qs = ItemMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('-id').all()
        return qs


class ItemMasterLedViewSet(viewsets.ModelViewSet):
    created_at = DateFromToRangeFilter()

    class ItemLedFilter(FilterSet):
        class Meta:
            model = ItemLed
            fields = ['id']

    queryset = ItemLed.objects.all()
    serializer_class = ItemLedSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemLedFilter
    pagination_class = None

    def get_queryset(self):
        print('ItemMasterLedViewSet 탄다 555')
        qs = ItemLed.objects.filter(enterprise=self.request.user.enterprise).order_by('id')
        return qs
