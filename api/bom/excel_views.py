from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.views import View
from openpyxl import load_workbook
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.bom.excel import excel_parser
from api.models import CustomerMaster, CodeMaster, ItemMaster, BomMaster, UserMaster, Bom
from api.serializers import BomSerializer, ItemMasterSerializer, CustomerMasterSerializer, CodeMasterSerializer


def gen_customer_master(eid, name, request, i):
    # to get a validate "code"
    qsc = CustomerMaster.objects.filter(enterprise__id=eid).order_by('-code')
    code = qsc.first().code + 1 if qsc.exists() else 1

    # new customer_master
    cs = CustomerMasterSerializer(data={
        'code': code,
        'division': None,
        'name': name,
        'licensee_number': "_",
        'owner_name': "_",
        'office_phone': "_",
        'office_fax': "_",
        'charge_name': "_",
        'charge_phone': "_"
    }, context={'request': request})
    if cs.is_valid() is False:
        raise ValidationError('{} 행의 \'{}\'에 문제가 있습니다: {}'.format(i + 1, name, cs.errors))

    cs.save()
    return cs


class BomExcelView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)
        excel = request.FILES.get('excel')

        wb = load_workbook(excel, data_only=True)
        ws = wb.worksheets[0]

        doesnotexists_field = ""
        bommaster = BomMaster.objects.filter()
        bommaster_saved = ""
        bom = Bom.objects.filter()
        itemmaster = ItemMaster.objects.filter()

        for row in ws:
            if row[0].value == '품번':
                pass
            elif row[0].value == "" or row[0].value is None:
                if row[4].value == "" or row[4].value is None:
                    pass
                else:
                    try:
                        bommaster_filter = bommaster.get(enterprise=user.enterprise, bom_number=bommaster_saved)
                    except BomMaster.DoesNotExist:
                        pass
                    else:
                        try:
                            item = itemmaster.get(enterprise=user.enterprise, code=row[4].value)
                        except ItemMaster.DoesNotExist:
                            pass
                        else:
                            try:
                                bom_filter = bom.get(enterprise=user.enterprise, item=item, master=bommaster_filter)
                            except Bom.DoesNotExist:
                                Bom.objects.create(
                                    master=bommaster_filter,
                                    item=item,
                                    required_amount=row[9].value if row[9].value is not None else 0,
                                    enterprise=user.enterprise,
                                    created_by=user,
                                    updated_by=user
                                )
                            else:
                                bom_filter.master = bommaster_filter
                                bom_filter.item = item
                                bom_filter.required_amount = row[9].value if row[9].value is not None else 0
                                bom_filter.updated_by = user
                                bom_filter.save()
            else:
                bommaster_saved = row[0].value
                try:
                    bommaster_filter = bommaster.get(enterprise=user.enterprise, bom_number=bommaster_saved)
                except BomMaster.DoesNotExist:
                    # doesnotexists_field += bommaster_saved + ", "
                    pass
                else:
                    try:
                        item = itemmaster.get(enterprise=user.enterprise, code=row[4].value)
                    except ItemMaster.DoesNotExist:
                        pass
                    else:
                        try:
                            bom_filter = bom.get(enterprise=user.enterprise, item=item, master=bommaster_filter)
                        except Bom.DoesNotExist:
                            Bom.objects.create(
                                master=bommaster_filter,
                                item=item,
                                required_amount=row[9].value if row[9].value is not None else 0,
                                enterprise=user.enterprise,
                                created_by=user,
                                updated_by=user
                            )
                        else:
                            bom_filter.master = bommaster_filter
                            bom_filter.item = item
                            bom_filter.required_amount = row[9].value if row[9].value is not None else 0
                            bom_filter.updated_by = user
                            bom_filter.save()

        context = {}
        return JsonResponse(context)

    # @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     excel = request.FILES['excel']
    #     master = request.data.get('master', None)
    #     if master is None or master == "undefined":
    #         raise ValidationError('정상적인 마스터 ID 형식(master id)이 아닙니다. 관리자에게 문의하세요.')
    #
    #     base = 'data/'
    #     prefix = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
    #     path = base + prefix + excel.name
    #     with open(path, 'wb+') as f:
    #         for chunk in excel.chunks():
    #             f.write(chunk)
    #
    #
    #     # print(items)
    #     eid = request.user.enterprise.id
    #     master_qs = BomMaster.objects.filter(pk=master)
    #     if master_qs.count() != 1:
    #         raise ValidationError('정상적인 BOM 형식 (bom_master id)이 아닙니다. 관리자에게 문의하세요.')
    #     master_obj = master_qs.first()
    #     items = excel_parser(path, master_obj)
    #
    #     master_qs.first().bom_set.all().delete()      # BOM 덮어쓰기 요청 반영.
    #     for i, item in enumerate(items):
    #         # 거래처, 고객사
    #         # TODO: name은 unique 아니기 때문에, 처음 것만 가져옴
    #         if 'manufacturer' in item:
    #             qs = CustomerMaster.objects.filter(name=item['manufacturer'], enterprise__id=eid)
    #             if qs.exists() is False:
    #                 ret = gen_customer_master(eid, item['manufacturer'], request, i)
    #                 item['manufacturer'] = ret.data['id']
    #             else:
    #                 item['manufacturer'] = qs.first().id
    #
    #         if 'customer' in item:
    #             qs = CustomerMaster.objects.filter(name=item['customer'], enterprise__id=eid)
    #             if qs.exists() is False:
    #                 ret = gen_customer_master(eid, item['customer'], request, i)
    #                 item['customer'] = ret.data['id']
    #             else:
    #                 item['customer'] = qs.first().id
    #
    #         if 'storage' in item:
    #             qs = CodeMaster.objects.filter(group__code=109, name=item['storage'], enterprise__id=eid)
    #             if qs.exists() is False:
    #                 raise ValidationError('{} 행에 문제가 있습니다: {}'.format(i + 1, '"' + item['storage'] + '" 생산공정(창고)를 코드마스터에서 찾을 수 없습니다.'))
    #             elif qs.count() > 1:
    #                 raise ValidationError('{} 행에 문제가 있습니다: {}'.format(i + 1, '코드마스터에 동일한 생산공정(창고)명이 복수개 존재합니다('+item['storage']+').'))
    #
    #             item['storage'] = qs.first().id
    #
    #         # item이 없거나 없는 품목일 경우 생성
    #         ic = ItemMaster.objects.filter(code=item.get('item', ''), enterprise=self.request.user.enterprise)
    #         if 'item' not in item or ic.exists() is False:
    #             isin = {'code': item.get('item', '')}  # TODO:
    #
    #             part = str(item.get('part', ''))
    #             part_num = str(item.get('part_num', ''))
    #             if 'item_name' in item:
    #                 isin['name'] = item['item_name']
    #                 isin['detail'] = (part + " " + part_num)[:64] if 'part_num' in item else part[:64]
    #             else:
    #                 isin['name'] = (part + " " + part_num)[:20] if 'part_num' in item else part[:20]
    #                 isin['detail'] = isin['name']
    #
    #             # name blank일 경우 강제로 . 삽입
    #             # if isin['name'].strip() == '':
    #             #     isin['name'] = 'BOM 자동생성'
    #
    #             # detail blank일 경우 강제로 . 삽입
    #             if isin['detail'].strip() == '':
    #                 isin['detail'] = 'BOM 자동생성'
    #
    #             if 'manufacturer' in item:
    #                 isin['purchase_from_id'] = item['manufacturer']
    #             if 'customer' in item:
    #                 isin['sales_to_id'] = item['customer']
    #             if 'unit' in item:
    #                 isin['unit_id'] = item['unit']
    #
    #             iss = ItemMasterSerializer(data=isin, context={'request': request})
    #             if iss.is_valid() is False:
    #                 raise ValidationError('{} 행에 문제가 있습니다:{}'.format(i + 1, ','.join(list(map(lambda x: iss.errors[x][0], iss.errors)))))
    #
    #             iss.save()
    #             item['item'] = iss.data['id']
    #         else:
    #             item['item'] = ic.first().id
    #
    #         item['master'] = master
    #         item['enterprise'] = eid
    #
    #         s = BomSerializer(data=item, context={'request': request})
    #         if s.is_valid() is False:
    #             raise ValidationError(
    #                 '{} 행에 문제가 있습니다:{}'.format(i + 1, ', '.join(list(map(lambda x: s.errors[x][0], s.errors)))))
    #         s.save()
    #
    #     return Response(status=status.HTTP_200_OK)
