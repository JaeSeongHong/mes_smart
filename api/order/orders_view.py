from django.db import transaction
from django.db.models import Sum, Value, FloatField, Count, Avg, F, ExpressionWrapper, DecimalField, Max
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import re

from KPI.kpi_views import kpi_log
from api.models import Orders, OrdersItems, ItemIn, OrdersInItems, ItemMaster
from api.permission import MesPermission
from api.serializers import OrdersSerializer, OrdersItemsSerializer, generate_code, OrdersInItemsSerializer
from api.temp_volt_monitoring.send_mail import send_gmail, send_gmail_pdf
from api.pagination import PostPageNumberPagination5
from django.views import View
from datetime import datetime


class OrdersitemsOnlyRead(View):
    def get(self, request, *args, **kwargs):
        orders_id = self.request.GET.get('orders_id')

        qs = OrdersItems.objects.filter(enterprise_id=self.request.COOKIES['enterprise_id'],
                                        orders_id=orders_id).annotate(
            in_quantity=Coalesce(Sum('ordersinitems__in_quantity'), 0),
            in_faulty=Coalesce(Sum('ordersinitems__in_faulty'), 0),
            code=F('item__code'),
            name=F('item__name'),
            detail=F('item__detail'),
            shape=F('item__shape')
        ).values(
            'id', 'item_id', 'quantity', 'in_quantity', 'in_faulty', 'code', 'name', 'detail', 'shape'
        ).order_by('id')
        list_qs = list(qs)
        result = get_ordersItems_result(list_qs)
        context = {}
        context['results'] = result

        return JsonResponse(context, safe=False)


class OrdersInputRead(View):
    def get(self, request, *args, **kwargs):
        qs = Orders.objects.filter(finish_chk=True, enterprise_id=self.request.COOKIES['enterprise_id']).annotate(
            customer_name=F('customer__name'),
            item_code=F('ordersitems__item__code'),
            item_name=F('ordersitems__item__name'),
            item_detail=F('ordersitems__item__detail'),
            quantity=F('ordersitems__quantity'),
            in_items_status=F('ordersitems__in_status'),
            orders_items_id=F('ordersitems__id'),
        ).values(
            'id', 'po_no', 'customer_name', 'customer_id', 'in_status', 'created_at', 'in_items_status', 'item_code',
            'item_name', 'item_detail', 'quantity', 'orders_items_id'
        ).order_by('-id')

        # qs = qs.filter(in_status__in=['U', 'P'])

        in_status = self.request.GET.get('in_status')

        if in_status is not None:
            qs = qs.filter(in_status=in_status)

        customer = self.request.GET.get('customer_id')

        if customer is not None:
            customer = customer.strip()
            qs = qs.filter(customer_id=customer)

        fr_date = self.request.GET.get('make_from')
        to_date = self.request.GET.get('make_to')

        if to_date is not None:
            # 날짜 문자열을 datetime 객체로 변환
            fr_date = datetime.strptime(fr_date, '%Y-%m-%d')
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
            to_date = to_date.replace(hour=23, minute=59)
            qs = qs.filter(created_at__range=[fr_date, to_date])

        list_qs = list(qs)
        result = get_ordersInput_result(list_qs)
        context = {}
        context['results'] = result

        return JsonResponse(context, safe=False)


