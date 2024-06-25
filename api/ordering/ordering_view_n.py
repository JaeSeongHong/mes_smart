import traceback
from datetime import datetime, date

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import UserMaster, Request, CustomerMaster, Ordering, ItemOut, ItemMaster, EnterpriseMaster, CodeMaster
from lib import Pagenation
from msgs import msg_create_fail, msg_error, msg_pk, msg_delete_fail, msg_update_fail


class Ordering_in(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'ordering/ordering_input.html', context)


class Ordering_create(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=user_id)

        # 거래처코드, 거래처명, 사업자번호
        # 대표자명, 업태, 종목, 우편번호, 주소, 회사번호, 팩스번호, 담당자, 직급, 연락처, 이메일, 비고
        # 품번, 품명, 수량, (단가)
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

        # 주문서번호 생성하고..
        ordering_code = generate_code('O', Ordering, 'ordering_code', user)

        # export_status = "미출하" 가 기본
        # enable = 0 이 기본
        # provide_sum
        # provide_surtax 세금여부? 가져오고,

        provide_surtax = request.POST.get('provide_surtax', '')

        if (provide_surtax == "true"):
            provide_surtax = True
        else:
            provide_surtax = False

        provide_sum = request.POST.get('provide_sum', 0)

        # division_id 거래처구분인데 기존에 값들 다 널로 들어가 있음...
        # 화면에 뿌려준 거래처구분 값이 없어서, 값 넣으려면 별도로 가져와야 함.

        due_date = request.POST.get('due_date', '')
        pay_option = request.POST.get('pay_option', '')
        guarantee_date = request.POST.get('guarantee_date', '')
        deliver_place = request.POST.get('deliver_place', '')
        note = request.POST.get('note', '')

        context = {}

        # 오늘날짜
        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            obj = Ordering.objects.create(

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

                export_status="미출하",
                enable=0,
                provide_sum=provide_sum,  # 얘 계산해서 가져와야 하고,
                provide_surtax=provide_surtax,
                # division_id= 널값이고,

                ordering_code=ordering_code,

                due_date=due_date,
                pay_option=pay_option,
                guarantee_date=guarantee_date,
                deliver_place=deliver_place,
                note=note,

                code_id=code,

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
            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 주문서가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class Ordering_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')

        # 검색인자 - 거래처, 의뢰일자(시작일, 종료일)
        customer_id = request.GET.get('customer_id', '')

        fr_date = request.GET.get('fr_date', '')
        to_date = request.GET.get('to_date', '')

        # 주문서 리스트 클릭했을 때 세부정보 보기 위한
        pk = request.GET.get('pk')

        last = request.GET.get('last')

        qs = Ordering.objects.filter(enterprise__name=request.COOKIES['enterprise_name']) \
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


# 일단 안씀.
class Ordering_update(View):

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
class Ordering_delete(View):

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


class OrderingAPI(APIView):
    #
    # def get_object(self, pk):
    #     try:
    #         return KTVBroadDispatch.objects.get(pk=pk)
    #     except KTVBroadDispatch.DoesNotExist:
    #         raise Http404
    #
    # def get(self, request, format=None):
    #     dispatch = KTVBroadDispatch.objects.all()
    #     serializer = KTVDispatchSerializer(dispatch, many=True)
    #     return Response(serializer.data)

    @transaction.atomic
    def post(self, request, format=None):

        print('ordring api data:')
        print(request.data)
        enterprise = EnterpriseMaster.objects.get(name="TEST_상규")
        user = UserMaster.objects.get(username="TEST_상규 관리자")
        out = ItemOut.objects.filter(enterprise=enterprise)

        duplicate_count = 0
        item_non_exist_count = 0
        item_non_exist_list = []

        try:
            for x in request.data:
                print(x['oddate'][:10])
                if out.filter(
                    out_at=x['oddate'][:10],
                    item__name=x['name'],
                    item__code=x['itnum'],
                    item__nice_number=x['nicenum'],
                    # item__brand__explain=x['brand'],
                    # item__item_group__explain=x['caid'],
                    out_amount=x['qty'],
                    out_price=x['price']
                ).count() == 0:
                    try:
                        it = ItemMaster.objects.get(
                            name=x['name'],
                            code=x['itnum'],
                            nice_number=x['nicenum'],
                            # brand__explain=x['brand'],
                            # item_group__explain=x['caid'],
                            enterprise=enterprise
                        )
                        # enterprise = EnterpriseMaster.objects.get(name="유성산업")
                        location = CodeMaster.objects.get(name="쇼핑몰 창고", enterprise=enterprise)
                        customer = CustomerMaster.objects.get(name="나이스필터 쇼핑몰", enterprise=enterprise)

                        pre = ItemOut.objects.create(
                            num=generate_code('O', ItemOut, 'num', user),
                            out_at=x['oddate'][:10],
                            item=it,
                            # brand__explain=x['brand'],
                            # item_group__explain=x['caid'],
                            out_amount=x['qty'],
                            out_price=x['price'],
                            location=location,
                            purchase_from=customer,
                            purpose="쇼핑몰 주문",

                            created_at=timezone.now(),
                            updated_at=timezone.now(),
                            enterprise=enterprise,
                        )

                        item = ItemMaster.objects.get(pk=it.id)
                        now_stock = item.stock - float(x['qty'])
                        item.stock = now_stock
                        item.save()

                        pre.current_amount = now_stock
                        pre.save()
                    except Exception as e:
                        print(e)
                        print(item_non_exist_count)
                        item_non_exist_list[item_non_exist_count] = x
                        item_non_exist_count += 1
                        # return Response({
                        #     'success': False,
                        #     'error': 'Item does not exist',
                        # }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    duplicate_count += 1
                    continue
                    # return Response({
                    #     'success': False,
                    #     'error': 'some of data are duplicated!',
                    # }, status=status.HTTP_400_BAD_REQUEST)
            return Response({'success': True,
                             'status': status.HTTP_200_OK,
                             'duplication': str(duplicate_count) + " duplicated data have been ignored",
                             'item_non_exists': str(item_non_exist_count) + " items does not exists",
                             'item_non_exists_list': item_non_exist_list},
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return Response({
                'success': False,
                'error': 'error has been occurred'}, status=status.HTTP_400_BAD_REQUEST)


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
            customer_id = row.code.id
            code_name = row.code.name
            code_code = row.code.code
        else:
            customer_id = ''
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

            'ordering_code': row.ordering_code,
            'code_id': customer_id,
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
            'export_status': row.export_status,

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
