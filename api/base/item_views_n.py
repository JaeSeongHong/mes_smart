import traceback
from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
# rest...
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

from api.base.base_form import facilities_fm, item_fm
from api.models import CustomerMaster, UserMaster, CodeMaster, FacilitiesMaster, ItemMaster
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class ItemMaster_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
        return render(request, 'basic_information/item.html', context)


class ItemMaster_create(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        detail = request.POST.get('detail', '')

        item_division = request.POST.get('item_division', '')
        if item_division == '':
            item_division = None
        else:
            item_division = int(item_division)

        unit = request.POST.get('unit', '')
        if unit == '':
            unit = None
        else:
            unit = int(unit)

        model = request.POST.get('model', '')
        if model == '':
            model = None
        else:
            model = int(model)

        container = request.POST.get('container', '')
        if container == '':
            container = None
        else:
            container = int(container)

        color = request.POST.get('color', '')
        if color == '':
            color = None
        else:
            color = int(color)

        type = request.POST.get('type', '')
        if type == '':
            type = None
        else:
            type = int(type)

        purchase_from = request.POST.get('purchase_from', '')
        if purchase_from == '':
            purchase_from = None
        else:
            purchase_from = int(purchase_from)

        purchase_from2 = request.POST.get('purchase_from2', '')
        if purchase_from2 == '':
            purchase_from2 = None
        else:
            purchase_from2 = int(purchase_from2)

        purchase_from3 = request.POST.get('purchase_from3', '')
        if purchase_from3 == '':
            purchase_from3 = None
        else:
            purchase_from3 = int(purchase_from3)

        moq = request.POST.get('moq', '')
        if moq == '':
            moq = 0
        else:
            moq = int(moq)

        etc = request.POST.get('etc', '')

        standard_price = request.POST.get('standard_price', '')
        if standard_price == '':
            standard_price = 0
        else:
            standard_price = int(standard_price)

        brand = request.POST.get('brand_id', '')
        if brand == '':
            brand = None
        else:
            brand = int(brand)

        item_group = request.POST.get('item_group_id', '')
        if item_group == '':
            item_group = None
        else:
            item_group = int(item_group)

        nice_number = request.POST.get('nice_number', '')

        shape = request.POST.get('shape', '')

        safe_amount = request.POST.get('safe_amount', '')
        if safe_amount == '':
            safe_amount = 0
        else:
            safe_amount = int(safe_amount)

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        # qr 생성 ret.data['qr_path']
        if request.POST['qr_path'] is '':
            _mutable = request.POST._mutable
            request.POST._mutable = True

            from api.QRCode.QRCodeManager import QRCodeGen_Code
            filename = QRCodeGen_Code(request.POST.get('code', ''), 'ItemMaster')

            request.POST['qr_path'] = filename
            request.POST._mutable = _mutable

        try:
            obj = ItemMaster.objects.create(

                code=code,
                name=name,
                detail=detail,

                item_division_id=item_division,
                unit_id=unit,
                model_id=model,
                container_id=container,
                color_id=color,
                type_id=type,
                purchase_from_id=purchase_from,
                purchase_from2_id=purchase_from2,
                purchase_from3_id=purchase_from3,

                moq=moq,
                etc=etc,
                standard_price=standard_price,

                brand_id=brand,
                item_group_id=item_group,
                nice_number=nice_number,
                shape=shape,
                safe_amount=safe_amount,

                created_by=user,
                updated_by=user,
                created_at=d_today,
                updated_at=d_today,
                enterprise=user.enterprise,
                qr_path=filename,

            )

            if obj:
                context = get_res(context, obj)
            else:
                msg = msg_create_fail
                return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            print(e)

            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 품번이 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class ItemMaster_read(View):
    ordering_fields = ["name", "code", "detail"]

    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')
        print(request.GET)
        # 검색인자 - 품번, 품명, 자재분류
        it_code_sch = request.GET.get('it_code_sch', '')
        it_name_sch = request.GET.get('it_name_sch', '')
        it_div_sch = request.GET.get('it_div_sch', '')
        it_nice_number_sch = request.GET.get('it_nice_number_sch', '')
        it_brand_sch = request.GET.get('it_brand_sch', '')
        it_item_group_sch = request.GET.get('it_item_group_sch', '')
        total_search = request.GET.get('total_search', '')
        ordering = request.GET.get('ordering', '')

        # 의리서 작성에서 아이템 검색하기 위해서 필요함.
        it_id_sch = request.GET.get('it_id_sch', '')

        if ordering != '':
            qs = ItemMaster.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by(ordering)
        else:
            qs = ItemMaster.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('-id')

        if total_search != '':
            print(total_search)
            total_search_list = total_search.split()
            total_qs = ItemMaster.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('-id')

            for item in total_search_list:
                total_qs = total_qs.filter(
                    Q(brand__name__contains=item) |
                    Q(item_group__name__contains=item) |
                    Q(name__contains=item) |
                    Q(code__contains=item) |
                    Q(nice_number__contains=item) |
                    Q(detail__contains=item)
                )

            print(total_search_list)
            qs_total = Pagenation(total_qs, _size, _page)
            results = get_results(qs_total)

            pre = int(_page) - 1
            url_pre = "/?page_size=" + _size + "&page=" + str(pre)
            if pre < 1:
                url_pre = None

            next = int(_page) + 1
            url_next = "/?page_size=" + _size + "&page=" + str(next)
            if next > qs_total.paginator.num_pages:
                url_next = None

            context = {}
            context['count'] = qs_total.paginator.count
            context['previous'] = url_pre
            context['next'] = url_next
            context['results'] = results

            return JsonResponse(context, safe=False)

        # Search
        if it_item_group_sch != '':
            sc = CodeMaster.objects.get(id=it_item_group_sch)
            if sc:
                qs = qs.filter(item_group_id=sc.id)

        if it_brand_sch != '':
            sc = CodeMaster.objects.get(id=it_brand_sch)
            if sc:
                qs = qs.filter(brand_id=sc.id)

        if it_div_sch != '':
            sc = CodeMaster.objects.get(id=it_div_sch)
            if sc:
                qs = qs.filter(item_division_id=sc.id)

        if it_code_sch != '':
            # qs = qs.filter(code__contains=it_code_sch)
            qs = qs.filter(id=it_code_sch)
        elif it_nice_number_sch != '':
            # qs = qs.filter(name__contains=it_name_sch)
            qs = qs.filter(id=it_nice_number_sch)

        if it_id_sch != '':
            qs = qs.filter(id=it_id_sch)

        if (it_name_sch):
            qs = qs.filter(id=it_name_sch)

        # Pagination
        qs_ps = Pagenation(qs, _size, _page)

        pre = int(_page) - 1
        url_pre = "/?page_size=" + _size + "&page=" + str(pre)
        if pre < 1:
            url_pre = None

        next = int(_page) + 1
        url_next = "/?page_size=" + _size + "&page=" + str(next)
        if next > qs_ps.paginator.num_pages:
            url_next = None

        results = get_results(qs_ps)

        context = {}
        context['count'] = qs_ps.paginator.count
        context['previous'] = url_pre
        context['next'] = url_next
        context['results'] = results

        return JsonResponse(context, safe=False)


class ItemMaster_update(View):
    @transaction.atomic
    def post(self, request):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        pk = request.POST.get('pk', '')
        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        detail = request.POST.get('detail', '')

        item_division = request.POST.get('item_division', '')
        if item_division == '':
            item_division = None
        else:
            item_division = int(item_division)

        unit = request.POST.get('unit', '')
        if unit == '':
            unit = None
        else:
            unit = int(unit)

        model = request.POST.get('model', '')
        if model == '':
            model = None
        else:
            model = int(model)

        container = request.POST.get('container', '')
        if container == '':
            container = None
        else:
            container = int(container)

        color = request.POST.get('color', '')
        if color == '':
            color = None
        else:
            color = int(color)

        type = request.POST.get('type', '')
        if type == '':
            type = None
        else:
            type = int(type)

        purchase_from = request.POST.get('purchase_from', '')
        if purchase_from == '':
            purchase_from = None
        else:
            purchase_from = int(purchase_from)

        purchase_from2 = request.POST.get('purchase_from2', '')
        if purchase_from2 == '':
            purchase_from2 = None
        else:
            purchase_from2 = int(purchase_from2)

        purchase_from3 = request.POST.get('purchase_from3', '')
        if purchase_from3 == '':
            purchase_from3 = None
        else:
            purchase_from3 = int(purchase_from3)

        etc = request.POST.get('etc', '')

        moq = request.POST.get('moq', '')
        if moq == '':
            moq = 0
        else:
            moq = int(moq)

        standard_price = request.POST.get('standard_price', '')
        if standard_price == '':
            standard_price = 0
        else:
            standard_price = int(standard_price)

        brand = request.POST.get('brand_id', '')
        if brand == '':
            brand = None
        else:
            brand = int(brand)

        item_group = request.POST.get('item_group_id', '')
        if item_group == '':
            item_group = None
        else:
            item_group = int(item_group)

        nice_number = request.POST.get('nice_number', '')

        shape = request.POST.get('shape', '')

        safe_amount = request.POST.get('safe_amount', '')
        if safe_amount == '':
            safe_amount = 0
        else:
            safe_amount = int(safe_amount)

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = ItemMaster.objects.get(pk=int(pk))

            obj.code = code
            obj.name = name
            obj.detail = detail

            obj.item_division_id = item_division
            obj.unit_id = unit
            obj.model_id = model
            obj.container_id = container
            obj.color_id = color
            obj.type_id = type

            obj.purchase_from_id = purchase_from
            obj.purchase_from2_id = purchase_from2
            obj.purchase_from3_id = purchase_from3

            obj.moq = moq
            obj.etc = etc
            obj.standard_price = standard_price

            obj.brand_id = brand
            obj.item_group_id = item_group
            obj.nice_number = nice_number
            obj.shape = shape
            obj.safe_amount = safe_amount

            # 특이점... updated_by_id 랑 enterprise_id 에서는 id를 빼고 쓰고,
            obj.updated_at = d_today
            obj.updated_by = user
            obj.enterprise = user.enterprise

            obj.save()

            if obj:
                context = get_res(context, obj)
            else:
                msg = msg_update_fail
                return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            print(e)
            print(traceback.format_exc())

            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    # 수정할 때는 발생하지 않는 에러일텐데? 일단 냅둠.
                    msg = '중복된 품번이 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class ItemMaster_delete(View):

    @transaction.atomic
    def post(self, request):
        pk = request.POST.get('pk', '')
        _qr_filename = request.POST.get('qr_path', '')
        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = ItemMaster.objects.get(pk=int(pk))
            inv.delete()
        except Exception as e:
            print('삭제 실패')
            # 예외 구분이 필요하네... 일단 출고, 의뢰서에서 외래키로 사용중인 경우 발견
            print(e)
            # msg = msg_delete_fail
            msg = ["사용중인 데이터 입니다. 관련 데이터 삭제 후 다시 시도해주세요."]
            return JsonResponse({'error': True, 'message': msg})

        from api.QRCode.QRCodeManager import DeleteQRCode
        try:
            DeleteQRCode(_qr_filename)
            print("아이템에 QR코드 이미지 경로 파일 삭제")
        except:
            # kpi_log(self.request.user.enterprise, self.request.user.user_id, "ItemMasterViewSet", "destroy", True)
            msg = ["QR Code 이미지 삭제 에러가 발생했습니다."]
            return JsonResponse({'error': True, 'message': msg})

        context = {}
        context['id'] = pk
        return JsonResponse(context)


class ItemMaster_qr_update(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        item_id = request.POST.get('pk')
        item_master = ItemMaster.objects.filter(id=item_id)

        for items in item_master:
            if items.qr_path:
                msg = 'QR코드가 이미 존재하는 품목입니다.'
                return JsonResponse({'error': True, 'message': msg})

            else:
                bom_code = items.code

                from api.QRCode.QRCodeManager import QRCodeGen_Code
                filename = QRCodeGen_Code(bom_code, 'ItemMaster')

                # instance['qr_path'] = filename
                items.qr_path = filename
                items.save()

        context = {}
        obj = ItemMaster.objects.get(pk=item_id)
        context = get_res2(context, obj)

        return JsonResponse(context)


def get_res2(context, obj):
    context['id'] = obj.id
    context['qr_path'] = obj.qr_path

    # 여기에 있어야.. 화면상에 값 넘김...
    if (obj.bom_division):
        context['bom_division_id'] = obj.item_division
        context['bom_division_name'] = 'BOM'
    else:
        context['bom_division_id'] = ''
        context['bom_division_name'] = '일반'

    return context


def get_res(context, obj):
    print(obj)
    # context['id'] = obj.id
    context['code'] = obj.code
    context['name'] = obj.name
    context['detail'] = obj.detail
    context['qr_path'] = obj.qr_path

    # 여기에 있어야.. 화면상에 값 넘김...
    if obj.bom_division:
        context['bom_division_id'] = obj.bom_division.id
        context['bom_division_name'] = 'BOM'
    else:
        context['bom_division_id'] = ''
        context['bom_division_name'] = '일반'

    if obj.item_division:
        context['item_division_id'] = obj.item_division.id
        context['item_division_name'] = obj.item_division.name
    else:
        context['item_division_id'] = ''
        context['item_division_name'] = ''

    if obj.unit:
        context['unit_id'] = obj.unit.id
        context['unit_name'] = obj.unit.name
    else:
        context['unit_id'] = ''
        context['unit_name'] = ''

    if obj.model:
        context['model_id'] = obj.model.id
        context['model_name'] = obj.model.name
    else:
        context['model_id'] = ''
        context['model_name'] = ''

    if obj.container:
        context['container_id'] = obj.container.id
        context['container_name'] = obj.container.name
    else:
        context['container_id'] = ''
        context['container_name'] = ''

    if obj.color:
        context['color_id'] = obj.color.id
        context['color_name'] = obj.color.name
    else:
        context['color_id'] = ''
        context['color_name'] = ''

    if obj.type:
        context['type_id'] = obj.type.id
        context['type_name'] = obj.type.name
    else:
        context['type_id'] = ''
        context['type_name'] = ''

    if obj.purchase_from:
        context['purchase_from_id'] = obj.purchase_from.id
        context['purchase_from_name'] = obj.purchase_from.name
        context['purchase_from_code'] = obj.purchase_from.code
    else:
        context['purchase_from_id'] = ''
        context['purchase_from_name'] = ''
        context['purchase_from_code'] = ''

    if obj.purchase_from2:
        context['purchase_from2_id'] = obj.purchase_from2.id
        context['purchase_from2_name'] = obj.purchase_from2.name
        context['purchase_from2_code'] = obj.purchase_from2.code
    else:
        context['purchase_from2_id'] = ''
        context['purchase_from2_name'] = ''
        context['purchase_from2_code'] = ''

    if obj.purchase_from3:
        context['purchase_from3_id'] = obj.purchase_from3.id
        context['purchase_from3_name'] = obj.purchase_from3.name
        context['purchase_from3_code'] = obj.purchase_from3.code
    else:
        context['purchase_from3_id'] = ''
        context['purchase_from3_name'] = ''
        context['purchase_from3_code'] = ''

    if obj.brand:
        context['brand_id'] = obj.brand.id
        context['brand_name'] = obj.brand.name
    else:
        context['brand_id'] = ''
        context['brand_name'] = ''

    if obj.item_group:
        context['item_group_id'] = obj.item_group.id
        context['item_group_name'] = obj.item_group.name
    else:
        context['item_group_id'] = ''
        context['item_group_name'] = ''

    if obj.nice_number:
        context['nice_number'] = obj.nice_number
    else:
        context['nice_number'] = ''

    if obj.shape:
        context['shape'] = obj.shape
    else:
        context['shape'] = ''

    context['moq'] = obj.moq
    context['etc'] = obj.etc
    context['standard_price'] = obj.standard_price

    context['created_at'] = obj.created_at
    context['updated_at'] = obj.updated_at
    context['created_by_id'] = obj.created_by.id
    context['enterprise_id'] = obj.enterprise.id
    context['updated_by_id'] = obj.updated_by.id

    return context


def get_results(qs):
    results = []
    appendResult = results.append

    # 자재분류, 모델, 단위, 거래처, 용기타입, 칼라구분, 품종구분

    for row in qs.object_list:
        if row.item_division_id:
            division_id = row.item_division.id
            division_name = row.item_division.name
        else:
            division_id = ''
            division_name = ''

        if row.model_id:
            model_id = row.model.id
            model_name = row.model.name
        else:
            model_id = ''
            model_name = ''

        if row.unit_id:
            unit_id = row.unit.id
            unit_name = row.unit.name
        else:
            unit_id = ''
            unit_name = ''

        if row.purchase_from_id:
            customer_id = row.purchase_from.id
            customer_name = row.purchase_from.name
            customer_code = row.purchase_from.code
        else:
            customer_id = ''
            customer_name = ''
            customer_code = ''


        if row.container_id:
            container_id = row.container.id
            container_name = row.container.name
        else:
            container_id = ''
            container_name = ''

        # 에러 났던... color, container 혼동
        if row.color_id:
            color_id = row.color.id
            color_name = row.color.name
        else:
            color_id = ''
            color_name = ''

        if row.type_id:
            type_id = row.type.id
            type_name = row.type.name
        else:
            type_id = ''
            type_name = ''

        #
        if row.bom_division_id:
            bom_division = row.bom_division.id
        else:
            bom_division = ''

        # 상세, 표준가, 비고, moq, qr
        if row.detail:
            detail = row.detail
        else:
            detail = ''

        if row.standard_price:
            standard_price = row.standard_price
        else:
            standard_price = ''

        if row.etc:
            etc = row.etc
        else:
            etc = ''

        if row.moq:
            moq = row.moq
        else:
            moq = ''

        if row.qr_path:
            qr_path = row.qr_path
        else:
            qr_path = ''

        if row.brand_id:
            brand_id = row.brand.id
            brand_name = row.brand.name
        else:
            brand_id = ''
            brand_name = ''

        if row.item_group_id:
            item_group_id = row.item_group.id
            item_group_name = row.item_group.name
        else:
            item_group_id = ''
            item_group_name = ''

        if row.nice_number:
            nice_number = row.nice_number
        else:
            nice_number = ''

        if row.shape:
            shape = row.shape
        else:
            shape = ''

        if row.safe_amount:
            safe_amount = row.safe_amount
        else:
            safe_amount = ''

        if row.fee_rate:
            fee_rate_str = str(row.fee_rate)  # '15.400'
            fee_rate = fee_rate_str.rstrip('0').rstrip('.')  # '15.4'
        else:
            fee_rate = 0.0

        appendResult({
            'id': row.id,
            'code': row.code,
            'name': row.name,

            'detail': detail,

            # 자재분류, 모델, 단위, 거래처, 용기타입, 칼라구분, 품종구분
            'division_id': division_id,
            'division_name': division_name,

            'model_id': model_id,
            'model_name': model_name,

            'unit_id': unit_id,
            'unit_name': unit_name,

            'purchase_from_id': customer_id,
            'purchase_from_name': customer_name,
            'purchase_from_code': customer_code,

            'container_id': container_id,
            'container_name': container_name,

            'color_id': color_id,
            'color_name': color_name,

            'type_id': type_id,
            'type_name': type_name,

            # moq, 비고, 표준단가
            'moq': moq,

            'etc': etc,
            'standard_price': standard_price,

            # bom 타입, qr
            'bom_division_id': bom_division,
            'qr_path': qr_path,

            'brand_id': brand_id,
            'brand_name': brand_name,

            'item_group_id': item_group_id,
            'item_group_name': item_group_name,

            'nice_number': nice_number,
            'shape': shape,
            'safe_amount': safe_amount,
            'fee_rate': fee_rate,
        })

    return results

