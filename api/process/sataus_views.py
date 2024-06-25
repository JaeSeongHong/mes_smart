from django.db.models import Q
from django_filters.rest_framework import FilterSet, DateFromToRangeFilter, DjangoFilterBackend

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import Process, Subprocess
from api.permission import MesPermission
from api.serializers import ProcessStatusSerializer
from api.pagination import PostPageNumberPagination5

class ProcessStatusViewSet(viewsets.ModelViewSet):
    class ProcessManagementFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Process
            fields = ['created_by', 'created_at', 'customer__id',
                      'bom_master', 'bom_master__bom_name', 'bom_master__product_name', 'name']

    queryset = Process.objects.all()
    serializer_class = ProcessStatusSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']  # to remove 'put'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['bom_master__detail', 'bom_master__shape', 'bom_master__product_name', "bom_master__brand__name",
                     "bom_master__item_group__name"]
    filterset_class = ProcessManagementFilter
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "ProcessStatusViewSet", "get_queryset", False)
        qs = Process.objects.filter(enterprise=self.request.user.enterprise).all()

        if 'fr_date' in self.request.query_params:
            fr_date = self.request.query_params['fr_date']
            if fr_date != '':
                qs = qs.filter(to_date__gte=fr_date)

        if 'to_date' in self.request.query_params:
            to_date = self.request.query_params['to_date']
            if to_date != '':
                qs = qs.filter(fr_date__lte=to_date)
                # qs = qs.filter(to_date__gte=to_date)

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

        if 'status' in self.request.query_params:
            status = self.request.query_params['status']

            if status == '대기':
                qs = qs.filter(complete=False)
                for row in qs:
                    if Subprocess.objects.filter(process_id=row.id).exists():
                        qs = qs.exclude(id=row.id)
            if status == '완료':
                qs = qs.filter(complete=True)
            if status == '진행':
                qs = qs.filter(complete=False)
                for row in qs:
                    if Subprocess.objects.filter(process_id=row.id).exists():
                        pass
                    else:
                        qs = qs.exclude(id=row.id)
        return qs

    def list(self, request, *args, **kwargs):
        """
        공정진행현황 조회

        공정진행현황을 조회할 수 있는 함수로, 4.4 공정진행현황조회 설계화면의 아래쪽 테이블에 사용되는 데이터를 출력합니다. \
        TV 화면도 이 함수를 똑같이 사용하시길 바랍니다.

        본 페이지는 전반적인 공정 진행 현황을 조회하는 집계 페이지 입니다. 기존에 사용되는 `Process`, `Subprocess`, \
        `SubprocessProgress`들이 전부 계산되어 각각의 생상공정별과 세부공정에 따른 지시수량, 생산수량, 불량수량, 진행상태를 나타냅니다. \
        아래쪽 테이블의 각 "생상공정명"은 `Process` (즉, `process/` `GET` method의 결과)와 같은 형태로 읽어들이시면 됩니다. \
        "세부공정 진행현황" 에 나타날 데이터는 `status`라는 집계 필드를 이용하시면 됩니다. 이 필드에는 `types`, `order_amounts`, \
        `produce_amounts`, `faulty_amount`, `progresses` array 형태의 필드들이 존재하고, 이들은 전부 존재하는 세부공정 개수만큼 \
        출력됩니다 (즉, 세부공정명을 추가하지 않았다면, 수입검사 ... 출고까지 하여 총 7개). 각각의 필드에 대한 내용은 아래 bullets을 \
        참고하시기 바랍니다.
        - `types`: 어떤 세부공정임을 나타냄.
        - `order_amounts`: 지시수량.
        - `produce_amounts`: 생산수량.
        - `faulty_amounts`: 불량수량.
        - `progresses`: 진행상태.
        """
        return super().list(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        공정진행현황 (개별)

        개별 공정진행현황을 조회하는 함수입니다.
        """
        return super().retrieve(request, request, *args, **kwargs)
