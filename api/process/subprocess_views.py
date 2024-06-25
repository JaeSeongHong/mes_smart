import traceback
from datetime import datetime

from django.db import transaction
from django.db.models import Q, F, Sum, Max, Count
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from KPI.kpi_views import kpi_log
from api.models import Subprocess, SubprocessLog, ItemIn, ItemOut
from api.pagination import PostPageNumberPagination5
from api.permission import MesPermission
from api.serializers import SubprocessSerializer


class SubprocessManagementViewSet(viewsets.ModelViewSet):
    queryset = Subprocess.objects.all()
    serializer_class = SubprocessSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['process', "type__id"]
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessManagementViewSet", "get_queryset", False)
        return Subprocess.objects.filter(enterprise=self.request.user.enterprise).order_by('type')

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessManagementViewSet", "create", False)
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessManagementViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessManagementViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)

    def graph(self, request, *args, **kwargs):
        print(request.data)

        product = request.data['product_name']
        fr_date = request.data['actual_fr_date']
        to_date = request.data['actual_to_date']

        qs = Subprocess.objects.filter(enterprise=self.request.user.enterprise, process__has_fault_reason=True).\
            filter(process__name=product,  actual_fr_date__gte=fr_date, actual_to_date__lte=to_date)

        print(qs)

        col_cnt = qs.aggregate(col_cnt=Max('fault_reason__col_cnt'))
        row_cnt = qs.aggregate(row_cnt=Max('fault_reason__row_cnt'))

        qs_ret = qs.values('type__name').\
            annotate(
            R1_lower=F('fault_reason__R01_lower__name'), R2_lower=F('fault_reason__R02_lower__name'), R3_lower=F('fault_reason__R03_lower__name'),
            R4_lower=F('fault_reason__R04_lower__name'), R5_lower=F('fault_reason__R05_lower__name'), R6_lower=F('fault_reason__R06_lower__name'),
            R7_lower=F('fault_reason__R07_lower__name'), R8_lower=F('fault_reason__R08_lower__name'), R9_lower=F('fault_reason__R09_lower__name'),
            R10_lower=F('fault_reason__R10_lower__name'), R11_lower=F('fault_reason__R11_lower__name'), R12_lower=F('fault_reason__R12_lower__name'),
            R13_lower=F('fault_reason__R13_lower__name'), R14_lower=F('fault_reason__R14_lower__name'), R15_lower=F('fault_reason__R15_lower__name'),
            R1=Sum('fault_reason__R01_amount'), R2=Sum('fault_reason__R02_amount'), R3=Sum('fault_reason__R03_amount'),
            R4=Sum('fault_reason__R04_amount'), R5=Sum('fault_reason__R05_amount'), R6=Sum('fault_reason__R06_amount'),
            R7=Sum('fault_reason__R07_amount'), R8=Sum('fault_reason__R08_amount'), R9=Sum('fault_reason__R09_amount'),
            R10=Sum('fault_reason__R10_amount'), R11=Sum('fault_reason__R11_amount'), R12=Sum('fault_reason__R12_amount'),
            R13=Sum('fault_reason__R13_amount'), R14=Sum('fault_reason__R14_amount'), R15=Sum('fault_reason__R15_amount'),
            ).order_by('id')

        data = [{'subpro_name':[]}, {'lower':[]}, {'datas':[]}]

        for item in qs_ret:
            if item['type__name'] not in data[0]['subpro_name']:
                data[0]['subpro_name'].append(item['type__name'])

        for item in qs_ret:
            for num in range(col_cnt['col_cnt']):
                if item['R' + str(num + 1) + '_lower'] not in data[1]['lower']:
                    if item['R' + str(num + 1) + '_lower'] is None:
                        continue
                    data[1]['lower'].append(item['R' + str(num+1) + '_lower'])

        for row in range(len(data[1]['lower'])):
            data[2]['datas'].append([0] * row_cnt['row_cnt'])

        for item in qs_ret:
            for num in range(col_cnt['col_cnt']):
                if item['R' + str(num + 1) + '_lower'] not in data[1]['lower']:
                    if item['R' + str(num + 1) + '_lower'] is None:
                        continue
                data[2]['datas'][data[1]['lower'].index(item['R' + str(num + 1) + '_lower'])][data[0]['subpro_name'].index(item['type__name'])] += item['R' + str(num+1)]

        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete_recent(self, request, *args, **kwargs):
        print(self.request.query_params)
        process_id = self.request.query_params['process']
        subprocess = Subprocess.objects.filter(enterprise=self.request.user.enterprise,
                                               process_id=process_id
                                               ).order_by('-pk')[0]
        sub_log = SubprocessLog.objects.filter(subprocess=subprocess)
        item_in = ItemIn.objects.filter()
        item_out = ItemOut.objects.filter()

        print(sub_log)
        try:
            for log in sub_log:
                if log.itemIn_id is not None:
                    select_in = item_in.get(id=log.itemIn_id)
                    item = select_in.item
                    item.stock = item.stock - select_in.package_amount

                    item.save()
                    select_in.delete()
                    log.delete()

                elif log.itemOut_id is not None:
                    select_out = item_out.get(id=log.itemOut_id)
                    item = select_out.item
                    item.stock = item.stock + select_out.out_amount

                    item.save()
                    select_out.delete()
                    log.delete()

            subprocess.delete()
            data = {'results': 'ok'}
            return JsonResponse(data)
        except Exception as e:
            print(e)
            print(traceback.format_exc())

            data = {'results': 'error'}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


class SubprocessManagementAlertViewSet(viewsets.ModelViewSet):
    queryset = Subprocess.objects.all()
    serializer_class = SubprocessSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['process']
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessManagementViewSet", "get_queryset", False)
        qs = Subprocess.objects.filter(enterprise=self.request.user.enterprise)
        qs = qs.filter(~Q(status="완료")).order_by('fr_date')

        return qs


class SubprocessManagementLookupViewSet(viewsets.ModelViewSet):
    queryset = Subprocess.objects.all()
    serializer_class = SubprocessSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['process']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessManagementViewSet", "get_queryset", False)
        qs = Subprocess.objects.filter(enterprise=self.request.user.enterprise)

        return qs