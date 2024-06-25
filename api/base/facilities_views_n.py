from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from api.base.base_form import facilities_fm
from api.models import CustomerMaster, UserMaster, CodeMaster, FacilitiesMaster
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class FacilitiesMaster_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['eq'] = facilities_fm(request.GET, request.COOKIES['enterprise_name'])
        return render(request, 'basic_information/equipment.html', context)


class FacilitiesMaster_create(View):

    @transaction.atomic
    def post(self, request):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        detail = request.POST.get('detail', '')

        factory = request.POST.get('factory', '')
        if factory == '':
            factory = None
        else:
            factory = int(factory)

        made_by = request.POST.get('made_by', '')
        buy_at = request.POST.get('buy_at', '')
        enable = request.POST.get('enable', '')

        process = request.POST.get('process', '')
        if process == '':
            process = None
        else:
            process = int(process)

        workshop = request.POST.get('workshop', '')
        if workshop == '':
            workshop = None
        else:
            workshop = int(workshop)

        type = request.POST.get('type', '')
        if type == '':
            type = None
        else:
            type = int(type)

        order = request.POST.get('order', '')
        group = request.POST.get('group', '')
        op_at = request.POST.get('op_at', '')
        kill_at = request.POST.get('kill_at', '')
        etc = request.POST.get('etc', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = FacilitiesMaster.objects.create(

                code=code,
                name=name,
                detail=detail,
                factory_id=factory,
                made_by=made_by,
                buy_at=buy_at,
                enable=enable,

                process_id=process,
                workshop_id=workshop,
                type_id=type,

                order=order,
                group=group,
                op_at=op_at,
                kill_at=kill_at,
                etc=etc,

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
                    msg = '중복된 설비코드가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class FacilitiesMaster_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')

        # 검색인자 - 공장구분, 공정구분, 사용구분, 설비명
        eq_factory_sch = request.GET.get('eq_factory_sch', '')
        eq_process_sch = request.GET.get('eq_process_sch', '')
        eq_enable_sch = request.GET.get('eq_enable_sch', '')
        eq_name_sch = request.GET.get('eq_name_sch', '')

        qs = FacilitiesMaster.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('-id')

        # Search
        if eq_factory_sch != '':
            sc = CodeMaster.objects.get(id=eq_factory_sch)
            if sc:
                qs = qs.filter(factory_id=sc.id)

        if eq_process_sch != '':
            sc = CodeMaster.objects.get(id=eq_process_sch)
            if sc:
                qs = qs.filter(process_id=sc.id)

        if eq_enable_sch != '':
            qs = qs.filter(enable=eq_enable_sch)

        if eq_name_sch != '':
            qs = qs.filter(name__contains=eq_name_sch)

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


class FacilitiesMaster_update(View):

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
        made_by = request.POST.get('made_by', '')
        order = request.POST.get('order', '')
        group = request.POST.get('group', '')

        buy_at = request.POST.get('buy_at', '')
        op_at = request.POST.get('op_at', '')
        kill_at = request.POST.get('kill_at', '')
        enable = int(request.POST.get('enable', ''))

        factory = request.POST.get('factory', '')
        if factory == '':
            factory = None
        else:
            factory = int(factory)

        process = request.POST.get('process', '')
        if process == '':
            process = None
        else:
            process = int(process)

        workshop = request.POST.get('workshop', '')
        if workshop == '':
            workshop = None
        else:
            workshop = int(workshop)

        type = request.POST.get('type', '')
        if type == '':
            type = None
        else:
            type = int(type)

        etc = request.POST.get('etc', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = FacilitiesMaster.objects.get(pk=int(pk))

            obj.code = code
            obj.name = name
            obj.detail = detail
            obj.factory_id = factory
            obj.made_by = made_by
            obj.buy_at = buy_at
            obj.enable = enable

            obj.process_id = process
            obj.workshop_id = workshop
            obj.type_id = type

            obj.order = order
            obj.group = group
            obj.op_at = op_at
            obj.kill_at = kill_at
            obj.etc = etc

            # 특이점... updated_by_id 랑 enterprise_id 에서는 id를 빼고 쓰고,
            obj.updated_at = d_today
            obj.updated_by = user
            obj.enterprise = user.enterprise

            # 여기서는 또 _id 를 쓰고, 같은 외래키인데 암튼 뭔가 다름
            obj.factory_id = factory
            obj.process_id = process
            obj.type_id = type
            obj.workshop_id = workshop

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
                    # 수정할 때는 발생하지 않는 에러일텐데? 일단 냅둠.
                    msg = '중복된 설비가 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class FacilitiesMaster_delete(View):

    @transaction.atomic
    def post(self, request):
        pk = request.POST.get('pk', '')
        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = FacilitiesMaster.objects.get(pk=int(pk))
            inv.delete()
        except Exception as e:
            msg = msg_delete_fail
            return JsonResponse({'error': True, 'message': msg})

        context = {}
        context['id'] = pk
        return JsonResponse(context)


def get_res(context, obj):
    context['id'] = obj.id
    context['code'] = obj.code
    context['name'] = obj.name
    context['detail'] = obj.detail

    if (obj.factory):
        context['factory_id'] = obj.factory.id
        context['factory_name'] = obj.factory.name
    else:
        context['factory_id'] = ''
        context['factory_name'] = ''

    context['made_by'] = obj.made_by
    context['buy_at'] = obj.buy_at
    context['enable'] = obj.enable

    if (obj.process):
        context['process_id'] = obj.process.id
        context['process_name'] = obj.process.name
    else:
        context['process_id'] = ''
        context['process_name'] = ''

    if (obj.workshop):
        context['workshop_id'] = obj.workshop.id
        context['workshop_name'] = obj.workshop.name
    else:
        context['workshop_id'] = ''
        context['workshop_name'] = ''

    if (obj.type):
        context['type_id'] = obj.type.id
        context['type_name'] = obj.type.name
    else:
        context['type_id'] = ''
        context['type_name'] = ''

    context['order'] = obj.order
    context['group'] = obj.group
    context['op_at'] = obj.op_at
    context['kill_at'] = obj.kill_at
    context['etc'] = obj.etc

    context['created_at'] = obj.created_at
    context['updated_at'] = obj.updated_at
    context['created_by_id'] = obj.created_by.id
    context['enterprise_id'] = obj.enterprise.id
    context['updated_by_id'] = obj.updated_by.id

    return context


def get_results(qs):
    results = []
    appendResult = results.append

    # 설비코드, 설비명, 설비상세, 공장구분, 제작업체, 구입일자, 사용유무 필수
    # (공정구분, 작업장, 설비타입), 설비순번, 설비그룹, 가동일자, 폐기일자, 비고 비필수

    for row in qs.object_list:
        if (row.process_id):
            process_id = row.process.id
            process_name = row.process.name
        else:
            process_id = ''
            process_name = ''

        if (row.workshop_id):
            workshop_id = row.workshop.id
            workshop_name = row.workshop.name
        else:
            workshop_id = ''
            workshop_name = ''

        if (row.type_id):
            type_id = row.type.id
            type_name = row.type.name
        else:
            type_id = ''
            type_name = ''

        if (row.order):
            order = row.order
        else:
            order = ''

        if (row.group):
            group = row.group
        else:
            group = ''

        if (row.op_at):
            op_at = row.op_at
        else:
            op_at = ''

        if (row.kill_at):
            kill_at = row.kill_at
        else:
            kill_at = ''

        if (row.etc):
            etc = row.etc
        else:
            etc = ''

        appendResult({
            'id': row.id,
            'code': row.code,
            'name': row.name,
            'detail': row.detail,
            'made_by': row.made_by,

            # 공장구분, 구입일자, 사용유무
            'factory_id': row.factory.id,
            'factory_name': row.factory.name,
            'buy_at': row.buy_at,
            'enable': row.enable,

            ## (공정구분, 작업장, 설비타입), 설비순번, 설비그룹, 가동일자, 폐기일자, 비고 비필수

            'process_id': process_id,
            'process_name': process_name,

            'workshop_id': workshop_id,
            'workshop_name': workshop_name,

            'type_id': type_id,
            'type_name': type_name,

            'order': order,
            'group': group,
            'op_at': op_at,
            'kill_at': kill_at,
            'etc': etc,
        })

    return results
