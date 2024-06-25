import re
from django.db import transaction
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from KPI.kpi_views import kpi_log
from api.models import Ordering, OrderingItems, OrderingExItems, ItemMaster, ItemOut
from api.pagination import PostPageNumberPagination5
from api.permission import MesPermission
from api.serializers import OrderingSerializer, OrderingItemsSerializer, OrderingExItemsSerializer, generate_code, \
    get_Avg, OrderingPartSerializer, OrderingItemsPartSerializer
from api.temp_volt_monitoring.send_mail import send_gmail, send_gmail_pdf


class OrderingViewSet(viewsets.ModelViewSet):
    class OrderingFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Ordering
            fields = ['id']

    queryset = Ordering.objects.all()
    serializer_class = OrderingSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderingFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingViewSet", "get_queryset", False)
        qs = Ordering.objects.filter(enterprise=self.request.user.enterprise).all()

        if 'last' in self.request.query_params:
            last = self.request.query_params['last']
            if last == 'true':
                last_id = qs.last()

                if last_id == None:
                    qs = qs.none()
                else:
                    qs = qs.filter(id=last_id.id)

                return qs

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(created_at__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(created_at__lte=to_date)

        if 'fr_due_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_due_date']
            if fr_date != '':
                qs = qs.filter(due_date__gte=fr_date)

        if 'to_due_date' in self.request.query_params:
            to_date = self.request.query_params['to_due_date']
            if to_date != '':
                qs = qs.filter(due_date__lte=to_date)

        # 출하현황 계산
        for row in qs:
            Items = OrderingItems.objects.filter(ordering=row.id)

            export_none = True  # 미출하
            export_all = True  # 출하완료

            for item in Items:
                # 둘다 아니라면 미출하
                if item.export_now_quantity != 0:  # 출하수량이 모두 0 이면.. 미출하
                    export_none = False

                if item.quantity > item.export_now_quantity:  # 모두 출하 되었으면.. 출하완료
                    export_all = False

            if export_none == True:
                row.export_status = "미출하"

            elif export_all == True:
                row.export_status = "출하완료"

            else:
                row.export_status = "일부출하"

            row.save()

        if 'export_status' in self.request.query_params:
            export_status = self.request.query_params['export_status']
            if export_status != "":
                qs = qs.filter(export_status=export_status)

        qs = qs.order_by('-id')
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingViewSet", "create", False)
        res = super().create(request, request, *args, **kwargs)

        if 'itemCnt' in request.data:
            cnt = int(request.data['itemCnt'])
            user = request.user

            item_id = []
            item_detail = []
            item_unit = []

            item_quantity = []
            item_price = []
            supply_price = []

            surtax = []
            item_supply_total = []

            item_remarks = []
            item_file = []

            # 초기화
            for i in range(0, cnt):
                item_id.append(None)
                item_detail.append(None)
                item_unit.append(None)

                item_quantity.append(None)
                item_price.append(None)
                supply_price.append(None)
                surtax.append(None)
                item_supply_total.append(None)

                item_remarks.append(None)
                item_file.append(None)

            for i in range(0, cnt):
                item_id[i] = request.data['item_id[' + str(i) + ']']  # 품번 ID
                item_detail[i] = request.data['item_detail[' + str(i) + ']']  # 품명상세
                item_unit[i] = request.data['item_unit[' + str(i) + ']']  # 품명단위

                item_quantity[i] = request.data['item_quantity[' + str(i) + ']']  # 수량
                item_price[i] = request.data['item_price[' + str(i) + ']']  # 단가
                supply_price[i] = request.data['supply_price[' + str(i) + ']']  # 공급가
                surtax[i] = request.data['surtax[' + str(i) + ']']  # 부가세

                item_supply_total[i] = request.data['item_supply_total[' + str(i) + ']']  # 합계

                item_remarks[i] = request.data['item_remarks[' + str(i) + ']']  # 비고
                item_file[i] = request.data['file[' + str(i) + ']']

                # 주문항목 등록
                row = OrderingItems.objects.create(ordering_id=res.data['id'],
                                                   item_id=item_id[i],
                                                   item_detail=item_detail[i],
                                                   item_unit=item_unit[i],

                                                   quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                                                   item_price=(0 if (item_price[i] == '') else item_price[i]),
                                                   supply_price=(0 if (supply_price[i] == '') else supply_price[i]),

                                                   surtax=(0 if (surtax[i] == '') else surtax[i]),

                                                   item_supply_total=(
                                                       0 if (item_supply_total[i] == '') else item_supply_total[i]),

                                                   remarks=item_remarks[i],
                                                   file=item_file[i],

                                                   created_by=user,
                                                   updated_by=user,
                                                   created_at=user,
                                                   updated_at=user,
                                                   enterprise=request.user.enterprise
                                                   )

                # 미출하 등록
                num = generate_code('O', ItemOut, 'num', user)
                OrderingExItems.objects.create(out=False,  # 미출하
                                               ordering_id=res.data['id'],
                                               ordering_item_id=row.id,
                                               num=num,
                                               item_id=item_id[i],
                                               item_detail=item_detail[i],
                                               item_unit=item_unit[i],
                                               item_price=(0 if (item_price[i] == '') else item_price[i]),

                                               quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),  # 주문수량
                                               supply_price=(0 if (supply_price[i] == '') else supply_price[i]),  # 공급가

                                               surtax=(0 if (surtax[i] == '') else surtax[i]),  # 부가세
                                               item_supply_total=(
                                                   0 if (item_supply_total[i] == '') else item_supply_total[i]),  # 합계

                                               export_quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                                               # 출하수량 ? 미출하수량
                                               export_date=None,  # 출하일자
                                               export_address=None,  # 출하주소

                                               created_by=user,
                                               updated_by=user,
                                               created_at=user,
                                               updated_at=user,
                                               enterprise=request.user.enterprise
                                               )

        return res

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingViewSet", "partial_update", False)
        res = super().partial_update(request, request, *args, **kwargs)

        if 'itemCnt' in request.data:
            cnt = int(request.data['itemCnt'])
            user = request.user

            item_id = []
            item_detail = []
            item_unit = []

            item_quantity = []
            item_price = []
            supply_price = []

            surtax = []
            item_supply_total = []

            item_remarks = []
            item_file = []

            # 초기화
            for i in range(0, cnt):
                item_id.append(None)
                item_detail.append(None)
                item_unit.append(None)

                item_quantity.append(None)
                item_price.append(None)
                supply_price.append(None)
                surtax.append(None)
                item_supply_total.append(None)

                item_remarks.append(None)
                item_file.append(None)

            for i in range(0, cnt):
                item_id[i] = request.data['item_id[' + str(i) + ']']  # 품번 ID
                item_detail[i] = request.data['item_detail[' + str(i) + ']']  # 품명상세
                item_unit[i] = request.data['item_unit[' + str(i) + ']']  # 품명단위

                item_quantity[i] = request.data['item_quantity[' + str(i) + ']']  # 수량
                item_price[i] = request.data['item_price[' + str(i) + ']']  # 단가
                supply_price[i] = request.data['supply_price[' + str(i) + ']']  # 공급가

                surtax[i] = request.data['surtax[' + str(i) + ']']  # 부가세
                item_supply_total[i] = request.data['item_supply_total[' + str(i) + ']']  # 합계

                item_remarks[i] = request.data['item_remarks[' + str(i) + ']']  # 비고
                item_file[i] = request.data['file[' + str(i) + ']']

                # 주문항목 등록
                row = OrderingItems.objects.create(ordering_id=res.data['id'],
                                                   item_id=item_id[i],
                                                   item_detail=item_detail[i],
                                                   item_unit=item_unit[i],

                                                   quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                                                   item_price=(0 if (item_price[i] == '') else item_price[i]),
                                                   supply_price=(0 if (supply_price[i] == '') else supply_price[i]),

                                                   surtax=(0 if (surtax[i] == '') else surtax[i]),
                                                   item_supply_total=(
                                                       0 if (item_supply_total[i] == '') else item_supply_total[i]),

                                                   remarks=item_remarks[i],
                                                   file=item_file[i],

                                                   created_by=user,
                                                   updated_by=user,
                                                   created_at=user,
                                                   updated_at=user,
                                                   enterprise=request.user.enterprise
                                                   )

                # 미출하 등록
                num = generate_code('O', ItemOut, 'num', user)
                OrderingExItems.objects.create(out=False,  # 미출하
                                               ordering_id=res.data['id'],
                                               ordering_item_id=row.id,
                                               num=num,
                                               item_id=item_id[i],
                                               item_detail=item_detail[i],
                                               item_unit=item_unit[i],
                                               item_price=(0 if (item_price[i] == '') else item_price[i]),

                                               quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),  # 주문수량
                                               supply_price=(0 if (supply_price[i] == '') else supply_price[i]),  # 공급가

                                               surtax=(0 if (surtax[i] == '') else surtax[i]),  # 부가세
                                               item_supply_total=(
                                                   0 if (item_supply_total[i] == '') else item_supply_total[i]),  # 합계

                                               export_quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                                               # 출하수량 ? 미출하수량
                                               export_date=None,  # 출하일자
                                               export_address=None,  # 출하주소

                                               created_by=user,
                                               updated_by=user,
                                               created_at=user,
                                               updated_at=user,
                                               enterprise=request.user.enterprise
                                               )

        return res

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)


