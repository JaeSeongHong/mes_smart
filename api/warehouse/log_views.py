from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models import ItemIn, ItemOut, ItemMaster, UserMaster, ItemWarehouseIn, ItemWarehouseOut, ItemWarehouseAdjust
from api.permission import MesPermission
from api.serializers import ItemWarehouseLogSerializer


class ItemWarehouseLogViewSet(viewsets.ModelViewSet):

    queryset = ItemIn.objects.all()
    serializer_class = ItemWarehouseLogSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']
    pagination_class = None

    def get_queryset(self):
        code = self.request.query_params.get('code', 0)     # warehouse code
        # 강제 filtering. model 사용하지 않아 수등으로..
        created_at_after = self.request.query_params.get('created_at_after', '1970-01-01')
        created_at_before = self.request.query_params.get('created_at_before', '9999-12-31')
        item = self.request.query_params.get('item', 0)

        # TODO
        if created_at_before == '':
            created_at_before = '9999-12-31'
        if created_at_after == '':
            created_at_after = '1970-01-01'
        if item == '':
            item = 0

        out = []
        # 입고
        for i in ItemWarehouseIn.objects.filter(item_in__item_id=int(item),
                                                item_in__enterprise=self.request.user.enterprise,
                                                warehouse__code=code,
                                                created_at__gte=created_at_after,
                                                created_at__lte=created_at_before) \
                .values_list('item_in__item',
                             'item_in__receive_amount',
                             'item_in__in_faulty_amount',
                             'item_in__current_amount',
                             'item_in__created_by',
                             'item_in__etc',
                             'item_in__created_at'):
            out.append({
                'item': get_object_or_404(ItemMaster, pk=i[0]),
                'receive_amount': i[1],
                'in_faulty_amount': i[2],
                'current_amount': i[3],
                'created_by': get_object_or_404(UserMaster, pk=i[4]),
                'etc': i[5],
                'created_at': i[6]
            })
        # 출고
        for i in ItemWarehouseOut.objects.filter(item_out__item_id=int(item),
                                                 item_out__enterprise=self.request.user.enterprise,
                                                 warehouse__code=code,
                                                 created_at__gte=created_at_after,
                                                 created_at__lte=created_at_before)\
                .values_list('item_out__item',
                             'item_out__out_amount',
                             'item_out__current_amount',
                             'item_out__created_by',
                             'item_out__purpose',
                             'item_out__etc',
                             'item_out__created_at'):
            out.append({
                'item': get_object_or_404(ItemMaster, pk=i[0]),
                'out_amount': i[1],
                'current_amount': i[2],
                'created_by': get_object_or_404(UserMaster, pk=i[3]),
                'purpose': i[4],
                'etc': i[5],
                'created_at': i[6]
            })

        # 재고실사
        for i in ItemWarehouseAdjust.objects.filter(item_adjust__item_id=int(item),
                                                    item_adjust__enterprise=self.request.user.enterprise,
                                                    warehouse__code=code,
                                                    created_at__gte=created_at_after,
                                                    created_at__lte=created_at_before) \
                .values_list('item_adjust__item',
                             'item_adjust__previous_amount',
                             'item_adjust__current_amount',
                             'item_adjust__created_by',
                             'item_adjust__reason',
                             'item_adjust__created_at'):
            out.append({
                'item': get_object_or_404(ItemMaster, pk=i[0]),
                'previous_amount': i[1],
                'current_amount': i[2],
                'created_by': get_object_or_404(UserMaster, pk=i[3]),
                'purpose': i[4],
                'created_at': i[5]
            })

        return sorted(out, key=lambda x: x['created_at'])

    def list(self, request, *args, **kwargs):
        """자재이력 조회"""
        return super(ItemWarehouseLogViewSet, self).list(request, *args, **kwargs)

