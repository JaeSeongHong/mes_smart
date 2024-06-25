from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from requests import Response
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter

from KPI.kpi_views import kpi_log
from api.base.base_form import item_fm
from api.models import ItemIn, ItemMaster, CodeMaster
from api.permission import MesPermission
from api.serializers import ItemInSerializer


class ItemInViewSet(viewsets.ModelViewSet):
    class ItemInMasterFilter(FilterSet):

        class Meta:
            model = ItemIn
            fields = ['id']

    queryset = ItemIn.objects.all()
    serializer_class = ItemInSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["item__name", "item__code", "item__nice_number", "item__brand", "item__item_group",
                       "item__shape", "item__safe_amount"]
    filterset_class = ItemInMasterFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemInViewSet", "get_queryset", False)
        qs = ItemIn.objects.filter(enterprise=self.request.user.enterprise).all().order_by('-id')
        # print(self.request.query_params)

        if 'total_search' in self.request.query_params:
            total_search = str(self.request.query_params['total_search'])
            if total_search != '':
                total_search_list = total_search.split()
                total_qs = ItemIn.objects.filter(enterprise=self.request.user.enterprise)

                for item in total_search_list:
                    print(item)
                    total_qs = total_qs.filter(
                        Q(item__brand__name__contains=item) |
                        Q(item__item_group__name__contains=item) |
                        Q(item__name__contains=item) |
                        Q(item__code__contains=item) |
                        Q(item__nice_number__contains=item) |
                        Q(customer__name__contains=item)
                    )

                print(total_qs)
                return total_qs

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(created_at__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(created_at__lte=to_date)

        if 'customer' in self.request.query_params:
            customer = self.request.query_params['customer']
            print(customer)
            qs = qs.filter(customer__id=customer)

        if 'brand' in self.request.query_params:
            brand = self.request.query_params['brand']
            qs = qs.filter(item__brand=brand)

        if 'item_group' in self.request.query_params:
            item_group = self.request.query_params['item_group']
            qs = qs.filter(item__item_group=item_group)

        if 'item_name' in self.request.query_params:
            item_name = self.request.query_params['item_name']
            qs = qs.filter(item=item_name)
        # elif 'item_code' in self.request.query_params:
        #     item_code = self.request.query_params['item_code']
        #     qs = qs.filter(item=item_code)
        elif 'nice_number' in self.request.query_params:
            nice_number = self.request.query_params['nice_number']
            qs = qs.filter(item=nice_number)

        # if 'detail' in self.request.query_params:
        #     detail = self.request.query_params['detail']
        #     qs = qs.filter(item__detail__contains=detail)
        #
        # if 'shape' in self.request.query_params:
        #     shape = self.request.query_params['shape']
        #     qs = qs.filter(item__shape__contains=shape)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemInViewSet", "create", False)

        item_id = request.data.get('item')
        in_price = request.data.get('in_price')
        receive_amount, in_faulty_amount = request.data.get('receive_amount', ""), request.data.get('in_faulty_amount', "")
        # TODO: serializer의 validator로 이동.
        if receive_amount == "" or in_faulty_amount == "":
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemInViewSet", "create", True)
            raise ValidationError('receive_amount / in_faulty_amount 개수 확인 바랍니다. (관리자에게 문의)')
        in_amount = float(receive_amount) - float(in_faulty_amount)

        item = get_object_or_404(ItemMaster, pk=item_id)
        item.stock = item.stock + in_amount
        item.standard_price = in_price  # 표준단가, 마지막에 입고된 단가
        item.save()

        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemInViewSet", "partial_update", False)

        previous = get_object_or_404(ItemIn, pk=kwargs.get('pk'))

        # if previous.created_at != date.today():
        #     raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        # TODO: serializer의 validator로 이동.
        receive_amount, in_faulty_amount = request.data.get('receive_amount', ""), request.data.get('in_faulty_amount', "")
        if receive_amount == "" or in_faulty_amount == "":
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemInViewSet", "partial_update", True)
            raise ValidationError('receive_amount / in_faulty_amount 개수 확인 바랍니다. (관리자에게 문의)')

        diff = float(receive_amount) - float(in_faulty_amount) - previous.in_amount
        previous.item.stock = previous.item.stock + diff

        previous.item.save()
        # previous.save()

        return super().partial_update(request, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemInViewSet", "destroy", False)

        _qr_filename = request.data.get('qr', "")

        # 아이템에 QR코드 이미지 경로 파일 삭제
        from api.QRCode.QRCodeManager import DeleteQRCode
        try:
            DeleteQRCode(_qr_filename)
            print("아이템에 QR코드 이미지 경로 파일 삭제")
        except:
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemInViewSet", "destroy", True)
            raise ValidationError('QR Code 삭제시 에러가 발생했습니다.')

        previous = get_object_or_404(ItemIn, pk=kwargs.get('pk'))

        # if previous.created_at != date.today():
        #     raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        previous.item.stock = previous.item.stock - previous.in_amount
        previous.item.save()

        return super().destroy(request, request, *args, **kwargs)