class OrderingPartViewSet(viewsets.ModelViewSet):
    class OrderingFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Ordering
            fields = ['id']

    queryset = Ordering.objects.all()
    serializer_class = OrderingPartSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderingFilter
    pagination_class = None

    def get_queryset(self):
        qs = Ordering.objects.filter(enterprise=self.request.user.enterprise).all()

        if 'last' in self.request.query_params:
            last = self.request.query_params['last']
            if last == 'true':
                last_id = qs.last()

                if last_id == None:
                    qs = qs.none()
                else:
                    qs = qs.filter(id=last_id.id)

                return qs

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(created_at__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(created_at__lte=to_date)

        qs = qs.order_by('-id')
        return qs


class OrderingItemsViewSet(viewsets.ModelViewSet):
    queryset = OrderingItems.objects.all()
    serializer_class = OrderingItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'ordering_id']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingItemsViewSet", "get_queryset", False)
        qs = OrderingItems.objects.filter(enterprise=self.request.user.enterprise).all().order_by('item_id')

        for row in qs:
            item_id = row.item
            item = ItemMaster.objects.get(pk=item_id.id)

            # Todo: hjlim 추후 Serializer 로 옮기면 좋을 듯
            if item.bom_division:  # BOM 인경우
                price = get_Avg(item.bom_division)
                row.cost_price = price
                row.cost_total = price * row.quantity

            else:  # 원자재인경우
                row.cost_price = item.standard_price  # 원가 설정, 표준단가로 (마지막에 입고된 단가)
                row.cost_total = item.standard_price * row.quantity

            row.stock = item.stock  # 현재 재고
            row.save()

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingItemsViewSet", "create", False)
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingItemsViewSet", "partial_update",
                False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingItemsViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)


