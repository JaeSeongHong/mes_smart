from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from api.models import UserMaster, RequestItems
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class RequestItems_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'request/request_input.html', context)


class RequestItems_create(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        # 리퀘스트 아이디,
        fk = request.POST.get('fk', '')

        # 아이템(항목) 개수
        cnt = int(request.POST.get('itemCnt', ''))

        context = {}

        if cnt is not None:
            item_id = []
            item_detail = []
            item_unit = []

            item_quantity = []
            item_remarks = []
            item_file = []

            # 초기화
            for i in range(0, cnt):
                item_id.append(None)
                item_detail.append(None)
                item_unit.append(None)

                item_quantity.append(None)
                item_remarks.append(None)
                item_file.append(None)

            for i in range(0, cnt):
                item_id[i] = request.POST.get('item_id[' + str(i) + ']')  # 품번 ID
                item_detail[i] = request.POST.get('item_detail[' + str(i) + ']')  # 품명상세
                item_unit[i] = request.POST.get('item_unit[' + str(i) + ']')  # 품명단위
                item_quantity[i] = request.POST.get('item_quantity[' + str(i) + ']')  # 수량
                item_remarks[i] = request.POST.get('item_remarks[' + str(i) + ']')  # 비고
                item_file[i] = request.FILES.get('file[' + str(i) + ']')

                try:
                    obj = RequestItems.objects.create(

                        request_id=fk,

                        item_id=item_id[i],
                        item_detail=item_detail[i],
                        item_unit=item_unit[i],

                        quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                        remarks=item_remarks[i],
                        file=item_file[i],

                        created_by=user,
                        updated_by=user,
                        created_at=d_today,
                        updated_at=d_today,
                        enterprise=user.enterprise,
                    )

                    # if obj:
                    #     context = get_res(context, obj)
                    # else:
                    #     msg = msg_create_fail
                    #     return JsonResponse({'error': True, 'message': msg})

                except Exception as e:
                    print('이게 발생했다고?')
                    print(e)
                    msg = msg_error
                    # for j in e.args:
                    #     if j == 1062:
                    #         # msg = msg_1062
                    #         msg = '중복된 아이템항목이 존재합니다.'

                    return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class RequestItems_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '100')

        # 검색인자 - 의뢰서 id 로 외래키 참조
        fk = request.GET.get('fk')

        qs = RequestItems.objects.filter(enterprise__name=request.COOKIES['enterprise_name'], request__id=fk) \
            .order_by('id')

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
class RequestItems_update(View):

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
            obj = RequestItems.objects.get(pk=int(pk))

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

            # if obj:
            #     context = get_res(context, obj)
            # else:
            #     msg = msg_update_fail
            #     return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            print(e)

            msg = msg_error
            # for i in e.args:
            #     if i == 1062:
            #         # msg = msg_1062
            #         msg = '중복된 상세코드가 존재합니다.'
            #         break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)

# 일단 안씀.
class RequestItems_delete(View):

    @transaction.atomic
    def post(self, request):

        pk = request.POST.get('pk', '')

        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = RequestItems.objects.get(pk=int(pk))
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


# def get_res(context, obj):
#     context['id'] = obj.id
#     context['code'] = obj.code
#     context['name'] = obj.name
#     context['explain'] = obj.explain
#     context['enable'] = obj.enable
#     context['etc'] = obj.etc
#
#     if (obj.group):
#         context['group_id'] = obj.group.id
#         context['group_name'] = obj.group.name
#     else:
#         context['group_id'] = ''
#         context['group_name'] = ''
#
#     context['created_at'] = obj.created_at
#     context['updated_at'] = obj.updated_at
#     context['created_by_id'] = obj.created_by.id
#     context['enterprise_id'] = obj.enterprise.id
#     context['updated_by_id'] = obj.updated_by.id
#
#     return context


def get_results(qs):
    results = []
    appendResult = results.append

    # created_at, updated_at, created_by, updated_by, enterprise

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

        if (row.request):
            request_id = row.request.id
            request_code = row.request.request_code
        else:
            request_id = ''
            request_code = ''

        appendResult({
            'id': row.id,
            'quantity': row.quantity,
            'request_id': request_id,
            'request_code': request_code,

            'item_id': row.item.id,
            'item_code': row.item.code,
            'item_name': row.item.name,

            'item_detail': item_detail,
            'item_unit': item_unit,
            'file': file,
            'remarks': remarks,

            'created_by': row.created_by.username,
            'created_at': row.created_at,
            'updated_by': row.updated_by.username,
            'updated_at': row.updated_at,
        })

    return results



