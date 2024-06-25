from datetime import datetime

from django.db import transaction, connection
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from api.models import UserMaster, CodeMaster, ItemMaster, EnterpriseMaster
from api.serializers import UserMasterSerializer
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class EnterpriseMaster_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        # context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
        return render(request, 'basic_information/new_enterprise_register.html', context)


class EnterpriseMaster_create(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        manage = request.POST.get('manage', '')
        com_type = request.POST.get('com_type', '')
        user_id = request.POST.get('user_id', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        context = {}

        try:
            obj = EnterpriseMaster.objects.create(
                code=code,
                name=name,
                manage=manage,
                com_type=com_type
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
                    msg = '중복된 기업코드가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        # 마스터 사용자 등록
        try:
            user_code = get_userCode(True, code)

            userobj = UserMaster.objects.create(
                password=password,
                is_superuser=False,
                user_id=user_id,
                username=name + "관리자",
                is_master=True,
                enterprise_id=obj.id,
                code=user_code,
                created_by_id=request.COOKIES['user_id']
            )

            userobj.set_password(password)
            userobj.save()
        except Exception as e1:
            print(e1)

        # 메뉴 및 컬럼 정보 등록
        try:
            with connection.cursor() as cursor:
                cursor.callproc('autoAuth', [com_type, obj.id, userobj.id])  #기업유형, 회사아이디, 마스터사용자 아이디
            print('autoAuth process')
            
        except Exception as e2:
            print(e2)

        return JsonResponse(context)


class EnterpriseMaster_read(View):
    def get(self, request, *args, **kwargs):
        qs = EnterpriseMaster.objects.filter(
            Q(user_master_enterprise__is_superuser=True) | Q(user_master_enterprise__is_master=True)
        ).select_related(
            'user_master_enterprise'
        ).values('id', 'code', 'name', 'manage', 'com_type', 'user_master_enterprise__user_id',
                 'user_master_enterprise__username',
                 'user_master_enterprise__password')

        list_qs = list(qs)

        result = get_results(list_qs)
        context = {}
        context['results'] = result

        return JsonResponse(context, safe=False)


class EnterpriseMaster_update(View):

    @transaction.atomic
    def post(self, request):

        pk = request.POST.get('pk', '')
        if not pk:
            return JsonResponse({'error': True, 'message': msg_pk})

        code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        manage = request.POST.get('manage', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        context = {}

        try:
            obj = EnterpriseMaster.objects.get(pk=int(pk))
            if manage:
                obj.manage = manage
                obj.save()

            if obj:
                context = get_res(context, obj)
            else:
                msg = msg_update_fail
                return JsonResponse({'error': True, 'message': msg})

            if username or password:
                userResult = UserMaster.objects.get(enterprise_id=int(pk), is_master=True)
                if username:
                    userResult.username = username
                if password:
                    userResult.set_password(password)

                userResult.save()
        except EnterpriseMaster.DoesNotExist:
            msg = msg_update_fail
            return JsonResponse({'error': True, 'message': msg})
        except Exception as e:
            print(e)
            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 기업코드가 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class EnterpriseMaster_delete(View):

    @transaction.atomic
    def post(self, request):

        pk = request.POST.get('pk', '')

        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            unv = UserMaster.objects.get(enterprise_id=int(pk), is_master=True)
            if unv:
                unv.delete()
            inv = EnterpriseMaster.objects.get(pk=int(pk))
            if inv:
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
    context['code'] = obj.code
    context['name'] = obj.name
    context['manage'] = obj.manage

    # context['permissions'] = obj.permissions

    return context


def get_results(qs):
    results = []
    appendResult = results.append

    # id, 코드, 기업명, 관리명

    for row in qs:
        appendResult({
            'id': row['id'],
            'code': row['code'],
            'name': row['name'],
            'manage': row['manage'],
            'user_id': row['user_master_enterprise__user_id'],
            'username': row['user_master_enterprise__username'],
            'password': row['user_master_enterprise__password'],
            'com_type': row['com_type']
        })

    return results


def get_userCode(master, code):
    if master is True:

        return code[1:] + "0000"
    else:
        date = str(datetime.date.today()).replace('-', '')[2:6]
        order = '00'
        prefix = 'UN' + date
        res = UserMaster.objects.filter(code__istartswith=prefix)
        if res.exists():
            num = res.order_by('-code').first().code[-2:]
            order = str(int(num) + 1)
            if len(order) == 1:
                order = '0' + order
        return 'UN' + date + order
