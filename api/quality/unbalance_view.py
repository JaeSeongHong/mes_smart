from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import Qunbalance, QunbalanceDetail
from api.permission import MesPermission
from api.serializers import UnbalanceSerializer, UnbalanceDetailSerializer
from rest_framework.pagination import PageNumberPagination


class UnbalanceViewSet(viewsets.ModelViewSet):
    class UnbalanceFilter(FilterSet):

        class Meta:
            model = Qunbalance
            fields = ['id']

    queryset = Qunbalance.objects.all()
    serializer_class = UnbalanceSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = UnbalanceFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnbalanceViewSet", "get_queryset", False)
        qs = Qunbalance.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')

        if 'last' in self.request.query_params:
            last = self.request.query_params['last']
            if last == 'true':
                last_row = qs.filter().order_by('id').last()
                if last_row:
                    if last_row.complete == 1:
                        qs = qs.none()  # 등록된 데이타라면 안보여줌
                    else:
                        qs = qs.filter(id=last_row.id)

        if 'complete' in self.request.query_params:
            complete = self.request.query_params['complete']
            qs = qs.filter(complete=complete)

        if 'item_name' in self.request.query_params:
            item_name = self.request.query_params['item_name']
            if item_name != '':
                qs = qs.filter(item_name__contains=item_name)

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(test_date__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(test_date__lte=to_date)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnbalanceViewSet", "create", False)
        res = super().create(request, request, *args, **kwargs)

        first_unbalance1 = request.data['first_unbalance1']
        first_angle1 = request.data['first_angle1']
        first_unbalance2 = request.data['first_unbalance2']
        first_angle2 = request.data['first_angle2']

        user = request.user
        QunbalanceDetail.objects.create(num_id=int(res.data['id']),
                                        unbalance1=first_unbalance1,
                                        angle1=first_angle1,
                                        unbalance2=first_unbalance2,
                                        angle2=first_angle2,

                                        created_by=user,
                                        updated_by=user,
                                        created_at=user,
                                        updated_at=user,
                                        enterprise_id=request.user.enterprise.id
                                       )
        return res

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnbalanceViewSet", "partial_update", False)
        res = super().partial_update(request, request, *args, **kwargs)
        return res

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnbalanceViewSet", "destroy", False)
        qs = QunbalanceDetail.objects.filter(num=kwargs.get('pk'))
        for row in qs:
            row.delete()

        return super().destroy(request, request, *args, **kwargs)


class UnbalanceDetailViewSet(viewsets.ModelViewSet):
    class UnbalanceDetailFilter(FilterSet):

        class Meta:
            model = QunbalanceDetail
            fields = ['id', 'num']

    queryset = QunbalanceDetail.objects.all()
    serializer_class = UnbalanceDetailSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = UnbalanceDetailFilter
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnbalanceDetailViewSet", "get_queryset", False)
        qs = QunbalanceDetail.objects.filter(enterprise=self.request.user.enterprise).all().order_by('-id')
        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnbalanceDetailViewSet", "create", False)
        res = super().create(request, request, *args, **kwargs)
        num = res.data['num']
        qs = Qunbalance.objects.filter(id=num)
        if qs:
            row = qs.get(id=num)
            row.last_unbalance1 = float(res.data['unbalance1'])
            row.last_angle1 = float(res.data['angle1'])
            row.last_unbalance2 = float(res.data['unbalance2'])
            row.last_angle2 = float(res.data['angle2'])
            row.save()

        return res

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnbalanceDetailViewSet", "partial_update", False)
        res = super().partial_update(request, request, *args, **kwargs)
        return res

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnbalanceDetailViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)