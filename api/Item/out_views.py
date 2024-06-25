from datetime import datetime, time, date, timedelta
from django.db import transaction
from django.db.models import F, Sum
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter, FilterSet
from rest_framework import viewsets, filters
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from KPI.kpi_views import kpi_log
from api.models import ItemOut, ItemMaster, ItemIn, CodeMaster, GroupCodeMaster, ItemRein
from api.permission import MesPermission
from api.serializers import ItemOutSerializer
from api.pagination import PostPageNumberPagination5, PostPageNumberPagination10
from rest_framework import viewsets, status

from itertools import groupby
from dateutil.relativedelta import relativedelta
from datetime import datetime
from operator import itemgetter


class ItemOutViewSet(viewsets.ModelViewSet):
    class ItemOutFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemOut
            fields = ['item__item_division', 'item__code', 'item__name', 'item__brand', 'item__item_group',
                      'item__nice_number', 'item__type', 'item__model', 'item']
            # fields = ['created_at', 'item', 'num', 'location']

    queryset = ItemOut.objects.all()
    serializer_class = ItemOutSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend, OrderingFilter, filters.SearchFilter]
    ordering_fields = ["item__name", "item__code", "item__nice_number"]
    search_fields = ["item__name", "item__code", "item__nice_number", "item__brand__name",
                     "item__item_group__name", "purchase_from__name"]
    filterset_class = ItemOutFilter
    pagination_class = PostPageNumberPagination10

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemOutViewSet", "get_queryset", False)
        qs = ItemOut.objects.filter(enterprise=self.request.user.enterprise).all().order_by('-id')

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(out_at__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(out_at__lte=to_date)

        if 'customer' in self.request.query_params:
            customer = self.request.query_params['customer']
            qs = qs.filter(purchase_from__id=customer)

        if 'brand' in self.request.query_params:
            brand = self.request.query_params['brand']
            qs = qs.filter(item__brand=brand)

        if 'item_group' in self.request.query_params:
            item_group = self.request.query_params['item_group']
            qs = qs.filter(item__item_group=item_group)

        if 'item_code' in self.request.query_params:
            item_code = self.request.query_params['item_code']
            qs = qs.filter(item=item_code)
        elif 'nice_number' in self.request.query_params:
            nice_number = self.request.query_params['nice_number']
            qs = qs.filter(item=nice_number)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemOutViewSet", "create", False)
        ret = super().create(request, request, *args, **kwargs)

        # TODO: serializer의 validator로 이동.
        item_id = request.data.get('item')
        out_amount = request.data.get('out_amount')

        try:
            item = ItemMaster.objects.get(pk=item_id)
            item.stock = item.stock - float(out_amount)
            item.save()
        except ValueError:
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemOutViewSet", "create", True)
            raise ValidationError('적절한 출고수량을 숫자로 입력해 주시기 바랍니다.')

        return ret

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemOutViewSet", "partial_update", False)

        print(request.data)
        previous = get_object_or_404(ItemOut, pk=kwargs.get('pk'))
        out_amount = request.data.get('out_amount')
        diff = previous.out_amount - float(out_amount)

        location = request.data.get('location')

        # if location == "" or location is None:
        #     code = CodeMaster.objects.get(name="입고창고")
        #     previous.location = code
        # else:
        #     code = CodeMaster.objects.get(id=location)
        #     previous.location = code

        # if previous.created_at != date.today():
        #     raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        previous.item.stock = previous.item.stock + diff
        previous.item.save()

        return super().partial_update(request, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemOutViewSet", "destroy", False)
        previous = get_object_or_404(ItemOut, pk=kwargs.get('pk'))

        # if previous.created_at != date.today():
        #     raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        previous.item.stock = previous.item.stock + previous.out_amount
        previous.item.save()

        return super().destroy(request, request, *args, **kwargs)

    def graph(self, request, *args, **kwargs):
        name_filter = request.data['name_filter']
        # category = request.data['category']
        # selected = request.data['selected']
        if 'year' in request.data:
            out_year = request.data['year']
            out_month = request.data['month']

            qs = ItemOut.objects.filter(enterprise=self.request.user.enterprise).order_by('-id').all(). \
                filter(out_at__year=out_year, out_at__month=out_month)
            qs_ret = qs.values(name_filter).annotate(total=Sum('out_amount')).order_by(name_filter)

        if 'start_year' in request.data:
            start_year = request.data['start_year']
            start_month = request.data['start_month']
            end_year = request.data['end_year']
            end_month = request.data['end_month']

            start_date = datetime.strptime(start_year + '-' + start_month + '-' + '01', '%Y-%m-%d')

            if end_month in ['04', '06', '09', '11']:
                end_date = datetime.strptime(end_year + '-' + end_month + '-' + '30', '%Y-%m-%d')
            elif end_month == '02':
                if int(end_year) % 4 == 0 and (int(end_year) % 100 != 0 or int(end_year) % 400 == 0):
                    end_date = datetime.strptime(end_year + '-' + end_month + '-' + '29', '%Y-%m-%d')
                else:
                    end_date = datetime.strptime(end_year + '-' + end_month + '-' + '28', '%Y-%m-%d')
            else:
                end_date = datetime.strptime(end_year + '-' + end_month + '-' + '31', '%Y-%m-%d')

            qs = ItemOut.objects.filter(enterprise=self.request.user.enterprise).order_by('-out_at').all(). \
                filter(out_at__range=[start_date, end_date])
            qs_ret = qs.values(name_filter, 'out_at__year', 'out_at__month').annotate(total=Sum('out_amount')). \
                order_by(name_filter, 'out_at__year', 'out_at__month')

        # if selected:
        #     if category == '브랜드':
        #         print(category)
        #         qs = ItemOut.objects.filter(enterprise=self.request.user.enterprise).\
        #             order_by('-id').all().filter(item__type__id__in=selected,
        #                                          out_at__year=out_year, out_at__month=out_month)
        #         qs_ret = qs.values(name=F(name_filter)).annotate(total=Sum('out_amount')).order_by(name_filter)
        #
        #     elif category == '제품군':
        #         print(category)
        #         qs = ItemOut.objects.filter(enterprise=self.request.user.enterprise).\
        #             order_by('-id').all().filter(item__model__id__in=selected,
        #                                          out_at__year=out_year, out_at__month=out_month)
        #         qs_ret = qs.values(name=F(name_filter)).annotate(total=Sum('out_amount')).order_by(name_filter)
        #
        #     elif category == 'Scent':
        #         print(category)
        #         qs = ItemOut.objects.filter(enterprise=self.request.user.enterprise).\
        #             order_by('-id').all().filter(item__color__id__in=selected,
        #                                          out_at__year=out_year, out_at__month=out_month)
        #         qs_ret = qs.values(name=F(name_filter)).annotate(total=Sum('out_amount')).order_by(name_filter)
        #
        # else:
        #     qs = ItemOut.objects.filter(enterprise=self.request.user.enterprise).order_by('-id').all(). \
        #         filter(out_at__year=out_year, out_at__month=out_month)
        #     qs_ret = qs.values(name=F(name_filter)).annotate(total=Sum('out_amount')).order_by(name_filter)

        dics = []
        exist_date = []
        names = []
        if qs_ret:

            id = 0
            for row in qs_ret:
                dic = {}
                dic['id'] = id
                dic['name'] = row[name_filter]
                dic['total'] = row['total']
                if dic['name'] is None:
                    dic['name'] = '기타'
                if len(str(row['out_at__month'])) is 1:
                    row['out_at__month'] = '0' + str(row['out_at__month'])
                if 'out_at__year' in row:
                    dic['date'] = str(row['out_at__year']) + "-" + str(row['out_at__month'])
                if dic['date'] not in exist_date:
                    exist_date.insert(0, dic['date'])
                if dic['name'] not in names:
                    names.insert(0, dic['name'])
                dics.append(dic)
                id += 1

                # length = request.data['length']
        exist_date.sort()
        #건강 2,12 / 휴 6 / 아토 9

        length = len(dics)
        for date in exist_date:
            for name in names:
                try:
                    if next(item for item in dics if item["name"] == name and item["date"] == date):
                        pass
                except StopIteration:
                    append = {}
                    append['id'] = length
                    append['name'] = name
                    append['total'] = 0
                    append['date'] = date
                    dics.append(append)
                    length += 1

        data = sorted(dics, key=itemgetter('name', 'date'))
        return Response(data, status=status.HTTP_200_OK)
