from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views import View

from Pagenation import tof
from api.models import ItemOut, ItemOutPay
from lib import Pagenation


class Order_sales_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')

        make_from = request.GET.get('make_from', '')  # form
        make_to = request.GET.get('make_to', '')  # to
        customer_id = request.GET.get('customer_id', '')
        code_id = request.GET.get('code_id', '')

        qs = ItemOut.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('-id')

        # 단가가 0 이상인 경우만
        qs = qs.filter(~Q(out_price=0))

        # Search
        if make_from != '':
            qs = qs.filter(out_at__gte=make_from)

        if make_to != '':
            qs = qs.filter(out_at__lte=make_to)

        if customer_id != '':
            qs = qs.filter(purchase_from_id=customer_id)


        if code_id != '':
            qs = qs.filter(item_id=code_id)


        # 매출 합계
        total = qs.aggregate(
            out_amount_total=Coalesce(Sum('out_amount'), 0),
            out_price_total=Coalesce(Sum('out_price'), 0),  # 단가
        )
        out_amount_total = total['out_amount_total']

        # 소계 - 품번별
        # qs_sorted = qs.values('item_id').annotate(
        #     out_amount_sum=Sum('out_amount'),
        #     out_price_sum=Sum('out_price'),  # 출고단가
        # ).order_by('item_id')

        # 소계 - 거래처별
        qs_sorted = qs.values('purchase_from').annotate(
            out_amount_sum=Sum('out_amount'),
            out_price_sum=Sum('out_price'),  # 출고단가
        ).order_by('purchase_from')

        lists = []

        total_supply_sum = 0  # 매출합계 - 공급가 합
        total_surtax_sum = 0  # 매출합계 - 부가세 합

        if qs_sorted:
            for row in qs_sorted:
                supply_sum = 0
                surtax_sum = 0
                supply_surtax_sum = 0

                _purchase_from = row['purchase_from']
                sqs = qs.filter(purchase_from=_purchase_from).order_by('id')

                if sqs:
                    results = get_results_list(sqs)
                    lists.extend(results)

                    # lists.extend(sqs.values())
                    a = results
                    for res in results:
                        supply_sum += res['supply']
                        surtax_sum += res['surtax']
                        supply_surtax_sum += res['supply'] + res['surtax']

                        total_supply_sum += res['supply']
                        total_surtax_sum += res['surtax']

                list = []
                appendList = list.append
                appendList({
                    'type': 'sum',
                    'out_amount_sum': tof(row['out_amount_sum'], 3),  # 출고수량
                    'out_price_sum': row['out_price_sum'],  # 출고단가
                    'supply_sum': supply_sum,  # 공급가액
                    'surtax_sum': surtax_sum,  # 부가세액
                    'supply_surtax_sum': supply_surtax_sum,  # 합계금액
                })

                lists = lists + list
                pass

        # Pagination
        # qs_ps = Pagenation(qs, _size, _page)
        qs_ps = Pagenation(lists, _size, _page)

        pre = int(_page) - 1
        url_pre = "/?page_size=" + _size + "&page=" + str(pre)
        if pre < 1:
            url_pre = None

        next = int(_page) + 1
        url_next = "/?page_size=" + _size + "&page=" + str(next)
        if next > qs_ps.paginator.num_pages:
            url_next = None

        # results = get_results(qs_ps)
        results = get_results2(qs_ps)

        context = {}
        context['count'] = qs_ps.paginator.count
        context['previous'] = url_pre
        context['next'] = url_next
        context['results'] = results

        # 매출합계
        context['total_out_amount'] = tof(total['out_amount_total'], 3)  # 수량
        context['total_out_price'] = tof(total['out_price_total'], 3)  # 단가
        context['total_supply'] = tof(total_supply_sum, 3)  # 공급가 합
        context['total_surtex'] = tof(total_surtax_sum, 3)  # 부가세 합
        context['total_supply_surtex'] = tof(total_supply_sum + total_surtax_sum, 3)  # 합계 금액

        return JsonResponse(context, safe=False)


