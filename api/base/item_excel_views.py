import traceback

import pandas as pd

from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from openpyxl import load_workbook
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.bom.excel import excel_parser
from api.models import CustomerMaster, CodeMaster, ItemMaster, BomMaster, UserMaster
from api.serializers import BomSerializer, ItemMasterSerializer, CustomerMasterSerializer, CodeMasterSerializer


def excel_basic_item_parser(path):
    """ItemMaster 위한 엑셀 파서. 필드만 파싱하여 a list of dictionary 반환. 이후 FK에 대한 매핑 해줘야 함."""
    df = pd.read_excel(path)

    # Retrieve data
    items = []
    for i, row in df.iloc[:].iterrows():
        fields = ('code', 'name', 'g1_standard_type', 'g1_standard', 'unit', 'g1_item_type', 'g1_set', 'g1_stock', 'g1_process')
        item = {}
        for idx, field in enumerate(fields):
            item[field] = row.iloc[idx]

        items.append(item)

    return items


class ItemExcelView(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, ]

    @transaction.atomic

    def create(self, request, *args, **kwargs):
        excel = request.FILES['excel']

        base = 'data/'
        prefix = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        path = base + prefix + excel.name
        with open(path, 'wb+') as f:
            for chunk in excel.chunks():
                f.write(chunk)

        # unit, g1_process 두개는 FK 찾아야 함.
        items = excel_basic_item_parser(path)
        insert = []
        for idx, item in enumerate(items):
            one = {}
            for k, v in item.items():
                if k == 'unit':
                    unit = CodeMaster.objects.filter(enterprise=self.request.user.enterprise,
                                                     group__code=105,
                                                     name=v)
                    if unit.exists() is False:
                        raise ValidationError('{} 열에 문제가 있습니다: 단위가 존재하지 않습니다.'.format(idx + 1))

                    one[k] = unit.first().id
                elif k == 'g1_process':
                    g1_process = CodeMaster.objects.filter(enterprise=self.request.user.enterprise,
                                                           group__code=109,
                                                           name=v)
                    if g1_process.exists() is False:
                        raise ValidationError('{} 열에 문제가 있습니다: 공정이가 존재하지 않습니다.'.format(idx + 1))

                    one[k] = g1_process.first().id
                else:
                    one[k] = v

            insert.append(one)

        ims = ItemMasterSerializer(data=insert, many=True, context={'request': request})
        ims.is_valid(raise_exception=True)
        ims.save()

        return Response(status=status.HTTP_200_OK)


