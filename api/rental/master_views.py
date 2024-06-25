from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models import CodeMaster, CustomerMaster, RentalMaster
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, RentalMasterSerializer


class RentalMasterViewSet(viewsets.ModelViewSet):

    queryset = RentalMaster.objects.all()
    serializer_class = RentalMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'item__id', 'rental_class__id', 'factory_class__id']
    pagination_class = None

    def get_queryset(self):
        return RentalMaster.objects.filter(enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        """
        대여품목관리 - 대여품목 조회

        대여품목을 조회할 수 있는 함수로, 5.1 대여품목관리 설계화면의 아래쪽 테이블에 사용되는 데이터를 출력합니다. \
        아시다시피, **대여품목관리 항목은 대여관리 요구사항이 변경되었으며, 따라서 자재관리와 관계 없이 별도 DB를 구성합니다.**

        상단의 대여품목명, 모델명, 버전 부분은 `ItemMaster`(즉, 품목관리)의 품목에 해당하는 데이터를 필터링하시면 됩니다. \
        대여품 구분과 공장구분은 `CodeMaster`를 이용하시면 됩니다.

        5.2, 5.3, 5.4 페이지의 상단 대여품목 관련 code, 품목명, 모델명, 버전 등은
        """
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        대여품목관리 - 대여품목 등록

        대여품목관리의 대여품목 등록을 위한 함수로, 5.1 대여품목관리 설계화면에서 내용 입력 -> "등록" 버튼 클릭 -> \
        "저장"을 클릭하면 호출됩니다.
        """
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        대여품목관리 - 대여품목 조회 (개별)

        개별 대여품목을 조회하는 함수입니다.
        """
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        대여품목관리 - 대여품목 수정

        대여품목 수정 함수로, \
        5.1 대여품목관리 설계화면의 "수정" 버튼 클릭 후 내용 채운 뒤 "저장"을 클릭하면 호출됩니다.
        """
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        대여품목관리 - 대여품목 삭제

        대여품목 삭제 함수로,
        5.1 대여품목관리 설계화면의 "삭제" 버튼 클릭 후 "저장"을 클릭하면 호출됩니다.
        """
        return super().destroy(request, request, *args, **kwargs)