# Queryset Style 변환
def get_results(qs):
    results = []
    appendResult = results.append

    for row in qs.object_list:
        if row.item.purchase_from:
            from_id = row.item.purchase_from.id
            from_name = row.item.purchase_from.name
        else:
            from_id = ''
            from_name = ''

        appendResult({
            'id': row.id,
            'num': row.num,  # 출고번호
            'from_id': from_id,  # 거래처 ID
            'from_name': from_name,  # 거래처 명
            'item_id': row.item.id,  # 품번 ID
            'item_code': row.item.code,  # 품번
            'item_name': row.item.name,  # 품명

            'out_at': row.out_at,  # 출고일자
            'out_amount': tof(row.out_amount, 3),  # 출고수량
            'out_price': tof(row.out_price, 3),  # 출고단가

            'supply': tof(row.out_amount * row.out_price, 3),  # 공급가액 = 수량 * 단가
            'surtax': tof(row.out_amount * row.out_price * 0.1, 3),  # 부가세액 = 공급가액 * 0.1
            'sum': tof((row.out_amount * row.out_price) + (row.out_amount * row.out_price * 0.1), 3),  # 합계금액 = 공급가액 + 부가세액
            'out_price': tof(row.out_price, 3),  # 지급일자
            'etc': row.etc,  # 비고
        })

    return results


def get_results_list(qs):
    results = []
    appendResult = results.append

    for row in qs:
        if row.purchase_from:
            from_id = row.purchase_from.id
            from_name = row.purchase_from.name
        else:
            from_id = ''
            from_name = ''

        iqs = ItemOutPay.objects.filter(item_out_id=row.id).order_by('id')

        pay_at = ''  # 지급일자
        pay_amount = 0  # 지급액
        remain_amount = 0  # 미지급액

        if iqs:
            pay_at = iqs.order_by('pay_at').last().pay_at
            pay = iqs.aggregate(
                pay_amount_sum=Coalesce(Sum('pay_amount'), 0),
            )
            pay_amount = pay['pay_amount_sum']

        supply = tof(row.out_amount * row.out_price, 3)

        if (row.surtax_chk == True):
            surtax = tof(row.out_amount * row.out_price * 0.1, 3)
        else:
            surtax = 0

        sum = tof(supply + surtax, 3)
        remain_amount = tof(sum - pay_amount, 3)

        pay_div = '미수금'  # '부분지급' '지급완료'
        if pay_amount > 0:
            pay_div = '부분수금'
            if pay_amount >= sum:
                pay_div = '수금완료'

        appendResult({
            'type': 'list',
            'id': row.id,
            'num': row.num,  # 출고번호
            'from_id': from_id,  # 거래처 ID
            'from_name': from_name,  # 거래처 명
            'item_id': row.item.id,  # 품번 ID
            'item_code': row.item.code,  # 품번
            'item_name': row.item.name,  # 품명

            'out_at': row.out_at,  # 출고일자
            'out_amount': tof(row.out_amount, 3),  # 출고수량
            'out_price': tof(row.out_price, 3),  # 출고단가

            'supply': supply,  # 공급가액 = 수량 * 단가
            'surtax': surtax,  # 부가세액 = 공급가액 * 0.1
            'sum': sum,  # 합계금액 = 공급가액 + 부가세액

            'pay_at': pay_at,  # 지급일자
            'pay_amount': tof(pay_amount, 3),  # 지급액
            'remain_amount': remain_amount,  # 미지급액
            'pay_div': pay_div,  # 지급구분

            'etc': row.etc,  # 비고
        })

    return results

# Dict Style 변환
def get_results2(qs):
    results = []
    appendResult = results.append

    for row in qs.object_list:
        if row['type'] == 'list':
            appendResult({
                'type': 'list',
                'id': row['id'],
                'num': row['num'],  # 출고번호

                'from_id': row['from_id'],  # 거래처 ID
                'from_name': row['from_name'],  # 거래처 명

                'item_id': row['item_id'],  # 품번 ID
                'item_code': row['item_code'],  # 품번
                'item_name': row['item_name'],  # 품명

                'out_at': row['out_at'],  # 출고일자
                'out_amount': row['out_amount'],  # 출고수량
                'out_price': row['out_price'],  # 출고단가

                'supply': row['supply'],  # 공급가액 = 수량 * 단가
                'surtax': row['surtax'],  # 부가세액 = 공급가액 * 0.1
                'sum': row['sum'],  # 합계금액 = 공급가액 + 부가세액

                'pay_at': row['pay_at'],  # 지급일자
                'pay_amount': row['pay_amount'],  # 지급액
                'remain_amount': row['remain_amount'],  # 미지급액
                'pay_div': row['pay_div'],  # 지급구분

                'etc': row['etc'],  # 비고
            })

        elif row['type'] == 'sum':
            appendResult({
                'type': 'sum',
                'out_amount_sum': row['out_amount_sum'],
                'out_price_sum': row['out_price_sum'],
                'supply_sum': row['supply_sum'],
                'surtax_sum': row['surtax_sum'],
                'supply_surtax_sum': row['supply_surtax_sum'],
            })

    return results