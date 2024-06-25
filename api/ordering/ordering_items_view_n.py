from datetime import datetime, date

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from api.models import UserMaster, Request, CustomerMaster, Ordering, OrderingItems, ItemOut, OrderingExItems
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class Ordering_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'ordering/ordering_input.html', context)


class OrderingItems_create(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        # 주문서 아이디,
        fk = request.POST.get('fk', '')

        # 아이템(항목) 개수
        cnt = int(request.POST.get('itemCnt', ''))

        context = {}

        if cnt is not None:
            item_id = []
            item_detail = []
            item_unit = []

            item_quantity = []
            item_price = []
            supply_price = []
            surtax = []
            item_supply_total = []

            item_remarks = []
            item_file = []

            # 초기화
            for i in range(0, cnt):
                item_id.append(None)
                item_detail.append(None)
                item_unit.append(None)

                item_quantity.append(None)
                item_price.append(None)
                supply_price.append(None)
                surtax.append(None)
                item_supply_total.append(None)

                item_remarks.append(None)
                item_file.append(None)

            for i in range(0, cnt):
                item_id[i] = request.POST.get('item_id[' + str(i) + ']')  # 품번 ID
                item_detail[i] = request.POST.get('item_detail[' + str(i) + ']')  # 품명상세
                item_unit[i] = request.POST.get('item_unit[' + str(i) + ']')  # 품명단위

                item_quantity[i] = request.POST.get('item_quantity[' + str(i) + ']')  # 수량
                item_price[i] = request.POST.get('item_price[' + str(i) + ']')  # 단가
                supply_price[i] = request.POST.get('supply_price[' + str(i) + ']')  # 공급가
                surtax[i] = request.POST.get('surtax[' + str(i) + ']')  # 부가세
                item_supply_total[i] = request.POST.get('item_supply_total[' + str(i) + ']')  # 합계

                item_remarks[i] = request.POST.get('item_remarks[' + str(i) + ']')  # 비고
                item_file[i] = request.FILES.get('file[' + str(i) + ']')

                try:
                    # 주문항목 등록
                    obj = OrderingItems.objects.create(

                        ordering_id=fk,

                        item_id=item_id[i],
                        item_detail=item_detail[i],
                        item_unit=item_unit[i],

                        quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                        item_price=(0 if (item_price[i] == '') else item_price[i]),
                        supply_price=(0 if (supply_price[i] == '') else supply_price[i]),
                        surtax=(0 if (surtax[i] == '') else surtax[i]),
                        item_supply_total=(0 if (item_supply_total[i] == '') else item_supply_total[i]),


                        remarks=item_remarks[i],
                        file=item_file[i],

                        created_by=user,
                        updated_by=user,
                        # 이거 이상한데? 오토나우 애드여서 문제 없던 건가?
                        # created_at=user,
                        updated_at=user,
                        enterprise=user.enterprise
                    )

                    # 미출하 등록
                    num = generate_code('O', ItemOut, 'num', user)
                    obj2 = OrderingExItems.objects.create(

                        ordering_id=fk,

                        out=False,  # 미출하

                        ordering_item_id=obj.id,
                        num=num,
                        item_id=item_id[i],
                        item_detail=item_detail[i],
                        item_unit=item_unit[i],
                        item_price=(0 if (item_price[i] == '') else item_price[i]),

                        quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),  # 주문수량
                        supply_price=(0 if (supply_price[i] == '') else supply_price[i]),  # 공급가
                        surtax=(0 if (surtax[i] == '') else surtax[i]),  # 부가세
                        item_supply_total=(0 if (item_supply_total[i] == '') else item_supply_total[i]),  # 합계

                        export_quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),  # 출하수량 ? 미출하수량
                        export_date=None,  # 출하일자
                        export_address=None,  # 출하주소

                        created_by=user,
                        updated_by=user,
                        # 이거 이상한데? 오토나우 애드여서 문제 없던 건가?
                        # created_at=user,
                        updated_at=user,
                        enterprise=user.enterprise
                    )

                    # if obj:
                    #     context = get_res(context, obj)
                    # else:
                    #     msg = msg_create_fail
                    #     return JsonResponse({'error': True, 'message': msg})

                except Exception as e:
                    print('주문서 아이템 등록중 에러 발생')
                    print(e)
                    msg = msg_error
                    # for j in e.args:
                    #     if j == 1062:
                    #         # msg = msg_1062
                    #         msg = '중복된 아이템항목이 존재합니다.'

                    return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class OrderingItems_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '100')

        # 검색인자 - 주문서 id 로 외래키 참조
        fk = request.GET.get('fk')

        qs = OrderingItems.objects.filter(enterprise__name=request.COOKIES['enterprise_name'], ordering__id=fk) \
            .order_by('-id')

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


# 일단 안씀.
class OrderingItems_update(View):

    @transaction.atomic
    def post(self, request):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        pk = request.POST.get('pk')

        code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        explain = request.POST.get('explain', '')
        enable = request.POST.get('enable', '')

        if enable == 'true':
            enable = 1
        elif enable == 'false':
            enable = 0

        etc = request.POST.get('etc', '')

        group = request.POST.get('group', '')
        if group == '':
            group = None
        else:
            group = int(group)

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = Ordering.objects.get(pk=int(pk))

            obj.code = code
            obj.name = name
            obj.explain = explain
            obj.enable = enable
            obj.etc = etc
            obj.group_id = group

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

            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 상세코드가 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


