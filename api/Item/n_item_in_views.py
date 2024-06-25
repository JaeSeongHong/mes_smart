from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views import View

from api.models import ItemIn, ItemOut
from lib import Pagenation


class Material_input_read(View):
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '1')
        _size = request.GET.get('page_size', '1')
        item_name_search = request.GET.get('item_name_search', '')
        fr_date = request.GET.get('fr_date', '')
        to_date = request.GET.get('to_date', '')
        status = request.GET.get('status', '')

        qs = ItemIn.objects.filter(enterprise__name=request.COOKIES['enterprise_name']).order_by('-id')

        # Search
        if item_name_search != '':
            qs = qs.filter(item_id=item_name_search)

        if fr_date != '':
            qs = qs.filter(in_at__gte=fr_date)

        if to_date != '':
            qs = qs.filter(in_at__lte=to_date)


        # 불용자재만 Search
        if status == "1":
            new_qs = ItemIn.objects.none()

            for row in qs:
                remain = get_remain(row)  # 한번만 돌리는 방법은 없을까?
                if (remain > 0):
                    new_qs |= ItemIn.objects.filter(id=row.id)

            qs = new_qs

            import datetime
            today = str(datetime.date.today())
            qs = qs.filter(check_at__lte=today, )

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


def get_results(qs):
    results = []
    appendResult = results.append

    for row in qs.object_list:

        if (row.item.model):
            model_id = row.item.model.id
            model_name = row.item.model.name
        else:
            model_id = ''
            model_name = ''

        if (row.item.item_division):
            item_division_id = row.item.item_division.id
            item_division_name = row.item.item_division.name
        else:
            item_division_id = ''
            item_division_name = ''

        remain = get_remain(row)

        over = False
        if remain > 0:
            from datetime import datetime
            today = datetime.today()

            if row.check_at:
                check_time = datetime.strptime(str(row.check_at), "%Y-%m-%d")

                diff = check_time - today
                diff_day = diff.days

                if diff_day < 0:
                    over = True

        appendResult({
            'id': row.id,
            'num': row.num,  # 입고번호
            'item_code': row.item.code,  # 품번
            'item_name': row.item.name,  # 품명
            'item_created_at': row.item_created_at,  # 자재생산일자
            'check_at': row.check_at,  # 검사일자, 에이징타임
            'in_at': row.in_at,  # 입고일자
            'in_amount': row.in_amount,  # 입고수량

            'model_id': model_id,
            'model_name': model_name,

            'item_division_id': item_division_id,
            'item_division_name': item_division_name,
            'remain': remain,
            'over': over,

        })

    return results


def get_remain(obj):
    out_will = 0
    remain = 0

    # 출고합
    qs_out = ItemOut.objects.filter(item_id=obj.item_id)
    if qs_out:
        amount_out = qs_out.aggregate(sum=Coalesce(Sum('out_amount'), 0))
        out_will = amount_out['sum']

    # 입고 계산
    qs_in = ItemIn.objects.filter(item_id=obj.item_id, id__lte=obj.id).order_by('id')
    if qs_in:
        for row in qs_in:
            if out_will > 0:
                if out_will >= row.in_amount:
                    out_will = out_will - row.in_amount

                else:
                    remain = row.in_amount - out_will
                    out_will = 0

            else:
                remain = obj.in_amount

    return remain
