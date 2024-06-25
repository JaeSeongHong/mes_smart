from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.base.base_form import customer_fm
from api.models import CustomerMaster, ItemMaster, UnitPrice, UserMaster
from api.permission import MesPermission
from api.serializers import CustomerMasterSerializer, CustomerMasterSelectSerializer, CustomerMasterPartSerializer, \
    UnitPriceSerializer
from rest_framework.pagination import PageNumberPagination

from msgs import msg_pk, msg_update_fail, msg_error, msg_delete_fail
from datetime import datetime


def customer_unitprice(request):
    try:
        results = ItemMaster.objects.all().filter(enterprise__id=request.COOKIES.get('enterprise_id')).order_by('-id')
        # CU = customer_fm(request.GET, request.COOKIES['enterprise_name'])
        context = {}
        context['cu'] = customer_fm(request.GET, request.COOKIES['enterprise_name'])
        context['data'] = results
        data = {
            'data': [{
                'id': re.id,
                'code': re.code,
                'name': re.name,
                'detail': re.detail,
                'model': re.model
            } for re in results]
        }

    except Exception as ex:

        print(ex)

    return render(request, 'basic_information/customer_unitprice.html', context)


class UnitPriceSubViewSet(viewsets.ModelViewSet):
    queryset = UnitPrice.objects.all()
    serializer_class = UnitPriceSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']  # to remove 'put'
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnitPriceSubViewSet", "get_queryset", False)
        filtertype = self.request.query_params.get('type')  #
        if filtertype == "s":
            qs = UnitPrice.objects.filter(enterprise_id=self.request.user.enterprise_id,
                                          item_id=self.request.query_params.get('item_id'),
                                          customer_id=self.request.query_params.get('customer_id'),
                                          division_id=self.request.query_params.get('division_id'),
                                          del_flag='N').order_by('-id')
        else:
            qs = UnitPrice.objects.filter(enterprise_id=self.request.user.enterprise_id,
                                          item_id=self.request.query_params.get('item_id'),
                                          del_flag='N').order_by('-id')
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnitPriceSubViewSet", "create", False)

        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnitPriceSubViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnitPriceSubViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)


class customer_unitprice_update(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def post(self, request):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        pk = request.POST.get('pk', '')
        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        division = request.POST.get('division', '')
        if division == '':
            division = None
        else:
            division = int(division)

        unit_price = request.POST.get('unit_price', '')
        fee_rate = request.POST.get('fee_rate', '')
        etc = request.POST.get('etc', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:

            obj = UnitPrice.objects.get(pk=int(pk))

            obj.division_id = division  # 거래구분
            obj.etc = etc  # 비고

            obj.updated_by = user  # 최종 작성자
            obj.updated_at = d_today  # 최종 작성일

            obj.unit_price = unit_price  # 단가
            obj.fee_rate = fee_rate  # 수수료

            obj.save()

            if obj:
                context = get_res(context, obj)
            else:
                msg = msg_update_fail
                return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    # 수정할 때는 발생하지 않는 에러일텐데? 일단 냅둠.
                    msg = '중복된 거래처가 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


def get_res(context, obj):
    context['id'] = obj.id
    context['etc'] = obj.etc
    context['division_id'] = obj.division.id
    context['updated_at'] = obj.updated_at
    context['updated_by_id'] = obj.updated_by.id
    context['unit_price'] = obj.unit_price
    context['fee_rate'] = obj.fee_rate

    return context


class customer_unitprice_delete(View):
    @transaction.atomic
    def post(self, request):
        pk = request.POST.get('pk', '')
        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = UnitPrice.objects.get(pk=int(pk))
            inv.del_flag = 'Y'
            inv.save()
        except Exception as e:
            msg = msg_delete_fail
            return JsonResponse({'error': True, 'message': msg})

        context = {}
        context['id'] = pk
        return JsonResponse(context)