class YuseongItemExcelView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)
        excel = request.FILES.get('excel')

        wb = load_workbook(excel, data_only=True)
        ws = wb.worksheets[0]

        codemaster = CodeMaster.objects.filter()
        bommaster = BomMaster.objects.filter()
        itemmaster = ItemMaster.objects.filter()

        # qs = ItemMaster.objects.filter()

        for row in ws:
            if row[0].value == 'it_id':
                pass
            elif row[0].value == '브랜드':
                break
            elif row[30].value == 0:
                is_box = row[85].value
                box_quantity = row[86].value
                item_group = row[1].value + row[83].value
                code = row[84].value

                try:
                    item_group_query = codemaster.get(enterprise=user.enterprise, explain=item_group)
                    if item_group == "x0":
                        item_group_string = "(요소수필터)"
                        code += item_group_string
                    else:
                        ig_str = str(item_group_query.name).split()
                        item_group_string = "(" + ig_str[-1] + ")"
                        code += item_group_string
                except:
                    pass

                if is_box != "":
                    box_string = "(박스" + is_box + "수량" + box_quantity + ")"
                    code += box_string

                try:
                    deleted = itemmaster.get(enterprise=user.enterprise, code=code)
                    bom_division = deleted.bom_division_id
                    bom_deleted = bommaster.get(enterprise=user.enterprise, id=bom_division)
                    deleted.delete()
                    bom_deleted.delete()
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    pass
            else:
                # TODO: 나이스번호 브랜드 제품군 수정 후 재삽입
                code = row[84].value
                name = row[6].value
                # nice_number = row[80].value + row[81].value + row[82].value + row[83].value
                nice_number = row[80].value
                standard_price = row[24].value
                item_group = row[1].value + row[83].value
                brand = row[82].value

                is_box = row[85].value
                box_quantity = row[86].value

                try:
                    item_group_query = codemaster.get(enterprise=user.enterprise, explain=item_group)
                    if item_group == "x0":
                        item_group_string = "(요소수필터)"
                        code += item_group_string
                    else:
                        ig_str = str(item_group_query.name).split()
                        item_group_string = "(" + ig_str[-1] + ")"
                        code += item_group_string
                except Exception as e:
                    item_group_query = None
                if is_box != "":
                    box_string = "(박스" + is_box + "수량" + box_quantity + ")"
                    code += box_string

                try:
                    brand_query = codemaster.get(enterprise=user.enterprise, explain=brand)
                except Exception as e:
                    brand_query = None
                try:
                    bom_query = bommaster.get(enterprise=user.enterprise, bom_number=code, nice_number=nice_number)
                except Exception as e:
                    bom_query = None
                try:
                    item_query = itemmaster.get(enterprise=user.enterprise, code=code, nice_number=nice_number)
                except Exception as e:
                    item_query = None

                if bom_query:
                    if item_group_query:
                        bom_query.item_group = item_group_query
                    if brand_query:
                        bom_query.brand = brand_query
                    bom_query.price = standard_price
                    bom_query.save()

                    if item_query:
                        if item_group_query:
                            item_query.item_group = item_group_query
                        if brand_query:
                            item_query.brand = brand_query
                        item_query.standard_price = standard_price
                        item_query.bom_division = bom_query
                        item_query.save()
                    else:
                        item_created = ItemMaster.objects.create(
                            created_by=user,
                            updated_by=user,
                            enterprise=user.enterprise,
                            code=code,
                            # bom_number=code,
                            # product_name=name,
                            name=name,
                            nice_number=nice_number,
                            standard_price=standard_price,
                            item_group=item_group_query,
                            brand=brand_query,

                            bom_division_id=bom_query.id
                        )
                        item_created.save()

                else:
                    bom_created = BomMaster.objects.create(
                        created_by=user,
                        updated_by=user,
                        enterprise=user.enterprise,
                        bom_number=code,
                        product_name=name,
                        nice_number=nice_number,
                        price=standard_price,
                        item_group=item_group_query,
                        brand=brand_query
                    )
                    bom_created.save()

                    if item_query:
                        if item_group_query:
                            item_query.item_group = item_group_query
                        if brand_query:
                            item_query.brand = brand_query
                        item_query.standard_price = standard_price
                        item_query.bom_division = bom_created
                        item_query.save()
                    else:
                        item_created = ItemMaster.objects.create(
                            created_by=user,
                            updated_by=user,
                            enterprise=user.enterprise,
                            code=code,
                            # bom_number=code,
                            # product_name=name,
                            name=name,
                            nice_number=nice_number,
                            standard_price=standard_price,
                            item_group=item_group_query,
                            brand=brand_query,

                            bom_division_id=bom_created.id
                        )
                        item_created.save()

        for row in ws:
            if row[0].value == '브랜드':
                pass
            elif row[0].value == 'it_id':
                break
            else:
                customer = CustomerMaster.objects.filter()

                brand = row[0].value
                try:
                    brand_query = codemaster.get(enterprise=user.enterprise, name=brand)
                except CodeMaster.DoesNotExist:
                    brand_query = None

                item_group = row[1].value
                try:
                    item_group_query = codemaster.get(enterprise=user.enterprise, name=item_group)
                except CodeMaster.DoesNotExist:
                    item_group_query = None

                code = row[2].value
                name = row[3].value
                nice_number = row[4].value
                detail = row[5].value
                shape = row[6].value
                # 자재분류 7
                amount = row[8].value if row[8].value is not None else 0
                standard_price = row[9].value if row[9].value is not None else 0
                unit = row[10].value

                try:
                    unit_query = codemaster.get(enterprise=user.enterprise, name=unit)
                except CodeMaster.DoesNotExist:
                    unit_query = None

                try:
                    customer1 = customer.get(enterprise=user.enterprise, code=row[11].value)
                except CustomerMaster.DoesNotExist:
                    customer1 = None
                try:
                    customer2 = customer.get(enterprise=user.enterprise, code=row[13].value)
                except CustomerMaster.DoesNotExist:
                    customer2 = None
                try:
                    customer3 = customer.get(enterprise=user.enterprise, code=row[15].value)
                except CustomerMaster.DoesNotExist:
                    customer3 = None

                etc = row[17].value

                try:
                    item = itemmaster.get(enterprise=user.enterprise, code=code)
                except ItemMaster.DoesNotExist:
                    ItemMaster.objects.create(
                        brand=brand_query,
                        item_group=item_group_query,
                        code=code,
                        name=name,
                        nice_number=nice_number,
                        detail=detail,
                        shape=shape,
                        safe_amount=amount,
                        standard_price=standard_price,
                        unit=unit_query,
                        purchase_from=customer1,
                        purchase_from2=customer2,
                        purchase_from3=customer3,
                        etc=etc,
                        enterprise=user.enterprise,
                        created_by=user,
                        updated_by=user
                    )
                else:
                    item.brand = brand_query
                    item.item_group = item_group_query
                    item.code = code
                    item.name = name
                    item.nice_number = nice_number
                    item.detail = detail
                    item.shape = shape
                    item.safe_amount = amount
                    item.unit = unit_query
                    item.standard_price = standard_price
                    item.purchase_from = customer1
                    item.purchase_from2 = customer2
                    item.purchase_from3 = customer3
                    item.etc = etc
                    item.enterprise = user.enterprise
                    # item.created_by = user
                    item.updated_by = user

                    item.save()

        context = {}
        return JsonResponse(context)
