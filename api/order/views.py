import uuid
from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Order
from api.order.write_purchase_order_sheet import buildexcel
from api.permission import MesPermission
from api.serializers import OrderSerializer
from api.temp_volt_monitoring.send_mail import send_gmail
from api.pagination import PostPageNumberPagination5


def build_excel(order, request):
    target = 'data/purchase_order_{}.xlsx'.format(str(uuid.uuid1()))
    buildexcel({
        'company': order.customer.name,
        'charge': order.customer.charge_name + '님',
        'tel': order.customer.charge_phone,
        'date': '',
        'po': order.po,
        'cpo': order.cpo,

        'no': 1,
        'spec': [order.item.name, order.item.model.name if order.item.model is not None else ''],
        'qty_num': order.amount,
        'qty_unit': order.item.unit.name if order.item.unit is not None else 'EA',
        'unit_price': order.price,
        'price': order.price * order.amount,
        'note': [order.etc],

        'payment_terms': order.purchase_condition,
        'delivery_terms': order.date,
        'packing': order.package,
        'quality_warrenty': order.quality_guarantee,
        'delivery_location': order.place,

        'site': 'www.j-mcsys.com',
        'manager': request.user.username + request.user.job_position.name if request.user.job_position is not None else '',
        'email': 'Email:' + request.user.email if request.user.email is not None else '',
        'tel2': 'Tel:' + request.user.tel if request.user.tel is not None else ''
    }, target)
    return target


class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer', 'item__code', 'item__name', 'po']
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        return Order.objects.filter(enterprise=self.request.user.enterprise).all()

    def sendmail_to_company(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=request.data.get('pk', 0))
        target = build_excel(order, self.request)

        mail_info = dict(gmail_user='ssmesdev@gmail.com',
                         gmail_password='mes_developer1',
                         send_to=order.customer.email, subject="발주서", body="발주서 입니다.")
        send_gmail(mail_info, target)

        order.mail_sent_at = datetime.now()
        order.save()
        return Response({}, status=status.HTTP_201_CREATED)

    def download(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=request.query_params.get('pk', 0))
        target = build_excel(order, self.request)

        order.is_excel_printed = True
        order.save()

        return Response({'url': '/' + target}, status=status.HTTP_201_CREATED)
