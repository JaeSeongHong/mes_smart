
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import Process, Subprocess
from api.pagination import PostPageNumberPagination5
from api.permission import MesPermission
from api.serializers import ProcessSerializer


class ProcessManagementViewSet(viewsets.ModelViewSet):
    class ProcessManagementFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Process
            fields = ['created_at', 'customer__id', 'bom_master', 'bom_master__bom_name', 'bom_master__product_name', 'factory_classification',
                      'bom_master__version', 'name', 'amount', 'code', 'complete', 'bom_master__brand', 'bom_master__item_group',
                      'bom_master__detail', 'bom_master__shape']

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['bom_master__detail', 'bom_master__shape', 'bom_master__product_name', "bom_master__brand__name", "bom_master__item_group__name"]
    filterset_class = ProcessManagementFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ProcessManagementViewSet", "get_queryset", False)
        print(self.request.query_params)
        qs = Process.objects.filter(enterprise=self.request.user.enterprise).order_by('-id')

        # if 'fr_date' in self.request.query_params:
        #     fr_date = self.request.query_params['fr_date']
        #     if fr_date != '':
        #         qs = qs.filter(to_date__gte=fr_date)
        #
        # if 'to_date' in self.request.query_params:
        #     to_date = self.request.query_params['to_date']
        #     if to_date != '':
        #         qs = qs.filter(fr_date__lte=to_date)


        if 'item_code' in self.request.query_params:
            item_code = self.request.query_params['item_code']
            qs = qs.filter(bom_master__bom_number=item_code)
        if 'nice_number' in self.request.query_params:
            nice_number = self.request.query_params['nice_number']
            qs = qs.filter(bom_master__nice_number=nice_number)

        if 'brand' in self.request.query_params:
            brand = self.request.query_params['brand']
            qs = qs.filter(bom_master__brand=brand)

        if 'item_group' in self.request.query_params:
            item_group = self.request.query_params['item_group']
            qs = qs.filter(bom_master__item_group=item_group)


        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ProcessManagementViewSet", "create",
                False)
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ProcessManagementViewSet", "partial_update",
                False)

        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ProcessManagementViewSet", "destroy",
                False)

        qs = Subprocess.objects.filter(process_id=kwargs["pk"])

        # 하위에 있는 모든 세부공정 삭제
        for row in qs:
            row = Subprocess.objects.get(id=row.id)
            row.delete()

        return super().destroy(request, request, *args, **kwargs)


class ProcessHasFaultReasonViewSet(viewsets.ModelViewSet):
    class ProcessManagementFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Process
            fields = ['created_at', 'customer__id', 'bom_master', 'bom_master__bom_name', 'bom_master__product_name', 'factory_classification',
                      'bom_master__version', 'name', 'amount', 'code', 'complete']

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProcessManagementFilter
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ProcessManagementViewSet", "get_queryset", False)

        qs = Process.objects.filter(enterprise=self.request.user.enterprise, has_fault_reason=True).order_by('-id')

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(to_date__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(fr_date__lte=to_date)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)


class ProcessHasFaultReasonSelectViewSet(viewsets.ModelViewSet):
    class ProcessManagementFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Process
            fields = ['created_at', 'customer__id', 'bom_master', 'bom_master__bom_name', 'bom_master__product_name', 'factory_classification',
                      'bom_master__version', 'name', 'amount', 'code', 'complete']

    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProcessManagementFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ProcessManagementViewSet", "get_queryset", False)

        qs = Process.objects.filter(enterprise=self.request.user.enterprise, has_fault_reason=True).order_by('-id')

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(to_date__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(fr_date__lte=to_date)

        if 'actual_fr_date' in self.request.query_params:
            fr_date = self.request.query_params['actual_fr_date']
            if fr_date != '':
                qs = qs.filter(actual_to_date__gte=fr_date)
                print(qs)

        if 'actual_to_date' in self.request.query_params:
            to_date = self.request.query_params['actual_to_date']
            if to_date != '':
                qs = qs.filter(actual_fr_date__lte=to_date)
                print(qs)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)
