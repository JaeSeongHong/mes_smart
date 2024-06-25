import re
from django.db import transaction
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import Estimate, EstimateItems
from api.permission import MesPermission
from api.serializers import EstimateSerializer, EstimateItemsSerializer
from api.pagination import PostPageNumberPagination5
from api.temp_volt_monitoring.send_mail import send_gmail, send_gmail_pdf

class EstimateViewSet(viewsets.ModelViewSet):
    class EstimateFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Estimate
            fields = ['id', 'code_id']

    queryset = Estimate.objects.all()
    serializer_class = EstimateSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = EstimateFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        qs = Estimate.objects.filter(enterprise=self.request.user.enterprise)

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

    @transaction.atomic
    def sendmail_to_company(self, request, *args, **kwargs):

        mail_info = dict(gmail_user='greenbi5693@gmail.com', gmail_password='grqsbumhzdmrjeav',
                         sent_from='greenbi5693@gmail.com', send_to='greenbi5693@naver.com',
                         subject="견적서", body="견적서 입니다.")

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
                             Bcc=enter_email,
                             subject=request.data['enterprise_name'] + " - 발행한 견적서입니다.", enterprise=request.data['enterprise_name'],
                             enter_email=enter_email, enter_fax=enter_fax, enter_call=enter_call, logo_img=logo_img, type="견적서")

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

                # 의뢰서 등록
                row = EstimateItems.objects.create(estimate_id=res.data['id'],
                                                   item_id=item_id[i],
                                                   item_detail=item_detail[i],
                                                   item_unit=item_unit[i],

                                                   quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                                                   item_price=(0 if (item_price[i] == '') else item_price[i]),
                                                   supply_price=(0 if (supply_price[i] == '') else supply_price[i]),
                                                   surtax=(0 if (surtax[i] == '') else surtax[i]),
                                                   item_supply_total=(0 if (item_supply_total[i] == '') else item_supply_total[i]),

                                                   remarks=item_remarks[i],

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

        res = super().partial_update(request, request, *args, **kwargs)

        if 'itemCnt' in request.data:
            # Remove origin data
            es_qs = EstimateItems.objects.filter(estimate_id=res.data['id'])

            for es in es_qs:
                row = EstimateItems.objects.get(pk=es.id)
                row.delete()

            # Create New data
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

                # 견적서 등록
                row = EstimateItems.objects.create(estimate_id=res.data['id'],
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

                                                   created_by=user,
                                                   updated_by=user,
                                                   created_at=user,
                                                   updated_at=user,
                                                   enterprise=request.user.enterprise
                                                   )

        return res


    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, request, *args, **kwargs)


class EstimateItemsViewSet(viewsets.ModelViewSet):

    queryset = EstimateItems.objects.all()
    serializer_class = EstimateItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'estimate_id']
    pagination_class = PostPageNumberPagination5


    def get_queryset(self):
        return EstimateItems.objects.filter(enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, request, *args, **kwargs)
