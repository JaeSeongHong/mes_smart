from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter, FilterSet
from rest_framework import viewsets, filters
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import ItemMaster, ItemRein
from api.permission import MesPermission
from api.serializers import ItemReinSerializer
from api.pagination import PostPageNumberPagination5, PostPageNumberPagination10


class ItemReinViewSet(viewsets.ModelViewSet):
    class ItemReinFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = ItemRein
            fields = ['item__item_division', 'item__code', 'item__name', 'item__nice_number', 'item__brand',
                      'item__item_group', 'item__type', 'item__model', 'item']

    queryset = ItemRein.objects.all()
    serializer_class = ItemReinSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    search_fields = ["item__name", "item__code", "item__nice_number", "item__brand__name",
                     "item__item_group__name", "customer__name"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ItemReinFilter
    pagination_class = PostPageNumberPagination10

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemReinViewSet", "get_queryset", False)
        qs = ItemRein.objects.filter(enterprise=self.request.user.enterprise).all().order_by('-id')

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(rein_at__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(rein_at__lte=to_date)

        if 'customer' in self.request.query_params:
            customer = self.request.query_params['customer']
            qs = qs.filter(customer__id=customer)

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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemReinViewSet", "create", False)
        ret = super().create(request, request, *args, **kwargs)
        item_id = request.data.get('item')
        rein_amount, out_faulty_amount = request.data.get('rein_amount', None), request.data.get('out_faulty_amount', None)

        try:
            item = ItemMaster.objects.get(pk=item_id)
            # item.stock = item.stock + int(rein_amount) - int(out_faulty_amount)
            item.stock = item.stock + float(rein_amount) - float(out_faulty_amount)
            item.save()
        except:
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemReinViewSet", "create", True)
            raise ValidationError('적절한 수량을 숫자로 입력해 주시기 바랍니다.')

        return ret

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemReinViewSet", "partial_update", False)
        previous = get_object_or_404(ItemRein, pk=kwargs.get('pk'))
        ret = super().partial_update(request, request, *args, **kwargs)

        # if previous.created_at != date.today():
        #     raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        rein_amount, out_faulty_amount = request.data.get('rein_amount', None), request.data.get('out_faulty_amount', None)
        try:
            # newone = int(rein_amount) - int(out_faulty_amount)
            newone = float(rein_amount) - float(out_faulty_amount)

            # oldone = int(previous.rein_amount) - int(previous.out_faulty_amount)
            oldone = float(previous.rein_amount)- float(previous.out_faulty_amount)

            previous.item.stock = previous.item.stock - oldone + newone
            previous.item.save()
        except:
            kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemReinViewSet", "partial_update", True)
            raise ValidationError('적절한 수량을 숫자로 입력해 주시기 바랍니다.')

        return ret

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemReinViewSet", "destroy", False)
        previous = get_object_or_404(ItemRein, pk=kwargs.get('pk'))

        # if previous.created_at != date.today():
        #     raise ValidationError('오늘에 해당하는 객체만 수정/삭제가 가능합니다.')

        previous.item.stock = previous.item.stock - (previous.rein_amount - previous.out_faulty_amount)
        # previous.item.stock = previous.item.stock - previous.rein_amount
        previous.item.save()

        return super().destroy(request, request, *args, **kwargs)
