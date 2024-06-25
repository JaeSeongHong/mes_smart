import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Case, When, F, IntegerField, Avg, Q, Prefetch
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from api.Item.item_form import item_form
from api.base.base_form import customer_fm, user_fm, facilities_fm, item_fm, order_company_fm, group_code_fm, \
    request_fm, estimate_fm, ordering_fm, enterprise_fm
from api.form import Search_Customer1, Search_Code
from api.models import Process, ItemRein, Ordering, OrderingExItems, ItemMaster, MenuMaster, Menu_Auth, \
    EnterpriseMaster, ColumnMaster, Orders, UserMaster
from api.orderpurchase.orderpurchase_form import orderpurchase_form
from customer_manage.form import Search_Customer


def index(request):
    return render(request, 'index.html', {})


def login_page(request):
    #print(request.META['HTTP_HOST'])  # 접속도메인정보
    re_url = request.META['HTTP_HOST']

    # pagePath = 'login.html'

    if re_url == 'shop.test.com':

        pagePath = 'shop/mainshop.html'

    else:
        pagePath = 'login.html'

    return render(request, pagePath, {})


def register_page(request):
    return render(request, 'register.html', {})


def register_ok(request):
    return render(request, 'register_ok.html', {})


def codemaster(request):
    context = {}
    context['gc'] = group_code_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'basic_information/codemaster.html', context)


def codemaster_manage(request):
    return render(request, 'basic_information/codemaster_managepopup.html', {})


def customer(request):
    context = {}
    context['cu'] = customer_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'basic_information/customer.html', context)


def customerg1(request):
    return render(request, 'basic_information/customer_g1.html', {})


def user(request):
    context = {}
    context['us'] = user_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'basic_information/user.html', context)


def equipment(request):
    context = {}
    context['eq'] = facilities_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'basic_information/equipment.html', context)


def facilities_form(request):
    return render(request, 'basic_information/facilities_form.html', {})


def facilities_files(request):
    return render(request, 'basic_information/facilities_files.html', {})


def item(request):
    context = {}
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'basic_information/item.html', context)


def itemg1(request):
    return render(request, 'basic_information/item_g1.html', {})


def process(request):
    return render(request, 'basic_information/process.html', {})


def bom(request):
    return render(request, 'basic_information/BOM.html', {})


def bom_hanvit(request):
    return render(request, 'basic_information/BOM_hanvit.html', {})


def bom_form_add(request):
    return render(request, 'basic_information/BOM_form_add.html', {})


def auth_user(request):
    return render(request, 'basic_information/auth_user.html', {})


def auth_customer(request):
    return render(request, 'basic_information/auth_customer.html', {})


def new_enterprise(request):
    context = {}
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 109, 'M')
    context['column'] = column
    return render(request, 'basic_information/new_enterprise_register.html', context)


def print_page(request):
    return render(request, 'basic_information/print_page.html', {})


def volt_info(request):
    return render(request, 'monitoring/volt_info.html', {})


def bom_manage(request):
    return render(request, 'BOM/BOM_manage.html', {})


def bom_manage_hanvit(request):
    return render(request, 'BOM/BOM_manage_hanvit.html', {})


def amount_inform(request):
    return render(request, "amount_inform/amount.html", {})


def bom_lookup(request):
    return render(request, 'BOM/BOM_lookup.html', {})


def bom_lookup_hanvit(request):
    return render(request, 'BOM/BOM_lookup_hanvit.html', {})


def bom_lookup_popup(request):
    return render(request, 'BOM/BOM_lookup_popup.html', {})


def bom_lookup_popup_hanvit(request):
    return render(request, 'BOM/BOM_lookup_popup_hanvit.html', {})


def bom_lookup_log_popup(request):
    return render(request, 'BOM/BOM_lookup_log_popup.html', {})


def bom_inventory_status(request):
    return render(request, 'BOM/BOM_inventory.html', {})


def bom_add(request):
    return render(request, 'BOM/BOM_add.html', {})


def material_input(request):
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 19, 'M')
    context = {}
    context['cu'] = customer_fm(request.GET, request.COOKIES['enterprise_name'])
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    context['column'] = column
    return render(request, 'material/material_input.html', context)


def material_outorder(request):
    return render(request, 'material/material_outorder.html', {})


def material_outout(request):
    return render(request, 'material/material_outout.html', {})


def material_output(request):
    context = {}
    # context['out'] = item_form(request.GET, request.COOKIES['enterprise_name'])
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 20, 'M')
    context['column'] = column
    return render(request, 'material/material_output.html', context)


def material_import(request):
    context = {}
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 21, 'M')
    context['column'] = column
    return render(request, 'material/material_import.html', context)


