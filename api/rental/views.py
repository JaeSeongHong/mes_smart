from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models import CodeMaster, CustomerMaster, RentalMaster, Rental
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, RentalMasterSerializer, RentalSerializer


class RentalViewSet(viewsets.ModelViewSet):
    class RentalFilter(FilterSet):
        created_at = DateFromToRangeFilter()

        class Meta:
            model = Rental
            fields = ['created_at', 'master__id', 'master__item__id', 'master__serial', 'customer__id', 'customer_name']

    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = RentalFilter
    pagination_class = None

    def get_queryset(self):
        return Rental.objects.filter(enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        """
        대여등록, 회수, 현황 조회

        대여등록, 회수, 현황 조회를 위한 함수로, 5.2 대여등록관리, 5.3 대여회수관리, 5.4 대여현황조회 하단의 테이블에 사용되는 \
        데이터를 출력합니다. 5.2 대여등록 페이지에서는 회수 관련 field들을 제외하고 출력하시고, 그 외에는 전부 출력하시면 됩니다 \
        (전부 같은 항목을 공유하고 있기 때문입니다.)\
        대여일 범위는 `created_at_after` (시작기간)과 `created_at_before` (종료기간)을 이용하시기 바랍니다.

        대여등록, 회수, 현황조회의 경우 DB/서버/클라이언트 로직의 복잡함을 줄이기 위해서 동일한 endpoint들을 공유하도록 \
        설계하였습니다. 대여등록은 `POST`, 회수등록은 관련 항목들과 함께 `PATCH`를 이용하시면 됩니다. \
        각각에 대한 상세한 내용은 각 method들의 설명을 참고하시길 바랍니다.
        """
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        대여등록

        대여품목을 대여해주기 위한 "대여등록"을 위한 함수로, 5.2 대여등록관리 설계화면에서 내용 입력 -> "등록" 버튼 클릭 -> \
        "저장"을 클릭하면 호출됩니다.

        `Rental`은 대여와 회수를 동시에 관리합니다. 따라서 등록시에는 회수와 관련된 내용은 빼주시고, "반납 예정입", "대여품 상태", \
        "대여업체", "대여자명", "대여자 연락처" 만 보내주시면 됩니다.

        """
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        대여, 회수, 현황 조회 (개별)

        개별 대여, 회수, 현황 조회 함수입니다.
        """
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        대여 수정과 회수 등록, 수정, 삭제

        본 endpoint를 이용하여 대여등록 수정과 회수등록/수정/삭제 네가지 기능을 수행할 수 있습니다. \
        - 대여관리을 수정하기 위해서는 `POST` method에서 입력해주신 필드들만 포함하여 전송하면 됩니다. (5.2 대여등록관려의 "수정")
        - 회수등록을 위해서는 `is_returned=true` 를 포함하여 request를 전송해주시면 됩니다. 여기에 추가로 "반납일", "회수품이상유무",
        "대여업체", "반납자명", "반납자연락처"을 포함하시면 됩니다. (5.3 대여회수관리의 "등록")
        - 회수수정은 회수등록에서 수정하고싶은 "반납일" ... "반납자연락처" 필드를 포함하여 전송해주시면 됩니다.\
        (5.3 대여회수관리의 "수정")
        - 회수삭제를 위해서는 회수등록과 반대로 `is_returned=false`을 포함하여 전송해주시면 됩니다. (5.3 대여회수관리 "삭제")

        """
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        대여 삭제

        대여, 회수를 삭제하는 함수로, 5.2 대여등록관리 설계화면의 "삭제" 버튼 클릭 후 "저장" 클릭하면 호출됩니다. \
        """
        return super().destroy(request, request, *args, **kwargs)