class OrdersOnlyRead(View):
    def get(self, request, *args, **kwargs):
        qs = Orders.objects.filter(enterprise_id=self.request.COOKIES['enterprise_id']).annotate(
            item_supply_total=(F('ordersitems__quantity') * F('ordersitems__item_price')
                               + F('ordersitems__quantity') * F('ordersitems__item_price') * 0.1)
        ).values(
            'id', 'customer_id', 'po_no', 'item_supply_total', 'finish_chk', 'finish_date', 'created_at', 'updated_at',
            'etc', 'customer__name', 'created_by__username', 'updated_by', 'pay_option', 'due_date', 'guarantee_date',
            'deliver_place', 'note', 'in_status'
        ).annotate(
            item_supply_total_sum=Sum('item_supply_total')
        )

        finish_chk = self.request.GET.get('finish_chk')

        if finish_chk is not None:
            # 'finish_chk' 매개변수가 존재하는 경우
            finish_chk = finish_chk.strip()
            qs = qs.filter(finish_chk=finish_chk)

        customer = self.request.GET.get('customer_id')

        if customer is not None:
            customer = customer.strip()
            qs = qs.filter(customer_id=customer)

        fr_date = self.request.GET.get('make_from')
        to_date = self.request.GET.get('make_to')

        if to_date is not None:
            # 날짜 문자열을 datetime 객체로 변환
            fr_date = datetime.strptime(fr_date, '%Y-%m-%d')
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
            to_date = to_date.replace(hour=23, minute=59)
            qs = qs.filter(created_at__range=[fr_date, to_date])

        in_status = self.request.GET.get('in_status')

        if in_status is not None:
            qs = qs.filter(finish_chk=True)

        list_qs = list(qs)

        result = get_results(list_qs)
        context = {}
        context['results'] = result

        return JsonResponse(context, safe=False)


class OrdersViewSet(viewsets.ModelViewSet):
    class OrdersFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Orders
            fields = ['id']

    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrdersFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersViewSet", "get_queryset", False)

        qs = Orders.objects.filter(enterprise=self.request.user.enterprise)

        return qs

    @transaction.atomic
    def sendmail_to_company(self, request, *args, **kwargs):

        mail_info = dict(gmail_user='greenbi5693@gmail.com', gmail_password='grqsbumhzdmrjeav',
                         sent_from='greenbi5693@gmail.com', send_to='greenbi5693@naver.com',
                         subject="발주서", body="발주서 입니다.")

        send_gmail(mail_info, None)

        return Response({}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def sendmail_to_company_pdf(self, request, *args, **kwargs):
        email_form = re.compile('[a-zA-Z0-9._-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        phone_form = re.compile('\d{2,3}-\d{3,4}-\d{4}')
        customer_email = email_form.search(request.data['customer_email'])
        enter_email = email_form.search(request.data['enter_email'])
        enter_fax = ""
        if phone_form.search(request.data['enter_fax']):
            enter_fax = phone_form.search(request.data['enter_fax']).group()
        enter_call = ""
        if phone_form.search(request.data["enter_call"]):
            enter_call = phone_form.search(request.data['enter_call']).group()
        logo_img = request.data['logo_img']

        if enter_email and customer_email:
            enter_email = enter_email.group()
        else:
            enter_email = ""
            customer_email = ""

        if customer_email:
            customer_email = customer_email.group()
            print(customer_email)
            mail_info = dict(gmail_user='seoulsoftinfo@gmail.com', gmail_password='zwsixkqojsisiqpc',
                             sent_from=enter_email, send_to=customer_email,
                             Cc='yubin.shin@seoul-soft.com', Bcc=enter_email,
                             subject=request.data['enterprise_name'] + " - 발행한 발주서입니다.",
                             enterprise=request.data['enterprise_name'],
                             enter_email=enter_email, enter_fax=enter_fax, enter_call=enter_call, logo_img=logo_img,
                             type="발주서")

            # 'hjlim@seoul-soft.com, greenbi5693@naver.com, ubin1101@gmail.com, ubin1101@naver.com'

            file = request.FILES['file']
            try:
                send_gmail_pdf(mail_info, file)
                return Response('success', status=status.HTTP_201_CREATED)

            except:
                raise ValidationError('관리자에게 문의하세요.')
        else:
            raise ValidationError('거래처 이메일을 확인해 주시기 바랍니다.')

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersViewSet", "create", False)

        cu_id = request.data.get('customer')
        item_id = request.data.get('item')
        orderItemsExgist = OrdersItems.objects.none()  # 비어있는 쿼리셋으로 초기화
        orderExgist = Orders.objects.filter(enterprise=self.request.user.enterprise, customer=cu_id,
                                            finish_chk=0).order_by('-id')
        if orderExgist.exists() is False:
            res = super().create(request, request, *args, **kwargs)
            res_id = res.data['id']
        else:
            res = None
            res_id = orderExgist.first().id
            orderItemsExgist = OrdersItems.objects.filter(enterprise=self.request.user.enterprise, orders_id=res_id,
                                                          item_id=item_id)

        quantity = request.data.get('quantity', 0)
        price = request.data.get('item_price', 0)
        user = request.user

        if (orderItemsExgist.exists()):
            row = orderItemsExgist.first()
            current_quantity = row.quantity + float(quantity)
            old_price = row.item_price * row.quantity
            new_price = float(quantity) * float(price)
            cal_price = (old_price + new_price) / current_quantity
            row.quantity = current_quantity
            row.item_price = cal_price
            row.save()

        else:
            # 발주항목 등록
            row = OrdersItems.objects.create(orders_id=res_id,
                                             item_id=item_id,

                                             quantity=(0 if (quantity == '') else quantity),
                                             item_price=(0 if (price == '') else price),

                                             created_by=user,
                                             updated_by=user,
                                             created_at=user,
                                             updated_at=user,
                                             enterprise=request.user.enterprise
                                             )

        return Response({'message': '주문 및 발주항목이 성공적으로 생성되었습니다.', 'data': {'orders_id': row.orders_id}},
                        status=status.HTTP_201_CREATED)
        # return res_id

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersViewSet", "partial_update", False)
        res = super().partial_update(request, request, *args, **kwargs)

        if 'send_try' in self.request.data:
            row = Orders.objects.get(pk=kwargs.get('pk'))

            if row:
                from datetime import datetime
                row.send_date = datetime.today().strftime("%Y-%m-%d")
                row.save()

                res.data['send_date'] = datetime.today().strftime("%Y-%m-%d")

        return res

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)


class OrdersItemsViewSet(viewsets.ModelViewSet):
    class OrdersItemsFilter(FilterSet):
        class Meta:
            model = OrdersItems
            fields = ['id', 'orders', 'orders_id']

    queryset = OrdersItems.objects.all()
    serializer_class = OrdersItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrdersItemsFilter
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersItemsViewSet", "get_queryset", False)
        orders_id = self.request.query_params['orders_id']
        qs = OrdersItems.objects.filter(enterprise=self.request.user.enterprise, orders_id=orders_id).order_by('-id')

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersItemsViewSet", "create", False)

        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersItemsViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersItemsViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)


