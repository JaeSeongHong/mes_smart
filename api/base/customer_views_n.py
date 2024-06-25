from datetime import datetime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from openpyxl import load_workbook

from api.base.base_form import customer_fm
from api.models import CustomerMaster, UserMaster, CodeMaster
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class CustomerMaster_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['cu'] = customer_fm(request.GET, request.COOKIES['enterprise_name'])
        return render(request, 'basic_information/customer.html', context)


class CustomerMaster_create(View):

    @transaction.atomic
    def post(self, request):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        code = request.POST.get('code', '')
        name = request.POST.get('name', '')

        division = request.POST.get('division', '')
        if division == '':
            division = None
        else:
            division = int(division)

        licensee_number = request.POST.get('licensee_number', '')
        owner_name = request.POST.get('owner_name', '')
        business_conditions = request.POST.get('business_conditions', '')
        business_event = request.POST.get('business_event', '')
        postal_code = request.POST.get('postal_code', '')
        address = request.POST.get('address', '')
        office_phone = request.POST.get('office_phone', '')
        office_fax = request.POST.get('office_fax', '')
        charge_name = request.POST.get('charge_name', '')
        charge_level = request.POST.get('charge_level', '')
        charge_phone = request.POST.get('charge_phone', '')
        email = request.POST.get('email', '')
        etc = request.POST.get('etc', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = CustomerMaster.objects.create(

                code=code,  # 거래처코드
                name=name,  # 거래처명
                division_id=division,  # 거래구분

                licensee_number=licensee_number,  # 사업자번호, it will cause bad occasions..
                owner_name=owner_name,  # 대표자명
                business_conditions=business_conditions,  # 업태
                business_event=business_event,  # 종목
                postal_code=postal_code,  # 우편번호
                address=address,  # 주소
                office_phone=office_phone,  # 회사전화번호, it will cause bad occasions..
                office_fax=office_fax,  # 회사팩스번호, it will cause bad occasions..
                charge_name=charge_name,  # 담당자, it will cause bad occasions..
                charge_phone=charge_phone,  # 담당자연락처, it will cause bad occasions..
                charge_level=charge_level,  # 직급
                email=email,  # 6/5 설계서 email
                enable=1,  # 사용구분
                etc=etc,  # 비고

                created_by=user,  # 최초작성자
                updated_by=user,  # 최종작성자
                created_at=d_today,  # 최초작성일
                updated_at=d_today,  # 최종작성일
                enterprise=user.enterprise,  # 업체
            )

            if obj:
                context = get_res(context, obj)
            else:
                msg = msg_create_fail
                return JsonResponse({'error': True, 'message': msg})

        except Exception as e:

            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 거래처가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class CustomerMaster_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')

        # 검색인자
        cu_division_sch = request.GET.get('cu_division_sch', '')
        cu_name_sch = request.GET.get('cu_name_sch', '')

        # 의리서 작성에서 거래처 검색하기 위해서 필요함.
        cu_id_sch = request.GET.get('cu_id_sch', '')

        # is_superuser = request.COOKIES['is_superuser']
        # print(is_superuser)

        qs = CustomerMaster.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('-id')

        custom_id = request.GET.get('custom_id', '')
        if custom_id :
           qs = qs.filter(id=custom_id)

        # 슈퍼 유저 구분 필요 없단다... ###
        # if is_superuser == 'true':
        #     qs = CustomerMaster.objects.all().order_by('-id')
        # else:

        # Search
        if cu_division_sch != '':
            sc = CodeMaster.objects.get(id=cu_division_sch)
            if sc:
                qs = qs.filter(division_id=sc.id)

        if cu_name_sch != '':
            qs = qs.filter(id=cu_name_sch)

        if cu_id_sch != '':
            qs = qs.filter(id=cu_id_sch)

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


class CustomerMaster_update(View):

    @transaction.atomic
    def post(self, request):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)
        # enterprise = request.COOKIES['enterprise_id']

        pk = request.POST.get('pk', '')
        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        code = request.POST.get('code', '')
        name = request.POST.get('name', '')

        division = request.POST.get('division', '')
        if division == '':
            division = None
        else:
            division = int(division)

        licensee_number = request.POST.get('licensee_number', '')
        owner_name = request.POST.get('owner_name', '')
        business_conditions = request.POST.get('business_conditions', '')
        business_event = request.POST.get('business_event', '')
        postal_code = request.POST.get('postal_code', '')
        address = request.POST.get('address', '')
        office_phone = request.POST.get('office_phone', '')
        office_fax = request.POST.get('office_fax', '')
        charge_name = request.POST.get('charge_name', '')
        charge_level = request.POST.get('charge_level', '')
        charge_phone = request.POST.get('charge_phone', '')
        email = request.POST.get('email', '')
        etc = request.POST.get('etc', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:

            obj = CustomerMaster.objects.get(pk=int(pk))

            obj.code = code  # 코드
            obj.name = name  # 거래처명
            obj.division_id = division  # 거래구분

            obj.licensee_number = licensee_number  # 사업자번호
            obj.owner_name = owner_name  # 대표자명
            obj.business_conditions = business_conditions  # 업태
            obj.business_event = business_event  # 종목
            obj.postal_code = postal_code  # 우편번호
            obj.address = address  # 주소
            obj.office_phone = office_phone  # 회사전화번호
            obj.office_fax = office_fax  # 팩스

            obj.charge_name = charge_name  # 담당자
            obj.charge_phone = charge_phone  # 연락처
            obj.charge_level = charge_level  # 직급
            obj.email = email  # 메일
            # 사용구분
            obj.etc = etc  # 비고

            obj.updated_by = user  # 최종 작성자
            obj.updated_at = d_today  # 최종 작성일

            obj.enterprise = user.enterprise  # 업체

            obj.save()

            if obj:
                context = get_res(context, obj)
            else:
                msg = msg_update_fail
                return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    # 수정할 때는 발생하지 않는 에러일텐데? 일단 냅둠.
                    msg = '중복된 거래처가 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class CustomerMaster_delete(View):

    @transaction.atomic
    def post(self, request):
        pk = request.POST.get('pk', '')
        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = CustomerMaster.objects.get(pk=int(pk))
            inv.delete()
        except Exception as e:
            msg = msg_delete_fail
            return JsonResponse({'error': True, 'message': msg})

        context = {}
        context['id'] = pk
        return JsonResponse(context)


class CustomerMaster_excel(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)
        excel = request.FILES.get('excel')

        wb = load_workbook(excel, data_only=True)
        ws = wb.worksheets[0]

        for row in ws:
            if row[0].value == '사업자번호':
                pass
            else:
                code = row[0].value
                name = row[1].value
                licensee_number = row[2].value
                owner_name = row[3].value
                business_conditions = row[4].value
                business_event = row[5].value
                postal_code = row[6].value
                address = row[7].value
                office_phone = row[8].value
                office_fax = row[9].value
                charge_name = row[10].value
                charge_level = row[11].value
                charge_phone = row[12].value
                email = row[13].value
                etc = row[15].value
                print(business_conditions)

                try:
                    customer = CustomerMaster.objects.get(enterprise=user.enterprise, code=code)
                except CustomerMaster.DoesNotExist:
                    CustomerMaster.objects.create(
                        code=code,
                        licensee_number=licensee_number,
                        name=name,
                        owner_name=owner_name,
                        business_conditions=business_conditions,
                        business_event=business_event,
                        postal_code=postal_code,
                        address=address,
                        office_phone=office_phone,
                        office_fax=office_fax,
                        charge_name=charge_name,
                        charge_level=charge_level,
                        charge_phone=charge_phone,
                        email=email,
                        etc=etc,

                        enterprise=user.enterprise,
                        created_by=user,
                        updated_by=user
                    )
                else:
                    customer.code = code
                    customer.licensee_number = licensee_number
                    customer.name = name
                    customer.owner_name = owner_name
                    customer.business_conditions = business_conditions
                    customer.business_event = business_event
                    customer.postal_code = postal_code
                    customer.address = address
                    customer.office_phone = office_phone
                    customer.office_fax = office_fax
                    customer.charge_name = charge_name
                    customer.charge_level = charge_level
                    customer.charge_phone = charge_phone
                    customer.email = email
                    customer.etc = etc

                    customer.enterprise = user.enterprise,
                    customer.updated_by = user

                    customer.save()

        context = {}
        return JsonResponse(context)

def get_res(context, obj):
    context['id'] = obj.id
    context['code'] = obj.code
    context['name'] = obj.name
    context['licensee_number'] = obj.licensee_number

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
    context['enable'] = obj.enable
    context['etc'] = obj.etc
    context['created_at'] = obj.created_at
    context['updated_at'] = obj.updated_at
    context['created_by_id'] = obj.created_by.id
    context['enterprise_id'] = obj.enterprise.id
    context['updated_by_id'] = obj.updated_by.id

    if (obj.division):
        context['division_id'] = obj.division.id
        context['division_name'] = obj.division.name
    else:
        context['division_id'] = ''
        context['division_name'] = ''

    return context


def get_results(qs):
    results = []
    appendResult = results.append

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

        if (row.postal_code):
            postal_code = row.postal_code
        else:
            postal_code = ''

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

        if (row.charge_name):
            charge_name = row.charge_name
        else:
            charge_name = ''

        if (row.charge_phone):
            charge_phone = row.charge_phone
        else:
            charge_phone = ''

        if (row.charge_level):
            charge_level = row.charge_level
        else:
            charge_level = ''

        if (row.email):
            email = row.email
        else:
            email = ''

        if (row.etc):
            etc = row.etc
        else:
            etc = ''

        if (row.division_id):
            division_id = row.division.id
            division_name = row.division.name
        else:
            division_id = ''
            division_name = ''

        appendResult({
            'id': row.id,
            'code': row.code,
            'name': row.name,
            'licensee_number': row.licensee_number,

            'owner_name': owner_name,
            'business_conditions': business_conditions,
            'business_event': business_event,
            'postal_code': postal_code,
            'address': address,
            'office_phone': office_phone,
            'office_fax': office_fax,
            'charge_name': charge_name,
            'charge_phone': charge_phone,
            'charge_level': charge_level,
            'email': email,
            'enable': row.enable,
            'etc': etc,

            'created_by': row.created_by.username,
            'updated_by': row.updated_by.username,
            'created_at': row.created_at,
            'updated_at': row.updated_at,
            'enterprise': row.enterprise_id,

            'division_id': division_id,
            'division_name': division_name,

        })

    return results