# 일단 안씀.
class OrderingItems_delete(View):

    @transaction.atomic
    def post(self, request):

        pk = request.POST.get('pk', '')

        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = Ordering.objects.get(pk=int(pk))
            inv.delete()
        except Exception as e:
            print('삭제 실패')
            print(e)
            # msg = msg_delete_fail
            msg = ["사용중인 데이터 입니다. 관련 데이터 삭제 후 다시 시도해주세요."]
            return JsonResponse({'error': True, 'message': msg})

        context = {}
        context['id'] = pk
        return JsonResponse(context)


def get_res(context, obj):
    context['id'] = obj.id
    context['licensee_number'] = obj.licensee_number
    context['owner_name'] = obj.owner_name
    context['business_conditions'] = obj.business_conditions
    context['business_event'] = obj.business_event
    context['postal_code'] = obj.postal_code
    context['address'] = obj.address
    context['office_phone'] = obj.office_phone
    context['office_fax'] = obj.office_fax
    context['charge_name'] = obj.charge_name
    context['charge_phone'] = obj.charge_phone
    context['charge_level'] = obj.charge_level
    context['email'] = obj.email
    context['etc'] = obj.etc

    context['provide_sum'] = obj.provide_sum
    context['due_date'] = obj.due_date
    context['pay_option'] = obj.pay_option
    context['guarantee_date'] = obj.guarantee_date
    context['deliver_place'] = obj.deliver_place
    context['note'] = obj.note

    if (obj.code):
        context['code_id'] = obj.code.id
        context['code_name'] = obj.code.name
    else:
        context['code_id'] = ''
        context['code_name'] = ''

    context['created_at'] = obj.created_at
    context['updated_at'] = obj.updated_at
    context['created_by_id'] = obj.created_by.id
    context['enterprise_id'] = obj.enterprise.id
    context['updated_by_id'] = obj.updated_by.id

    return context


def get_results(qs):
    results = []
    appendResult = results.append

    # /item_detail, /item_unit, /file, /remarks, export_quantity, export_now_quantity, export_address, export_date,
    # quantity, item_price, supply_price, surtax, item_supply_total, stock

    # cost_price, cost_total,

    # 품번, 품명, 품명상세, 단위, 수량, 단가, 공급가, 부가세, 합계, 첨부파일, 비고...

    for row in qs.object_list:
        if (row.item_detail):
            item_detail = row.item_detail
        else:
            item_detail = ''

        if (row.item_unit):
            item_unit = row.item_unit
        else:
            item_unit = ''

        if (row.file):
            file = row.file.url
        else:
            file = ''

        if (row.remarks):
            remarks = row.remarks
        else:
            remarks = ''

        if (row.ordering):
            ordering_id = row.ordering.id
            ordering_code = row.ordering.ordering_code
        else:
            ordering_id = ''
            ordering_code = ''
        if row.item.brand :
            item_brand_name = row.item.brand.name
        else:
            item_brand_name = ''

        if row.item.item_group:
            item_group_name = row.item.item_group.name
        else:
            item_group_name = ''

        if row.item.nice_number :
            item_nice = row.item.nice_number
        else:
            item_nice = ''
        if row.item.shape :
            item_shape = row.item.shape
        else:
            item_shape = ''

        # (수량), (단가), (공급가), (부가세), (합계)
        appendResult({
            'id': row.id,

            'ordering_id': ordering_id,
            'ordering_code': ordering_code,

            'item_id': row.item.id,
            'item_code': row.item.code,
            'item_name': row.item.name,

            'item_detail': item_detail,
            'item_unit': item_unit,
            'item_brand_name': item_brand_name,
            'item_group_name': item_group_name,
            'item_nice' : item_nice,
            'item_shape' : item_shape,
            'file': file,
            'remarks': remarks,

            'quantity': row.quantity,

            'item_price': row.item_price,
            'supply_price': row.supply_price,
            'surtax': row.surtax,
            'item_supply_total': row.item_supply_total,
            'created_by': row.created_by.username,
            'created_at': row.created_at,
            'updated_by': row.updated_by.username,
            'updated_at': row.updated_at,
        })

    return results


# 주문번호 만드는 함수
def generate_code(prefix1, model, model_field_prefix, user):
    today = date.today()
    prefix2 = str(today.year * 10000 + today.month * 100 + today.day)
    kwargs = {
        model_field_prefix + '__istartswith': prefix1 + prefix2,
        'enterprise': user.enterprise
    }
    res = model.objects.filter(**kwargs).order_by(model_field_prefix)
    if res.exists() is False:
        return prefix1 + str(int(prefix2) * 1000)

    last_order = res.values(model_field_prefix).last()[model_field_prefix]
    return prefix1 + str(int(prefix2) * 1000 + int(last_order[-3:]) + 1)
