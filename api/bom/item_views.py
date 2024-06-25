from datetime import date

from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, BooleanFilter
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Bom, ItemIn, ItemOut
from api.permission import MesPermission
from api.serializers import BomSerializer, ItemMasterSerializer, ItemOutSerializer


class BomItemViewSet(viewsets.ModelViewSet):

    # queryset = Bom.objects.all()
    # serializer_class = BomSerializer
    permission_classes = [IsAuthenticated, MesPermission]

    def get_bom_amount(self, source):
        bom_list = source.get('bom_list', None)
        amount_list = source.get('amount_list', None)

        if bom_list is None or amount_list is None:
            raise ValidationError('BOM과 수량을 확인해 주시기 바랍니다.')

        bom_list = bom_list.split(',')
        amounts = amount_list.split(',')
        if len(bom_list) != len(amounts):
            raise ValidationError('BOM과 수량을 확인해 주시기 바랍니다.')

        return bom_list, amounts

    @transaction.atomic
    def list(self, request, *args, **kwargs):
        bom_list, amounts = self.get_bom_amount(request.query_params)

        items = {}
        boms = Bom.objects.filter(master_id__in=bom_list)
        for i, bom in enumerate(boms):
            if bom.item_id not in items:
                res = ItemIn.objects.filter(item=bom.item)
                current_amount = 0
                if res.exists() is True:
                    current_amount = bom.item.stock

                items[bom.item_id] = {
                    'item': ItemMasterSerializer(bom.item).data,
                    'required_amount': 0,
                    'current_amount': current_amount,
                    'bom': BomSerializer(bom).data
                }

            amount_index = bom_list.index(str(bom.master_id))
            items[bom.item_id]['required_amount'] = bom.required_amount * int(amounts[amount_index]) + items[bom.item_id]['required_amount']

        # Convert
        res = []
        for k, v in items.items():
            res.append(v)

        return Response(res, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        bom_list, amounts = self.get_bom_amount(request.data)

        items = {}
        boms = Bom.objects.filter(master_id__in=bom_list)
        for i, bom in enumerate(boms):
            if bom.item_id not in items:
                items[bom.item_id] = {
                    'item': ItemMasterSerializer(bom.item).data,
                    'required_amount': 0,
                }

            amount_index = bom_list.index(str(bom.master_id))
            items[bom.item_id]['required_amount'] = bom.required_amount * int(amounts[amount_index]) + \
                items[bom.item_id]['required_amount']

        # TODO: ItemOutSerializer로 하면 편할텐데..
        for k, v in items.items():
            out = ItemOut(item_id=k, out_at=date.today(), out_amount=v['required_amount'], purpose='자재출고반영',
                          enterprise=request.user.enterprise, created_by=request.user, updated_by=request.user)
            out.num = self.generate_code('O', ItemOut, 'num')
            out.save()

        return Response({}, status=status.HTTP_200_OK)

    # TODO: delete it after refactoring
    def generate_code(self, prefix1, model, model_field_prefix):
        today = date.today()
        prefix2 = str(today.year * 10000 + today.month * 100 + today.day)
        kwargs = {
            model_field_prefix + '__istartswith': prefix1 + prefix2,
            'enterprise': self.request.user.enterprise
        }
        res = model.objects.filter(**kwargs)
        if res.exists():
            count = res.count()
            if count > 9:
                num = '00' + str(count + 1)
            elif count > 99:
                num = '0' + str(count + 1)
            else:
                num = str(count + 1)
        else:
            return prefix1 + str(int(prefix2) * 1000)

        return prefix1 + str(int(prefix2) * 1000 + int(num))