class OrderingItemsPartViewSet(viewsets.ModelViewSet):
    queryset = OrderingItems.objects.all()
    serializer_class = OrderingItemsPartSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'patch']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'ordering_id']
    pagination_class = None

    def get_queryset(self):
        qs = OrderingItems.objects.filter(enterprise=self.request.user.enterprise).all().order_by('item_id')
        return qs

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, request, *args, **kwargs)


class OrderingExItemsViewSet(viewsets.ModelViewSet):
    queryset = OrderingExItems.objects.all()
    serializer_class = OrderingExItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'ordering_id']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingExItemsViewSet", "get_queryset",
                False)
        return OrderingExItems.objects.filter(enterprise=self.request.user.enterprise).all().order_by('item_id')

    @transaction.atomic
    def sendmail_to_company(self, request, *args, **kwargs):

        mail_info = dict(gmail_user='greenbi5693@gmail.com', gmail_password='grqsbumhzdmrjeav',
                         sent_from='greenbi5693@gmail.com', send_to='greenbi5693@naver.com',
                         subject="거래명세서", body="거래명세서 입니다.")

        send_gmail(mail_info, None)

        return Response({}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def sendmail_to_company_pdf(self, request, *args, **kwargs):
        email_form = re.compile('[a-zA-Z0-9._-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        phone_form = re.compile('\d{2,3}-\d{3,4}-\d{4}')
        customer_email = email_form.search(request.data['customer_email'])
        enter_email = email_form.search(request.data['enter_email'])
        enter_fax = phone_form.search(request.data['enter_fax']).group()
        enter_call = phone_form.search(request.data['enter_call']).group()
        logo_img = request.data['logo_img']

        if enter_email:
            enter_email = enter_email.group()
        else:
            enter_email = ""

        if customer_email:
            customer_email = customer_email.group()
            mail_info = dict(gmail_user='seoulsoftinfo@gmail.com', gmail_password='zwsixkqojsisiqpc',
                             sent_from=enter_email, send_to=customer_email,
                             Cc='yubin.shin@seoul-soft.com', Bcc=enter_email,
                             subject=request.data['enterprise_name'] + " - 발행한 거래명세서입니다.",
                             enterprise=request.data['enterprise_name'],
                             enter_email=enter_email, enter_fax=enter_fax, enter_call=enter_call, logo_img=logo_img,
                             type="거래명세서")

            # 'hjlim@seoul-soft.com, greenbi5693@naver.com, ubin1101@gmail.com, ubin1101@naver.com'

            file = request.FILES['file']
            send_gmail_pdf(mail_info, file)

            return Response({}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError('거래처 이메일을 확인해 주시기 바랍니다.')

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingExItemsViewSet", "create", False)
        dataLength = int(request.data['dataLength'])

        for num in range(0, dataLength):
            ordering_id = request.data['itemData[' + str(num) + '][ordering]']  # 주문항목 ID
            ordering_item_id = request.data['itemData[' + str(num) + '][ordering_item]']  # 주문항목 ID
            item_id = request.data['itemData[' + str(num) + '][item]']  # 품번 ID
            item_detail = request.data['itemData[' + str(num) + '][item_detail]']  # 품명상세
            item_unit = request.data['itemData[' + str(num) + '][item_unit]']  # 품명단위
            item_price = request.data['itemData[' + str(num) + '][item_price]']  # 단가
            if item_price == '': item_price = 0

            quantity = request.data['itemData[' + str(num) + '][quantity]']  # 주문수량
            if quantity == '': quantity = 0

            supply_price = request.data['itemData[' + str(num) + '][supply_price]']  # 공급가
            if supply_price == '': supply_price = 0

            surtax = request.data['itemData[' + str(num) + '][surtax]']  # 부가세
            if surtax == '': surtax = 0

            item_supply_total = request.data['itemData[' + str(num) + '][item_supply_total]']  # 합계
            if item_supply_total == '': item_supply_total = 0

            export_quantity = request.data['itemData[' + str(num) + '][export_quantity]']  # 출하수량
            if export_quantity == '': export_quantity = 0

            export_date = request.data['itemData[' + str(num) + '][export_date]']  # 출하일자
            if export_date == '':
                from datetime import datetime
                export_date = datetime.today().strftime("%Y-%m-%d")

            export_address = request.data['itemData[' + str(num) + '][export_address]']  # 출하주소

            location = request.data['itemData[' + str(num) + '][location]']  # 출하수량
            user = request.user
            num = generate_code('O', ItemOut, 'num', user)

            # 미출하 모두 삭제
            qs = OrderingExItems.objects.filter(enterprise=self.request.user.enterprise).all()
            qs = qs.filter(ordering_item_id=ordering_item_id, out=False)
            for row in qs:
                row.delete()

            ordering = Ordering.objects.get(id=ordering_id)
            customer = ordering.code

            # 재고출고 진행
            current_amount = ItemMaster.objects.get(pk=item_id).stock

            item_out = ItemOut.objects.create(
                num=num,  # 출하번호
                item_id=item_id,  # 품번
                out_at=export_date,  # 출하일자
                current_amount=current_amount,  # 현재재고
                out_amount=export_quantity,  # 출고수량
                purpose="출하등록",  # 출고목적
                out_price=float(item_price),  # 출고단가
                purchase_from=customer,  # 거래처
                location_id=location,
                created_by=user,
                updated_by=user,
                created_at=user,
                updated_at=user,
                enterprise=request.user.enterprise
            )

            item = ItemMaster.objects.get(pk=item_id)
            item.stock = item.stock - float(export_quantity)
            item.save()

            # 출하내용 등록
            OrderingExItems.objects.create(out=True,  # 출하
                                           ordering_id=ordering_id,
                                           ordering_item_id=ordering_item_id,
                                           num=num,
                                           item_id=item_id,
                                           item_detail=item_detail,
                                           item_unit=item_unit,
                                           item_price=item_price,

                                           quantity=quantity,
                                           supply_price=supply_price,

                                           surtax=surtax,
                                           item_supply_total=item_supply_total,
                                           location_id = location,
                                           export_quantity=export_quantity,
                                           export_date=export_date,
                                           export_address=export_address,
                                           item_out_id=item_out.id,

                                           created_by=user,
                                           updated_by=user,
                                           created_at=user,
                                           updated_at=user,
                                           enterprise=request.user.enterprise
                                           )

            ordering_item = OrderingItems.objects.get(id=ordering_item_id)
            export_now_quantity = ordering_item.export_now_quantity
            to_export = export_now_quantity + float(export_quantity)
            ordering_item.location_id = None
            ordering_item.export_now_quantity = to_export
            ordering_item.export_quantity = 0
            ordering_item.save()

            # 미출하 등록
            a = ordering_item.quantity  # 주문수량
            b = ordering_item.export_now_quantity  # 출하된 수량
            remain = (a - b) if ((a - b) >= 0) else 0  # 미출하 수량 (남은 수량)

            if remain > 0:  # 미출하 내용등록
                OrderingExItems.objects.create(out=False,  # 미출하
                                               ordering_id=ordering_id,
                                               ordering_item_id=ordering_item_id,
                                               num=num,
                                               item_id=item_id,
                                               item_detail=item_detail,
                                               item_unit=item_unit,
                                               item_price=item_price,

                                               quantity=quantity,  # 주문수량
                                               supply_price=supply_price,  # 공급가
                                               surtax=surtax,  # 부가세
                                               item_supply_total=item_supply_total,  # 합계

                                               export_quantity=remain,  # 출하수량 ? 미출하수량
                                               export_date=None,  # 출하일자
                                               export_address=None,  # 출하주소
                                               location_id= location,
                                               created_by=user,
                                               updated_by=user,
                                               created_at=user,
                                               updated_at=user,
                                               enterprise=request.user.enterprise
                                               )

        queryset = self.filter_queryset(self.get_queryset()).filter(enterprise=self.request.user.enterprise,
                                                                    ordering_id=ordering_id).order_by('item_id')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingExItemsViewSet", "partial_update",
                False)
        return super().partial_update(request, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "OrderingExItemsViewSet", "destroy", False)
        dataLength = int(request.data['dataLength'])

        if kwargs['pk'] != '0':  # 출하등록 취소인 경우
            for num in range(0, dataLength):
                ordering_id = request.data['itemData[' + str(num) + '][ordering]']  # 주문서 ID
                ordering_item_id = request.data['itemData[' + str(num) + '][ordering_item]']  # 주문항목 ID
                item_id = request.data['itemData[' + str(num) + '][item]']  # 품번 ID
                item_detail = request.data['itemData[' + str(num) + '][item_detail]']  # 품명상세
                item_unit = request.data['itemData[' + str(num) + '][item_unit]']  # 품명단위
                item_price = request.data['itemData[' + str(num) + '][item_price]']  # 단가
                if item_price == '': item_price = 0

                quantity = request.data['itemData[' + str(num) + '][quantity]']  # 주문수량
                if quantity == '': quantity = 0

                supply_price = request.data['itemData[' + str(num) + '][supply_price]']  # 공급가
                if supply_price == '': supply_price = 0

                surtax = request.data['itemData[' + str(num) + '][surtax]']  # 부가세
                if surtax == '': surtax = 0

                item_supply_total = request.data['itemData[' + str(num) + '][item_supply_total]']  # 합계
                if item_supply_total == '': item_supply_total = 0

                export_quantity = request.data['itemData[' + str(num) + '][export_quantity]']  # 출하수량
                if export_quantity == '': export_quantity = 0

                ordering_ex_item_id = request.data['itemData[' + str(num) + '][ordering_ex_item]']  # 출하항목 ID
                item_num = request.data['itemData[' + str(num) + '][item_num]']  # 출하번호

                user = request.user
                num = generate_code('O', ItemOut, 'num', user)

                # 출하등록 취소
                out = OrderingExItems.objects.get(id=ordering_ex_item_id)
                out.delete()

                # 재고출고 취소
                qs = ItemOut.objects.filter(id=out.item_out_id)
                if qs:
                    item_out_row = qs.get(id=out.item_out_id)
                    item_out_row.delete()

                # 주문항목 남은 재고량 재계산
                ordering_item = OrderingItems.objects.get(id=int(ordering_item_id))
                export_now_quantity = ordering_item.export_now_quantity
                to_export = export_now_quantity - float(export_quantity)
                ordering_item.export_now_quantity = to_export
                ordering_item.location_id = None
                ordering_item.export_quantity = 0
                ordering_item.save()

                # 미출하 모두 삭제
                qs = OrderingExItems.objects.filter(enterprise=self.request.user.enterprise).all()
                qs = qs.filter(ordering_item_id=ordering_item_id, out=False)
                for row in qs:
                    row.delete()

                item = ItemMaster.objects.get(pk=item_id)
                item.stock = item.stock + float(export_quantity)
                item.save()

                # 미출하 등록
                a = ordering_item.quantity  # 주문수량
                b = ordering_item.export_now_quantity  # 출하된 수량
                remain = (a - b) if ((a - b) >= 0) else 0  # 미출하 수량 (남은 수량)

                if remain > 0:  # 미출하 내용등록
                    OrderingExItems.objects.create(out=False,  # 미출하
                                                   ordering_id=ordering_id,
                                                   ordering_item_id=ordering_item_id,
                                                   num=num,
                                                   item_id=item_id,
                                                   item_detail=item_detail,
                                                   item_unit=item_unit,
                                                   item_price=item_price,

                                                   quantity=quantity,  # 주문수량
                                                   supply_price=supply_price,  # 공급가

                                                   surtax=surtax,  # 부가세
                                                   item_supply_total=item_supply_total,  # 합계

                                                   export_quantity=remain,  # 출하수량 ? 미출하수량
                                                   export_date=None,  # 출하일자
                                                   export_address=None,  # 출하주소

                                                   created_by=user,
                                                   updated_by=user,
                                                   created_at=user,
                                                   updated_at=user,
                                                   enterprise=request.user.enterprise
                                                   )

            queryset = self.filter_queryset(self.get_queryset()).filter(enterprise=self.request.user.enterprise,
                                                                        ordering_id=ordering_id).order_by('item_id')
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return super().destroy(request, request, *args, **kwargs)
