from datetime import datetime

from django.contrib.sessions.backends import file
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from api.models import UserMaster, OrderCompany, MyInfoMaster
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class MyInfoMaster_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'basic_information/my_info.html', context)


class MyInfoMaster_create(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        company_division = request.POST['company_division']
        my_qs = MyInfoMaster.objects.filter(enterprise=user.enterprise, company_division=company_division)
        if my_qs.exists():
            msg = '사업장 명은 중복될 수 없습니다.'
            return JsonResponse({'error': True, 'message': msg})

        company_name = request.POST.get('company_name', '')
        licensee_number = request.POST.get('licensee_number', '')

        owner_name = request.POST.get('owner_name', '')
        business_conditions = request.POST.get('business_conditions', '')
        business_event = request.POST.get('business_event', '')
        post_code = request.POST.get('post_code', '')
        address = request.POST.get('address', '')
        office_phone = request.POST.get('office_phone', '')
        office_fax = request.POST.get('office_fax', '')
        email = request.POST.get('email', '')
        note = request.POST.get('note', '')

        filename = request.FILES.get('file', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = MyInfoMaster.objects.create(

                company_division=company_division,
                company_name=company_name,
                licensee_number=licensee_number,
                owner_name=owner_name,
                business_conditions=business_conditions,
                business_event=business_event,
                post_code=post_code,
                address=address,
                office_phone=office_phone,
                office_fax=office_fax,
                email=email,
                note=note,
                file=filename,

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
            print('이게 발생했다고?')
            print(e)
            # msg = msg_error
            # for i in e.args:
            #     if i == 1062:
            #         # msg = msg_1062
            #         msg = '중복된 사업장이 존재합니다.'
            #
            # return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class MyInfoMaster_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')

        # 견적서조회에서 사업장구분으로 검색하기 위해 필요함.
        myinfo_id = request.GET.get('myinfo_id', '')

        qs = MyInfoMaster.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('-id')

        if myinfo_id != '':
            qs = qs.filter(id=myinfo_id)

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


class MyInfoMaster_update(View):

    @transaction.atomic
    def post(self, request):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        pk = request.POST.get('pk')

        company_division = request.POST['company_division']
        my_qs = MyInfoMaster.objects.filter(enterprise=user.enterprise, company_division=company_division)

        obj_chek = MyInfoMaster.objects.get(pk=int(pk))

        # 사업장 원래 값이랑 입력한 값이 다를 때만 중복 체크
        if (obj_chek.company_division != company_division):
            if my_qs.exists():
                msg = '사업장 명은 중복될 수 없습니다.'
                return JsonResponse({'error': True, 'message': msg})

        company_name = request.POST.get('company_name', '')
        licensee_number = request.POST.get('licensee_number', '')

        owner_name = request.POST.get('owner_name', '')
        business_conditions = request.POST.get('business_conditions', '')
        business_event = request.POST.get('business_event', '')
        post_code = request.POST.get('post_code', '')
        address = request.POST.get('address', '')
        office_phone = request.POST.get('office_phone', '')
        office_fax = request.POST.get('office_fax', '')
        email = request.POST.get('email', '')
        note = request.POST.get('note', '')

        filename = request.FILES.get('file', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = MyInfoMaster.objects.get(pk=int(pk))

            obj.company_division = company_division
            obj.company_name = company_name
            obj.licensee_number = licensee_number
            obj.owner_name = owner_name
            obj.business_conditions = business_conditions
            obj.business_event = business_event
            obj.post_code = post_code
            obj.address = address
            obj.office_phone = office_phone
            obj.office_fax = office_fax
            obj.email = email
            obj.note = note

            if (filename != ''):
                # 바꿀 파일이 존재할때만 파일 업데이트
                obj.file = filename

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
            """ 
            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 사업장이 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})
            """

        return JsonResponse(context)


class MyInfoMaster_delete(View):

    @transaction.atomic
    def post(self, request):

        pk = request.POST.get('pk', '')

        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = MyInfoMaster.objects.get(pk=int(pk))
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
    context['company_division'] = obj.company_division
    context['company_name'] = obj.company_name
    context['licensee_number'] = obj.licensee_number

    context['owner_name'] = obj.owner_name
    context['business_conditions'] = obj.business_conditions
    context['business_event'] = obj.business_event
    context['post_code'] = obj.post_code
    context['address'] = obj.address
    context['office_phone'] = obj.office_phone
    context['office_fax'] = obj.office_fax
    context['email'] = obj.email
    context['note'] = obj.note
    context['file'] = obj.file.url

    context['created_at'] = obj.created_at
    context['updated_at'] = obj.updated_at
    context['created_by_id'] = obj.created_by.id
    context['enterprise_id'] = obj.enterprise.id
    context['updated_by_id'] = obj.updated_by.id

    return context


def get_results(qs):
    results = []
    appendResult = results.append

    # id, 사업장, 회사명, 사업자번호 필수
    # 대표자명, 업태, 종복, 우편번호, 주소, 전화번호, 팩스번호, 이메일, 비고, 날인 비필수

    for row in qs.object_list:
        if (row.owner_name):
            owner_name = row.owner_name
        else:
            owner_name = ''

        if (row.business_conditions):
            business_conditions = row.business_conditions
        else:
            business_conditions = ''

        if (row.business_event):
            business_event = row.business_event
        else:
            business_event = ''

        if (row.post_code):
            post_code = row.post_code
        else:
            post_code = ''

        if (row.address):
            address = row.address
        else:
            address = ''

        if (row.office_phone):
            office_phone = row.office_phone
        else:
            office_phone = ''

        if (row.office_fax):
            office_fax = row.office_fax
        else:
            office_fax = ''

        if (row.email):
            email = row.email
        else:
            email = ''

        if (row.note):
            note = row.note
        else:
            note = ''

        if (row.file):
            file = row.file.url
        else:
            file = ''

        appendResult({
            'id': row.id,
            'company_division': row.company_division,
            'company_name': row.company_name,
            'licensee_number': row.licensee_number,

            'owner_name': owner_name,
            'business_conditions': business_conditions,
            'business_event': business_event,
            'post_code': post_code,
            'address': address,
            'office_phone': office_phone,
            'office_fax': office_fax,
            'email': email,
            'note': note,

            'file': file,
        })

    return results