def material_status(request):
    context = {}
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 22, 'M')
    context['column'] = column
    return render(request, 'material/material_status.html', context)


def material_status_tv(request):
    return render(request, 'material/material_status_tv.html', {})


def material_status_tv_pop(request):
    context = {}
    context['searchForm'] = Search_Code(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'material/material_status_tv_pop.html', context)


# def material_adjust(request):
#     return render(request, 'material/material_adjust.html', {})
#


def material_adjust(request):
    context = {}
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 23, 'M')
    context['column'] = column
    return render(request, 'material/material_adjust_add.html', context)


def material_adjust_status(request):
    return render(request, 'material/material_adjust_status.html', {})


# QR Read 시 사용
def material_qr_view(request):
    return render(request, 'material/material_qr.html', {})


def material_qr_popup(request):
    return render(request, 'material/material_qr_popup.html', {})


def process_manage(request):
    return render(request, 'process/process_manage.html', {})


def process_detail_manage(request):
    return render(request, 'process/process_detail_manage.html', {})


def result_detail_manage(request):
    return render(request, 'result/detail_manage.html', {})


def result_progress_manage(request):
    return render(request, 'result/progress_manage.html', {})


def process_progress_manage(request):
    return render(request, 'process/process_progress_manage.html', {})


def process_progress_manage_tablet(request):
    return render(request, 'process/process_progress_manage_tablet.html', {})


def process_progress_manage_form(request):
    return render(request, 'process/process_form.html', {})


def process_progress_lookup(request):
    return render(request, 'process/process_progress_lookup.html', {})


def process_progress_lookup_tv(request):
    return render(request, 'process/process_progress_lookup_tv.html', {})


def subprocess_fault_manage(request):
    return render(request, 'process/subprocess_fault_manage.html', {})


def subprocess_fault_lookup(request):
    return render(request, 'process/subprocess_fault_lookup.html', {})


def subprocess_fault_graph(request):
    return render(request, 'process/subprocess_fault_graph.html', {})


def rental_item(request):
    return render(request, 'rental/rental_item.html', {})


def rental_manage(request):
    return render(request, 'rental/rental_manage.html', {})


def rental_status(request):
    return render(request, 'rental/rental_status.html', {})


def monitoring_manage(request):
    return render(request, 'monitoring/monitoring_manage.html', {})


def production_manage(request):
    return render(request, 'productionLine/product_manage.html')


def monitoring_pc(request):
    return render(request, 'monitoring/monitoring_pc.html', {})


def monitoring_tv(request):
    return render(request, 'monitoring/monitoring_tv.html', {})


def monitoring_h2_manage(request):
    return render(request, 'monitoring/monitoring_h2_manage.html', {})


def monitoring_h2_pc(request):
    return render(request, 'monitoring/monitoring_h2_pc.html', {})


def monitoring_h2_tv(request):
    return render(request, 'monitoring/monitoring_h2_tv.html', {})


def monitoring_h2_led(request):
    return render(request, 'monitoring/monitoring_h2_led.html', {})


def temp_volt_monitoring_manage(request):
    return render(request, 'temp_volt_monitoring/temp_volt_monitoring_manage.html', {})


def temp_volt_monitoring_status(request):
    return render(request, 'temp_volt_monitoring/temp_volt_monitoring_status.html', {})


def temp_volt_monitoring_lookup(request):
    return render(request, 'temp_volt_monitoring/temp_volt_monitoring_lookup.html', {})


def order_manage(request):
    context = {}
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 37, 'M')
    subcolumn = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 37, 'S')

    context['column'] = column

    context['subcolumn'] = subcolumn
    return render(request, 'order/order_manage.html', context)


def order_input(request):
    context = {}
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 38, 'M')
    subcolumn = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 38, 'S')

    context['column'] = column

    context['subcolumn'] = subcolumn
    return render(request, 'order/order_input.html', context)


def order_status(request):
    context = {}
    context['it'] = item_fm(request.GET, request.COOKIES['enterprise_name'])
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 39, 'M')
    subcolumn = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 39, 'S')

    context['column'] = column

    context['subcolumn'] = subcolumn
    return render(request, 'order/order_status.html', context)


def order_sales(request):
    context = {}
    context['out'] = orderpurchase_form(request.GET, request.COOKIES['enterprise_name'])
    return render(request, "OrderPurchase/order_sales.html", context)


def order_purchase(request):
    context = {}
    context['in'] = orderpurchase_form(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'OrderPurchase/order_purchase.html', context)


def outsourcing_manage(request):
    return render(request, 'outsourcing/outsourcing_manage.html', {})


def outsourcing_input(request):
    return render(request, 'outsourcing/outsourcing_input.html', {})