class OrdersInItemsViewSet(viewsets.ModelViewSet):
    class OrdersInItemsFilter(FilterSet):
        class Meta:
            model = OrdersInItems
            fields = ['id', 'orders_id']

    queryset = OrdersInItems.objects.all()
    serializer_class = OrdersInItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrdersInItemsFilter
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "get_queryset", False)

        if 'ordersitem_id' in self.request.query_params:
            ordersitem_id = self.request.query_params['ordersitem_id']
            qs = OrdersInItems.objects.filter(enterprise=self.request.user.enterprise,
                                              orders_item_id=ordersitem_id).order_by('-id')
        else:
            qs = OrdersInItems.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "create", False)

        ordersItem_id = request.data['orders_item_id']
        location = request.data['location_id']

        in_date = request.data['in_date']  # 입고일자

        if in_date == '':
            in_date = datetime.today().strftime("%Y-%m-%d")

        in_quantity = request.data['in_quantity']
        in_faulty = request.data['in_faulty']

        user = request.user
        num = generate_code('I', ItemIn, 'num', user)
        ordersItem = OrdersItems.objects.get(id=ordersItem_id)

        if ordersItem:
            item_id = ordersItem.item_id
            item_price = ordersItem.item_price
            orders_id = ordersItem.orders_id
            po_quan = ordersItem.quantity
        else:
            raise ValidationError('데이터가 정확하지 않습니다.')

        item = ItemMaster.objects.get(pk=item_id)
        item.stock = item.stock + float(in_quantity)
        item.save()

        current_amount = item.stock
        orders = Orders.objects.get(pk=orders_id)
        customer = orders.customer

        # 재고입고 진행
        item_in = ItemIn.objects.create(
            num=num,  # 입고번호
            item_id=item_id,  # 품번
            in_at=in_date,  # 입고일자
            current_amount=float(current_amount),  # 현재재고
            receive_amount=float(in_quantity),  # 입고할 수량
            in_faulty_amount=float(in_faulty),  # 입고할 불량수량
            in_price=float(item_price),  # 입고단가
            customer=customer,  # 거래처
            location_id=location,
            created_by=user,
            updated_by=user,
            created_at=user,
            updated_at=user,
            enterprise=request.user.enterprise
        )

        # 입고내용 등록
        OrdersInItems.objects.create(ins=True,  # 입고
                                     orders_id=orders_id,
                                     orders_item_id=ordersItem_id,
                                     num=num,
                                     item_id=item_id,
                                     item_price=float(item_price),
                                     quantity=float(po_quan),  # 발주수량
                                     in_quantity=float(in_quantity),
                                     in_faulty=float(in_faulty),

                                     in_date=in_date,
                                     location_id=location,

                                     item_in_id=item_in.id,

                                     created_by=user,
                                     updated_by=user,
                                     created_at=user,
                                     updated_at=user,
                                     enterprise=request.user.enterprise
                                     )

        # 입고상태 변경 : Orders
        ordersPoquan = OrdersItems.objects.filter(
            orders_id=orders_id,
            enterprise=request.user.enterprise
        ).aggregate(orderssumpoquan=Sum('quantity'))['orderssumpoquan']

        poObj = OrdersInItems.objects.filter(
            orders_id=orders_id,
            enterprise=request.user.enterprise
        ).aggregate(
            inquan=Sum('in_quantity'),
            infault=Sum('in_faulty')
        )
        realQuan = poObj['inquan'] + poObj['infault']

        if realQuan == 0:
            orders.in_status = 'U'
        elif ordersPoquan <= realQuan:
            orders.in_status = 'F'
        else:
            orders.in_status = 'P'

        orders.save()

        # 입고상태 변경 : OrdersItems
        poOdersItem = OrdersInItems.objects.filter(
            orders_id=orders_id,
            orders_item_id=ordersItem_id,
            enterprise=request.user.enterprise
        ).aggregate(
            initemquan=Sum('in_quantity'),
            initemfault=Sum('in_faulty')
        )

        realItemQuan = poOdersItem['initemquan'] + poOdersItem['initemfault']

        if realItemQuan == 0:
            ordersItem.in_status = 'U'
        elif po_quan <= realItemQuan:
            ordersItem.in_status = 'F'
        else:
            ordersItem.in_status = 'P'

        ordersItem.save()

        context = {}
        return Response(context)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "partial_update",
                False)
        return super().partial_update(request, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrdersInItemsViewSet", "destroy", False)

        dataLength = int(request.data['dataLength'])
        if kwargs['pk'] == '0':  # 출하등록 취소인 경우
            for nm in range(0, dataLength):
                orders_id = request.data['itemData[' + str(nm) + '][orders]']  # 발주서 ID
                orders_item_id = request.data['itemData[' + str(nm) + '][orders_item]']  # 발주항목 ID
                item_id = request.data['itemData[' + str(nm) + '][item]']  # 품번 ID
                item_detail = request.data['itemData[' + str(nm) + '][item_detail]']  # 품명상세
                item_price = request.data['itemData[' + str(nm) + '][item_price]']  # 단가
                if item_price == '': item_price = 0

                quantity = request.data['itemData[' + str(nm) + '][quantity]']  # 발주수량
                if quantity == '': quantity = 0

                # supply_price = request.data['itemData[' + str(nm) + '][supply_price]']  # 공급가
                # if supply_price == '': supply_price = 0
                #
                # surtax = request.data['itemData[' + str(nm) + '][surtax]']  # 부가세
                # if surtax == '': surtax = 0
                #
                # item_supply_total = request.data['itemData[' + str(nm) + '][item_supply_total]']  # 합계
                # if item_supply_total == '': item_supply_total = 0

                in_quantity = request.data['itemData[' + str(nm) + '][in_quantity]']  # 입고수량
                if in_quantity == '': in_quantity = 0

                in_faulty = request.data['itemData[' + str(nm) + '][in_faulty]']  # 불량수량
                if in_faulty == '': in_faulty = 0

                orders_in_item_id = request.data['itemData[' + str(nm) + '][orders_in_item]']  # 입고항목 ID
                item_num = request.data['itemData[' + str(nm) + '][item_num]']  # 입고번호

                user = request.user
                num = generate_code('O', ItemIn, 'num', user)

                # 입고등록 취소
                ins = OrdersInItems.objects.get(id=orders_in_item_id)
                if ins:
                    ins.delete()

                # 재고입고 취소
                qs = ItemIn.objects.filter(id=ins.item_in_id)
                if qs:
                    item_in_row = qs.get(id=ins.item_in_id)
                    if item_in_row:
                        item_in_row.delete()

                # 발주항목 남은 재고량 재계산
                orders_item = OrdersItems.objects.get(id=float(orders_item_id))

                in_ed_quantity = orders_item.in_ed_quantity
                to_in_quantity = in_ed_quantity - float(in_quantity)
                orders_item.in_ed_quantity = to_in_quantity

                in_ed_faulty = orders_item.in_ed_faulty
                to_in_ed_faulty = in_ed_faulty - float(in_faulty)
                orders_item.in_ed_faulty = to_in_ed_faulty

                # 품목마스터 현재고 재계산
                item = ItemMaster.objects.get(pk=item_id)
                item.stock = item.stock - float(in_quantity)
                item.save()

                # 미입고 모두 삭제
                qs = OrdersInItems.objects.filter(enterprise=self.request.user.enterprise).all()
                qs = qs.filter(orders_item_id=orders_item_id, ins=False)
                for row in qs:
                    row.delete()

                # 미입고 계산
                a = orders_item.quantity  # 발주수량
                b = orders_item.in_ed_quantity  # 입고된 수량
                remain = (a - b) if ((a - b) >= 0) else 0  # 미입고 수량 (남은 수량)

                # if remain == 0:
                #     orders_item.in_status = True  # 입고완료
                # else:
                #     orders_item.in_status = False  # 미입고

                # 미입고 : 입고한 수량 = 0
                # 입고완료 : 발주 수량 <= 입고한 수량
                # 일부입고 : 그 이외는 일부입고

                if orders_item.in_ed_quantity == 0:
                    orders_item.in_status = ''

                elif orders_item.quantity <= orders_item.in_ed_quantity:
                    orders_item.in_status = '입고완료'

                else:
                    orders_item.in_status = '일부입고'

                orders_item.save()

                if remain > 0:  # 미입고 내용등록
                    OrdersInItems.objects.create(ins=False,  # 미입고
                                                 orders_id=orders_id,
                                                 orders_item_id=orders_item_id,
                                                 num=num,
                                                 item_id=item_id,
                                                 item_detail=item_detail,
                                                 item_price=float(item_price),

                                                 quantity=float(quantity),  # 발주수량
                                                 # supply_price=supply_price,  # 공급가
                                                 # surtax=surtax,  # 부가세
                                                 # item_supply_total=item_supply_total,  # 합계

                                                 in_quantity=float(remain),  # 입고수량 ? 미입고수량
                                                 in_date=None,  # 입고일자
                                                 item_created_at=None,  # 자재생산일자

                                                 created_by=user,
                                                 updated_by=user,
                                                 created_at=user,
                                                 updated_at=user,
                                                 enterprise=request.user.enterprise
                                                 )

            orders_status_check(self, orders_id)  # 입고현황 체크

            queryset = self.filter_queryset(self.get_queryset()).filter(enterprise=self.request.user.enterprise,
                                                                        orders_id=orders_id).order_by('item_id')
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return super().destroy(request, request, *args, **kwargs)


def orders_status_check(self, _id):
    OrdersItems_qs = OrdersItems.objects.filter(orders_id=_id)

    cnt = OrdersItems_qs.count()
    ok_in = 0  # 각 항목의 '입고완료' 된 수
    no_in = 0  # 각 항목의 '미입고' 된 수

    for row in OrdersItems_qs:

        # 방어 코드 : '미입고', '일부입고', '입고완료' 가 아닌 경우는 모두 미입고로 처리
        if row.in_status == '' or row.in_status == '입고완료' or row.in_status == '일부입고':
            pass
        else:
            row.in_status = ''
            row.save()

        if row.in_status == '입고완료':
            ok_in = ok_in + 1

        if row.in_status == '':
            no_in = no_in + 1

    orders = Orders.objects.get(id=_id)
    if orders:
        if ok_in == cnt:
            orders.in_status = '입고완료'

        elif no_in == cnt:
            orders.in_status = ''  # 미입고

        else:
            orders.in_status = '일부입고'

        orders.save()


class OrdersByListViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        ordersList = request.data.getlist('order_id_list[]')
        finish_chk = request.data['finish_chk']
        finish_date = request.data['finish_date']
        in_status = request.data['in_status']

        context = {}
        if ordersList:
            for ordersItem in ordersList:
                try:
                    order_instance = self.queryset.filter(id=ordersItem).first()
                    order_instance.finish_chk = finish_chk
                    order_instance.finish_date = finish_date
                    order_instance.in_status = in_status
                    order_instance.save()
                    # context['error'] = False
                except Exception as e:
                    context['error'] = str(e)
        else:
            raise ValidationError('선택된 발주서가 없습니다.')

        return JsonResponse(context)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        ordersList = request.data.getlist('order_id_list[]')

        context = {}
        if ordersList:
            for ordersItem in ordersList:
                try:
                    # 연관 테이블 삭제
                    OrdersItems.objects.filter(orders_id=ordersItem).delete()
                    # 발주서 삭제
                    Orders.objects.filter(id=ordersItem).delete()

                    context['msg'] = "삭제가 완료되었습니다."
                except Exception as e:
                    context['error'] = str(e)
                    context['msg'] = "발주서 삭제중에 문제가 발생했습니다."
        else:
            raise ValidationError('선택된 발주서가 없습니다.')

        return JsonResponse(context)


def get_results(qs):
    results = []
    appendResult = results.append

    for instance in qs:
        appendResult({
            'id': instance['id'],  # id
            'po_no': instance['po_no'],  # 발주번호
            'created_at': instance['created_at'].strftime('%Y-%m-%d'),  # 발주일자

            'customer_name': instance['customer__name'],  # 거래처명

            'etc': instance['etc'],  # 비고

            'pay_option': instance['pay_option'],  # 결제조건
            'due_date': instance['due_date'],  # 납기일
            'guarantee_date': instance['guarantee_date'],  # 품질보증기한
            'deliver_place': instance['deliver_place'],  # 남품장소
            'note': instance['note'],  # NOTE 내용고정

            'finish_chk': instance['finish_chk'],  # 마감여부
            'finish_date': instance['finish_date'].strftime('%Y-%m-%d') if instance['finish_date'] else "",
            'in_status': instance['in_status'],  # 입고현황
            'item_supply_total': instance['item_supply_total_sum'],  # 총합계
            'updated_at': instance['updated_at'].strftime('%Y-%m-%d'),  # 발주일자
            'username': instance['created_by__username']
        })

    return results


def get_ordersItems_result(qs):
    results = []
    appendResult = results.append
    for instance in qs:
        ordersItemId = instance['id']
        obj = OrdersInItems.objects.filter(orders_item_id=ordersItemId).order_by('-id').first()
        if obj is None:
            created_at = None
            location = None
        else:
            created_at = obj.created_at
            location = obj.location_id

        appendResult({
            'id': instance['id'],
            'code': instance['code'],
            'name': instance['name'],
            'detail': instance['detail'],
            'quantity': instance['quantity'],
            'created_at': created_at,
            'in_quantity': instance['in_quantity'],
            'in_faulty': instance['in_faulty'],
            'location': location,
            'shape': instance['shape']
        })
    return results


def get_ordersInput_result(qs):
    results = []
    appendResult = results.append
    for instance in qs:
        appendResult({
            'id': instance['orders_items_id'],
            'po_no': instance['po_no'] + " : " + instance['customer_name'],
            'customer_name': instance['customer_name'],
            'in_status': instance['in_status'],
            'in_items_status': instance['in_items_status'],
            'quantity': instance['quantity'],

            'code': instance['item_code'],
            'name': instance['item_name'],

            'detail': instance['item_detail']
        })
    return results
