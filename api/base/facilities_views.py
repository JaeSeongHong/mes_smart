from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import FacilitiesMaster
from api.permission import MesPermission
from api.serializers import FacilitiesMasterSerializer


class FacilitiesMasterViewSet(viewsets.ModelViewSet):
    queryset = FacilitiesMaster.objects.all()
    serializer_class = FacilitiesMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['factory', 'process', 'enable', 'name', 'id']
    search_fields = ['name']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "FacilitiesMasterViewSet", "get_queryset", False)
        return FacilitiesMaster.objects.filter(enterprise=self.request.user.enterprise).all()


    def list(self, request, *args, **kwargs):
        """
        설비 조회

        설비 조회 함수로, 1.3 사용자관리 설계화면의 아래쪽 테이블 내용에 들어가게 될 내용들입니다.
        위쪽의 "검색" 기능을 사용하게 된다면 QUERY PARAMS에 적절히 필요 내용들을 함께 전송하시길 바랍니다.
        "공장별"은 코드마스터 (`codes`) 상에 정의되어 있는 공장구분을, "부서별"은 부서구분을 사용하시길 바랍니다.

        permissions 필드는 각 사용자별 메뉴 권한을 의미합니다. 사용법은 'enterprise/'의 GET method를 참고하세요.
        """
        return super().list(request, request, *args, **kwargs)