def outsourcing_status(request):
    return render(request, 'outsourcing/outsourcing_status.html', {})


def order_company(request):
    context = {}
    context['oc'] = order_company_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'basic_information/order_company.html', context)


def my_info(request):
    context = {}
    column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 60, 'M')
    context['column'] = column
    return render(request, 'basic_information/my_info.html', context)


def warehouse_input(request):
    return render(request, 'warehouse/input.html', {})


def warehouse_output(request):
    return render(request, 'warehouse/output.html', {})


def warehouse_import(request):
    return render(request, 'warehouse/import.html', {})


def warehouse_status(request):
    return render(request, 'warehouse/status.html', {})


def warehouse_adjust(request):
    return render(request, 'warehouse/adjust.html', {})


def warehouse_log(request):
    return render(request, 'warehouse/log.html', {})


def haccp_manage(request):
    return render(request, 'haccp/in_haccp.html', {})


#  hjlim new-module
def ordering_input(request):
    context = {}
    context['odr'] = ordering_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'ordering/ordering_input.html', context)


def ordering_status(request):
    context = {}
    context['odr'] = ordering_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'ordering/ordering_status.html', context)


def ordering_stats(request):
    return render(request, 'ordering/ordering_stats.html', {})


def estimate_input(request):
    context = {}
    context['es'] = estimate_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'estimate/estimate_input.html', context)


def estimate_status(request):
    context = {}
    context['es'] = estimate_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'estimate/estimate_status.html', context)


# 얜 뭐지???
# def estimate_stats(request):
#     return render(request, 'estimate/estimate_stats.html', {})


def request_input(request):
    context = {}
    context['re'] = request_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'request/request_input.html', context)


def request_status(request):
    context = {}
    context['re'] = request_fm(request.GET, request.COOKIES['enterprise_name'])
    return render(request, 'request/request_status.html', context)


def ordering_export_input(request):  # 출하등록
    return render(request, 'ordering_ex/ordering_export_input.html', {})


def ordering_export_status(request):  # 출하내역조회
    return render(request, 'ordering_ex/ordering_export_status.html', {})


def cost_by_product(request):  # 제품별원가
    return render(request, 'cost/cost_by_product.html', {})


def cost_by_export(request):  # 주문대비원가
    return render(request, 'cost/cost_by_export.html', {})


def UnbalanceAdd(request):  # UNBALANCE 등록
    return render(request, 'quality/UnbalanceAdd.html', {})


def UnbalanceSearch(request):  # UNBALANCE 조회
    return render(request, 'quality/UnbalanceSearch.html', {})


def RotatorAdd(request):  # 회전자검사 성적등록
    return render(request, 'quality/RotatorAdd.html', {})


def RotatorSearch(request):  # 회전자검사 성적조회
    return render(request, 'quality/RotatorSearch.html', {})


def StatorAdd(request):  # 고정자검사 성적등록
    return render(request, 'quality/StatorAdd.html', {})


def StatorSearch(request):  # 고정자검사 성적조회
    return render(request, 'quality/StatorSearch.html', {})


def Health(request):  # 건강생활연구소
    return render(request, 'basic_information/health.html', {})


def Graph(request):  # 건강생활연구소
    return render(request, 'basic_information/graph.html', {})


def Alert(request):  # 건강생활연구소
    return render(request, 'basic_information/alert.html', {})


def Rest_kpi(request):  # 건강생활연구소
    return render(request, 'basic_information/rest_kpi.html', {})


def Menumaster(request):
    allMenu = MenuMaster.objects.filter(type='L').order_by('id')
    useMenu = MenuMaster.objects.filter(menuauth__enterprise=request.COOKIES.get("enterprise_id")
                                        , menuauth__user=request.COOKIES.get('user_id')
                                        , menuauth__use_flag='Y'
                                        , menuauth__del_flag='N'
                                        , menuauth__parent_id=0
                                        ).annotate(alias=Coalesce('menuauth__alias', F('name'))
                                                   ).values('id', 'code', 'alias', 'path', 'type', 'comment', 'i_class'
                                                            , 'created_by_id', 'created_at', 'updated_by_id',
                                                            'updated_at'
                                                            , 'del_flag').order_by('menuauth__order')

    enter = enterprise_fm(request.GET, request.COOKIES['enterprise_name'])
    context = {}
    context['allMenu'] = allMenu
    context['useMenu'] = useMenu
    context['ep'] = enter
    return render(request, 'basic_information/menumaster.html', context)


def ColumnConfig(request):
    enter = enterprise_fm(request.GET, request.COOKIES)
    usrid = request.COOKIES['user_id']
    column = getColumnList(request.COOKIES['enterprise_id'], usrid, 112, 'M')

    context = {}
    context['ep'] = enter
    context['column'] = column
    return render(request, 'basic_information/columnconfig.html', context)


