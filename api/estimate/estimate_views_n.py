import re
from datetime import datetime, date

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from api.models import UserMaster, Request, CustomerMaster, Estimate
from api.temp_volt_monitoring.send_mail import send_gmail, send_gmail_pdf
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class Estimate_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'estimate/estimate_input.html', context)


class Estimate_create(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        # 거래처코드, 거래처명, 사업자번호
        # 대표자명, 업태, 종목, 우편번호, 주소, 회사번호, 팩스번호, 담당자, 직급, 연락처, 이메일, 비고
        # 품번, 품명, 수량
        # 품명상세, 단위, 비고,
        # 첨부파일

        code = request.POST.get('code', '')
        licensee_number = request.POST.get('licensee_number', '')
        owner_name = request.POST.get('owner_name', '')
        business_conditions = request.POST.get('business_conditions', '')
        business_event = request.POST.get('business_event', '')
        postal_code = request.POST.get('postal_code', '')
        address = request.POST.get('address', '')
        office_phone = request.POST.get('office_phone', '')
        office_fax = request.POST.get('office_fax', '')
        charge_name = request.POST.get('charge_name', '')
        charge_phone = request.POST.get('charge_phone', '')
        charge_level = request.POST.get('charge_level', '')
        email = request.POST.get('email', '')
        etc = request.POST.get('etc', '')

        # 견적서번호 생성하고..
        estimate_code = generate_code('E', Estimate, 'estimate_code', user)

        provide_sum = request.POST.get('provide_sum', '')
        provide_surtax = request.POST.get('provide_surtax', '')

        if (provide_surtax == "true"):
            provide_surtax = True
        else:
            provide_surtax = False

        due_date = request.POST.get('due_date', '')
        pay_option = request.POST.get('pay_option', '')
        guarantee_date = request.POST.get('guarantee_date', '')
        deliver_place = request.POST.get('deliver_place', '')
        note = request.POST.get('note', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = Estimate.objects.create(
                code_id=code,

                licensee_number=licensee_number,
                owner_name=owner_name,
                business_conditions=business_conditions,
                business_event=business_event,
                postal_code=postal_code,
                address=address,
                office_phone=office_phone,
                office_fax=office_fax,
                charge_name=charge_name,
                charge_phone=charge_phone,
                charge_level=charge_level,
                email=email,
                etc=etc,

                estimate_code=estimate_code,

                provide_sum=provide_sum,
                provide_surtax=provide_surtax,

                due_date=due_date,
                pay_option=pay_option,
                guarantee_date=guarantee_date,
                deliver_place=deliver_place,
                note=note,

                # 견적서의 사용유무? 왜 있는 걸까? 어따 써먹음?
                enable=0,

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
            print('견적서 등록 중에 이게 발생했다고?')
            print(e)
            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 견적서가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class Estimate_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')

        # 검색인자 - 거래처, 의뢰일자(시작일, 종료일)
        customer_id = request.GET.get('customer_id', '')

        fr_date = request.GET.get('fr_date', '')
        to_date = request.GET.get('to_date', '')

        # 견적서 리스트 클릭했을 때 세부정보 보기 위한
        pk = request.GET.get('pk')

        last = request.GET.get('last')

        qs = Estimate.objects.filter(enterprise__name=request.COOKIES['enterprise_name']) \
            .order_by('-id')

        # Search
        if customer_id != '':
            sc = CustomerMaster.objects.get(id=customer_id)
            if sc:
                qs = qs.filter(code_id=sc.id)

        if fr_date != '':
            qs = qs.filter(created_at__gte=fr_date)

        if to_date != '':
            qs = qs.filter(created_at__lte=to_date)

        if pk is not None:
            qs = qs.filter(pk=pk)

        if last == 'true':
            last_qs = qs.first()
            if last_qs is not None:
                qs = qs.filter(id=last_qs.id)

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


class Estimate_update(View):

    @transaction.atomic
    def post(self, request):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        pk = request.POST.get('pk')

        code = request.POST.get('code', '')
        licensee_number = request.POST.get('licensee_number', '')
        owner_name = request.POST.get('owner_name', '')
        business_conditions = request.POST.get('business_conditions', '')
        business_event = request.POST.get('business_event', '')
        postal_code = request.POST.get('postal_code', '')
        address = request.POST.get('address', '')
        office_phone = request.POST.get('office_phone', '')
        office_fax = request.POST.get('office_fax', '')
        charge_name = request.POST.get('charge_name', '')
        charge_phone = request.POST.get('charge_phone', '')
        charge_level = request.POST.get('charge_level', '')
        email = request.POST.get('email', '')
        etc = request.POST.get('etc', '')

        provide_sum = request.POST.get('provide_sum', '')
        provide_surtax = request.POST.get('provide_surtax', '')

        if (provide_surtax == "true"):
            provide_surtax = True
        else:
            provide_surtax = False

        due_date = request.POST.get('due_date', '')
        pay_option = request.POST.get('pay_option', '')
        guarantee_date = request.POST.get('guarantee_date', '')
        deliver_place = request.POST.get('deliver_place', '')
        note = request.POST.get('note', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = Estimate.objects.get(pk=int(pk))

            obj.code_id = code
            obj.licensee_number = licensee_number
            obj.owner_name = owner_name
            obj.business_conditions = business_conditions
            obj.business_event = business_event
            obj.postal_code = postal_code
            obj.address = address
            obj.office_phone = office_phone
            obj.office_fax = office_fax
            obj.charge_name = charge_name
            obj.charge_phone = charge_phone
            obj.charge_level = charge_level
            obj.email = email
            obj.etc = etc

            obj.provide_sum = provide_sum
            obj.provide_surtax = provide_surtax
            obj.due_date = due_date
            obj.pay_option = pay_option
            obj.guarantee_date = guarantee_date
            obj.deliver_place = deliver_place
            obj.note = note

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
                    msg = '중복된 견적서가 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


# 일단 안씀.
class Estimate_delete(View):

    @transaction.atomic
    def post(self, request):

        pk = request.POST.get('pk', '')

        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            inv = Estimate.objects.get(pk=int(pk))
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

    # enable, estimate_code, provide_sum, provide_surtax

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

    # id, 거래처코드, 거래처명, 사업자번호, // 품번, 품명, 수량 필수고
    # 그밖에 것들...
    # 오너네임, 업태, 종목, 우편번호, 주소, 사무실전화, 팩스, 담당자, 담당자 연락처, 직급, 이메일, 기타,
    # 의뢰서번호, export_status, provide_sum,
    # 페이옵션, 보증일, 납품장소, 노트, 작성일, 변경일

    # 의뢰번호, 의뢰일자, 거래처, 거래처담당자, 담당자 연락처, 작성자...

    for row in qs.object_list:
        if (row.charge_name):
            charge_name = row.charge_name
        else:
            charge_name = ''

        if (row.charge_phone):
            charge_phone = row.charge_phone
        else:
            charge_phone = ''

        if (row.code):
            code_id = row.code.id
            code_name = row.code.name
            code_code = row.code.code
        else:
            code_id = ''
            code_name = ''
            code_code = ''

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

        if (row.pay_option):
            pay_option = row.pay_option
        else:
            pay_option = ''

        if (row.due_date):
            due_date = row.due_date
        else:
            due_date = ''

        if (row.guarantee_date):
            guarantee_date = row.guarantee_date
        else:
            guarantee_date = ''

        if (row.deliver_place):
            deliver_place = row.deliver_place
        else:
            deliver_place = ''

        if (row.note):
            note = row.note
        else:
            note = ''

        appendResult({
            'id': row.id,

            'estimate_code': row.estimate_code,
            'code_id': code_id,
            'code_code': code_code,
            'code_name': code_name,
            'charge_name': charge_name,
            'charge_phone': charge_phone,

            # 사업자번호, 대표자명, 업태, 종목, 우편번호, 주소, 회사연락처, 팩스번호, 직급, 이메일, 비고
            'licensee_number': row.licensee_number,
            'owner_name': owner_name,
            'business_conditions': business_conditions,
            'business_event': business_event,
            'postal_code': postal_code,
            'address': address,
            'office_phone': office_phone,
            'office_fax': office_fax,
            'charge_level': charge_level,
            'email': email,
            'etc': etc,

            'provide_sum': row.provide_sum,
            'provide_surtax': row.provide_surtax,

            # 결제조건, 납기일, 품질보증기한, 납품장소, NOTE 내용고정
            'pay_option': pay_option,
            'due_date': due_date,
            'guarantee_date': guarantee_date,
            'deliver_place': deliver_place,
            'note': note,

            'created_by': row.created_by.username,
            'created_at': row.created_at,

            'updated_by': row.updated_by.username,
            'updated_at': row.updated_at,
        })

    return results


# 견적번호 만드는 함수
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


# 메일 보내는 함수
def sendmail_to_company_pdf(request):
    print('일단 메일보내기 타고...')
    email_form = re.compile('[a-zA-Z0-9._-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    phone_form = re.compile('\d{2,3}-\d{3,4}-\d{4}')
    customer_email = email_form.search(request.POST.get('customer_email'))

    # 새로 추가
    enter_email = email_form.search(request.POST.get('enter_email'))
    enter_fax = phone_form.search(request.POST.get('enter_fax'))
    enter_call = phone_form.search(request.POST.get('enter_call'))
    logo_img = request.POST.get('logo_img')

    if enter_email:
        enter_email = enter_email.group()
    else:
        enter_email = ""

    if enter_fax:
        enter_fax = enter_fax.group()
    else:
        enter_fax = ""

    if enter_call:
        enter_call = enter_call.group()
    else:
        enter_call = ""

    # req_my_eamil = request.POST.get('my_email')
    #
    # if req_my_eamil is not None:
    #     sc_my_email = email_form.search(request.POST.get('my_email'))
    #     my_email = sc_my_email.group()
    # else:
    #     my_email = ""

    if customer_email:
        customer_email = customer_email.group()
        # mail_info = dict(gmail_user='seoulsoftinfo@gmail.com', gmail_password='zwsixkqojsisiqpc',
        #                  sent_from='greenbi5693@gmail.com', send_to=customer_email,
        #                  Cc='ubin1101@gmail.com',
        #                  Bcc=my_email,
        #                  subject=request.POST.get('enterprise_name') + "에서 보낸 견적서입니다.",
        #                  enterprise=request.POST.get('enterprise_name'),
        #                  my_email=my_email, type="견적서")
        mail_info = dict(gmail_user='seoulsoftinfo@gmail.com', gmail_password='zwsixkqojsisiqpc',
                         sent_from=enter_email, send_to=customer_email,
                         Bcc=enter_email,
                         subject=request.POST.get('enterprise_name') + " - 발행한 견적서입니다.",
                         enterprise=request.POST.get('enterprise_name'),
                         enter_email=enter_email, enter_fax=enter_fax, enter_call=enter_call, logo_img=logo_img,
                         type="견적서")

        # 'hjlim@seoul-soft.com, greenbi5693@naver.com, ubin1101@gmail.com, ubin1101@naver.com'

        file = request.FILES.get('file', '')
        send_gmail_pdf(mail_info, file)

        context = {}

        return JsonResponse(context)
    else:
        msg = 'pdf 메일 전송 실패'
        return JsonResponse({'error': True, 'message': msg})
