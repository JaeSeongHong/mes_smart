from django.db import transaction
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import Request, RequestItems
from api.permission import MesPermission
from api.serializers import RequestSerializer, RequestItemsSerializer
from api.pagination import PostPageNumberPagination5


class RequestViewSet(viewsets.ModelViewSet):
    class RequestFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Request
            fields = ['id', 'code_id']

    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RequestFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        qs = Request.objects.filter(enterprise=self.request.user.enterprise)

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
            item_remarks = []
            item_file = []

            # 초기화
            for i in range(0, cnt):
                item_id.append(None)
                item_detail.append(None)
                item_unit.append(None)

                item_quantity.append(None)
                item_remarks.append(None)
                item_file.append(None)

            for i in range(0, cnt):
                item_id[i] = request.data['item_id[' + str(i) + ']']  # 품번 ID
                item_detail[i] = request.data['item_detail[' + str(i) + ']']  # 품명상세
                item_unit[i] = request.data['item_unit[' + str(i) + ']']  # 품명단위

                item_quantity[i] = request.data['item_quantity[' + str(i) + ']']  # 수량
                item_remarks[i] = request.data['item_remarks[' + str(i) + ']']  # 비고
                item_file[i] = request.data['file[' + str(i) + ']']

                # 의뢰서 등록
                row = RequestItems.objects.create(request_id=res.data['id'],
                                                  item_id=item_id[i],
                                                  item_detail=item_detail[i],
                                                  item_unit=item_unit[i],

                                                  quantity=(0 if (item_quantity[i] == '') else item_quantity[i]),
                                                  remarks=item_remarks[i],
                                                  file=item_file[i],

                                                  created_by=user,
                                                  updated_by=user,
                                                  created_at=user,
                                                  updated_at=user,
                                                  enterprise=request.user.enterprise
                                                  )

        return res

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, request, *args, **kwargs)


class RequestItemsViewSet(viewsets.ModelViewSet):
    queryset = RequestItems.objects.all()
    serializer_class = RequestItemsSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'request_id']
    pagination_class = None

    def get_queryset(self):
        return RequestItems.objects.filter(enterprise=self.request.user.enterprise)

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