def getColumnList(ep_id, user_id, menu, tier):
    if tier is None:
        tier = "M"

    qs = ColumnMaster.objects.filter(Q(enterprise_id=1) &
                                     Q(user_id=1) &
                                     Q(menu=menu) &
                                     Q(tier=tier) &
                                     # Q(visual_flag=True) &
                                     Q(use_flag=True)
                                     ).select_related('menu').annotate(code=F('menu__code')).order_by('position')

    return qs


def project_view(request):
    context = {}
    return render(request, 'project/project_view.html', context)


def kpi_pop(request):
    from datetime import date
    yesterday = date.today()
    _year = yesterday.strftime('%Y')
    _month = yesterday.strftime('%m')

    text_bom_number = 'B123456789'
    p_value = 0  # 생산량 향상
    q_value = 0  # 완제품 불량률
    c_value = 0  # 개당 작업공수
    d_value = 0  # 출하납기 준수율

    q_amount = 0
    fault = 0
    d_amount = 0

    enterprise_name = '할랄푸드코리아'

    try:
        # 월별
        # 생산량 향상 Start
        qs_pro = Process.objects.filter(enterprise__name=enterprise_name, bom_master__bom_number=text_bom_number,
                                        complete=True, updated_at__year=_year, updated_at__month=_month)

        if qs_pro:
            amount = qs_pro.aggregate(sum=Coalesce(Sum('amount'), 0))
            p_value = amount['sum']  # 생산량 향상

            # for row in qs:
            #     print(row)

        # 생산량 향상 End

        # 완제품 불량률 Start
        q_amount = p_value
        qs_reItem = ItemRein.objects.filter(enterprise__name=enterprise_name,
                                            item__bom_division__bom_number=text_bom_number,
                                            updated_at__year=_year, updated_at__month=_month)

        if qs_reItem:
            qs_faulty = qs_reItem.aggregate(sum=Coalesce(Sum('out_faulty_amount'), 0))
            fault = qs_faulty['sum']

        if q_amount == 0:
            q_value = 0
        elif fault > q_amount:
            q_value = 0
        else:
            q_value = (fault / q_amount) * 100

        # 완제품 불량률 End

        # 개당 작업공수 Start
        qs_pro1 = Process.objects.filter(enterprise__name=enterprise_name,
                                         complete=True, updated_at__year=_year, updated_at__month=_month)

        if qs_pro1:
            qs = qs_pro1.values('code', 'fr_date', 'to_date', 'amount')

            if qs:
                qs_time = qs.annotate(produce_time=Case(
                    When(fr_date=F('to_date'),
                         then=1
                         ),
                    When(fr_date__lte=F('to_date'),
                         then=((Avg(F('to_date') - F('fr_date'))) / (1000 * 1000 * 60 * 60 * 24)) + 1
                         ),
                    output_field=IntegerField(),
                    default=0))

                qs_minute = qs_time.annotate(produce_day=F('produce_time'), produce_minute=(F('produce_time') * 8 * 60))
                # for row in qs_minute:
                #     print(row)

                qs_avg = qs_minute.aggregate(sum_minute=Sum(F('produce_minute')), sum_amount=Sum(F('amount')))
                sum_minute = qs_avg['sum_minute']
                sum_amount = qs_avg['sum_amount']

                if sum_amount == 0:
                    c_value = 0
                else:
                    c_value = round(sum_minute / sum_amount, 1)
        # 개당 작업공수 End

        # 출하납기 준수율 Start
        qs_ordering_list = Ordering.objects.filter(enterprise__name=enterprise_name,
                                                   export_status='출하완료',
                                                   updated_at__year=_year, updated_at__month=_month)

        if qs_ordering_list:
            d_amount = qs_ordering_list.count()
            yes_sum = 0

            for row in qs_ordering_list:
                row_id = row.id
                due_date = row.due_date
                yes = 1

                exItems = OrderingExItems.objects.filter(ordering_id=row_id, out=1)
                if exItems:
                    for exItem in exItems:
                        export_date = exItem.export_date

                        if export_date <= due_date:
                            pass
                        else:
                            yes = 0  # 출하 비준수

                if yes == 1:
                    yes_sum += 1

        if d_amount == 0:
            d_value = 0
        else:
            d_value = (yes_sum / d_amount) * 100
        # 출하납기 준수율 End

        result = {
            "P": round(p_value, 2), "Q": round(q_value, 2), "C": round(c_value, 2), "D": round(d_value, 2)}

    except Exception as ex:
        print("kpi_pop Exception")
        print(ex)

    return render(request, 'KPI/kpi_pop.html', result)
