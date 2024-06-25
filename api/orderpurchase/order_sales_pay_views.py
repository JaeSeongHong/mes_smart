from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views import View

from Pagenation import rounds, tof
from api.models import ItemIn, ItemOut, ItemOutPay, UserMaster
from lib import Pagenation
from msgs import msg_error, msg_pk, msg_delete_fail


class Order_sales_pay_create(View):

    def post(self, request):
        user_id = request.COOKIES['user_id']
        # enterprise_id = request.COOKIES['enterprise_id']
        user = UserMaster.objects.get(id=user_id)

        item_out_id = int(request.POST.get('item_out_id', ''))  # 입고 리스트 ID
        pay_at = request.POST.get('pay_at', '')  # 지급일자
        pay_amount = float(request.POST.get('pay_amount', '0'))  # 지급액
        etc = request.POST.get('etc', '')  # 비고

        if pay_at == '':
            pay_at = None

        context = {}

        try:
            with transaction.atomic():

                obj = ItemOutPay.objects.create(
                    item_out_id=item_out_id,
                    pay_at=pay_at,  # 지급일자
                    pay_amount=pay_amount,  # 지급액
                    etc=etc,  # 비고
                    enterprise=user.enterprise,  # 업체
                )
                context['pay_id'] = str(obj.id)

        except Exception as e:
            msg = msg_error
            for i in e.args:

                if i == 1048:
                    msg = 'null 이 될 수 없습니다.'
                    break

                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 정보가 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        context['result'] = 'ok'
        return JsonResponse(context)


class Order_sales_pay_read(View):
    def get(self, request, *args, **kwargs):
        item_out_id = request.GET.get('item_out_id', '')
        if item_out_id == '':
            item_out_id = 0

        item_out_id = int(item_out_id)
        qs = ItemOutPay.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('id')
        qs = qs.filter(item_out_id=item_out_id)

        results = get_results(qs)

        context = {}
        context['results'] = results

        return JsonResponse(context, safe=False)


class Order_sales_pay_update(View):

    def post(self, request):
        user_id = request.COOKIES['user_id']
        # enterprise_id = request.COOKIES['enterprise_id']
        user = UserMaster.objects.get(id=user_id)

        pay_click_id = int(request.POST.get('pay_click_id', ''))  # pay 리스트 ID
        pay_at = request.POST.get('pay_at', '')  # 지급일자
        pay_amount = float(request.POST.get('pay_amount', '0'))  # 지급액
        etc = request.POST.get('etc', '')  # 비고

        if pay_at == '':
            pay_at = None

        context = {}

        try:
            with transaction.atomic():
                obj = ItemOutPay.objects.get(pk=pay_click_id)

                # 업데이트
                obj.pay_at = pay_at  # 지급일자
                obj.pay_amount = pay_amount  # 지급액
                obj.etc = etc  # 비고
                obj.save()

        except Exception as e:
            msg = msg_error
            for i in e.args:
                if i == 1062:
                    # msg = msg_1062
                    msg = '중복된 번호가 존재합니다.'
                    break

            return JsonResponse({'error': True, 'message': msg})

        context['result'] = 'ok'
        return JsonResponse(context)


class Order_sales_pay_delete(View):

    def post(self, request):
        pk = request.POST.get('pk', '')

        if (pk == ''):
            msg = msg_pk
            return JsonResponse({'error': True, 'message': msg})

        try:
            with transaction.atomic():
                obj = ItemOutPay.objects.get(pk=int(pk))
                obj.delete()

        except Exception as e:
            msg = msg_delete_fail
            return JsonResponse({'error': True, 'message': msg})

        context = {}
        context['id'] = pk
        return JsonResponse(context)


def get_results(qs):
    results = []
    appendResult = results.append

    for row in qs:

        appendResult({
            'id': row.id,
            'item_out': row.item_out.id,  # 출고 ID
            'pay_at': row.pay_at,  # 지급일자
            'pay_amount': tof(row.pay_amount, 3),  # 지급액
            'etc': row.etc,  # 비고
        })

    return results
