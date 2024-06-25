from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from api.base.base_form import order_company_fm
from api.models import UserMaster, CodeMaster, ItemMaster, EnterpriseMaster, OrderCompany
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class OrderCompany_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['oc'] = order_company_fm(request.GET, request.COOKIES['enterprise_name'])
        return render(request, 'basic_information/order_company.html', context)


class OrderCompany_create(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        name = request.POST.get('name', '')
        explain = request.POST.get('explain')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = OrderCompany.objects.create(
                name=name,
                explain=explain,

                created_by=user,
                updated_by=user,
                created_at=d_today,
                updated_at=d_today,
                enterprise=user.enterprise,
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
                    msg = '중복된 납품기업이 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class OrderCompany_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')

        # 검색인자 - 기업명
        oc_name_sch = request.GET.get('oc_name_sch', '')

        qs = OrderCompany.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('-id')

        # Search
        if oc_name_sch != '':
            qs = qs.filter(id=oc_name_sch)

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


class OrderCompany_update(View):

    @transaction.atomic
    def post(self, request):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        pk = request.POST.get('pk', '')
        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        name = request.POST.get('name', '')
        explain = request.POST.get('explain', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = OrderCompany.objects.get(pk=int(pk))

            obj.name = name
            obj.explain = explain

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
                    msg = '중복된 납품기업이 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class OrderCompany_delete(View):

    @transaction.atomic
    def post(self, request):

        pk = request.POST.get('pk', '')

        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = OrderCompany.objects.get(pk=int(pk))
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
    context['name'] = obj.name
    context['explain'] = obj.explain

    context['created_at'] = obj.created_at
    context['updated_at'] = obj.updated_at
    context['created_by_id'] = obj.created_by.id
    context['enterprise_id'] = obj.enterprise.id
    context['updated_by_id'] = obj.updated_by.id

    return context


def get_results(qs):
    results = []
    appendResult = results.append

    # id, 기업명, 설명, 등록자, 동록일, 수정일

    for row in qs.object_list:
        if (row.explain):
            explain = row.explain
        else:
            explain = ''

        appendResult({
            'id': row.id,
            'name': row.name,
            'explain': explain,

            'created_by': row.created_by.username,

            'created_at': row.created_at,
            'updated_at': row.updated_at,

        })

    return results
