from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import SubprocessProgress
from api.permission import MesPermission
from api.serializers import SubprocessProgressSerializer


class SubprocessProgressManagementViewSet(viewsets.ModelViewSet):
    queryset = SubprocessProgress.objects.all()
    serializer_class = SubprocessProgressSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['subprocess__process', 'id']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessProgressManagementViewSet", "get_queryset", False)

        user = self.request.user
        qs = SubprocessProgress.objects.filter(enterprise=self.request.user.enterprise).order_by('-created_at', '-id')
        return qs if user.is_master else qs.filter(updated_by=user)

    def list(self, request, *args, **kwargs):
        """
        작업진행현황 - 공정과정 조회

        공정과정을 조회할 수 있는 함수로, 4.3 작업진행현황등록 설계화면의 아래쪽 테이블에 사용되는 데이터를 출력합니다. \
        상단의 "공정명 조회" 부분에서 공정을 선택할 경우, 하단의 세부공정명, 작업장명, 생산지시수량, 작업자명, 작업일정이 자동으로 \
        나타나야 합니다. 여기에서 출력되는 내용들은 세부공정조회 endpoint를 를 이용하시면 수월합니다. \
        작업신쟁현황은 작업진행현황 `CodeMaster`를 이용하시길 바랍니다.
        """
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessProgressManagementViewSet", "create", False)
        """
        작업진행현황 - 공정과정 등록

        작업진행현황의 공정과정 등록을 위한 함수로, 4.3 작업진행현황 설계화면에서 내용 입력 -> "등록" 버튼 클릭 -> \
        "저장"을 클릭하면 호출됩니다.
        """
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        작업진행현황 - 공정과정 조회 (개별)

        개별 공정과정을 조회하는 함수입니다.
        """
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessProgressManagementViewSet", "partial_update", False)
        """
        작업진행현황 - 공정과정 수정

        공정과정 수정 함수로, \
        4.3 작업진행현황 설계화면의 "수정" 버튼 클릭 후 내용 채운 뒤 "저장"을 클릭하면 호출됩니다.
        """
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "SubprocessProgressManagementViewSet", "destroy", False)
        """
        작업진행현황 - 공정과정 삭제

        공정과정 삭제 함수로,
        4.3 작업진행현황 설계화면의 "삭제" 버튼 클릭 후 "저장"을 클릭하면 호출됩니다.
        """
        return super().destroy(request, request, *args, **kwargs)
