from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from api.models import CodeMaster, CustomerMaster, EnterpriseMaster, UserMaster
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, EnterpriseMasterSerializer


class EnterpriseMasterViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseMaster.objects.all().order_by('code')
    serializer_class = EnterpriseMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code', 'name']
    pagination_class = None

    # def get_queryset(self):
    #     return EnterpriseMaster.objects.filter(enterprise=self.request.user.enterprise).order_by('code').all()

    def list(self, request, *args, **kwargs):
        """
        업체 조회

        업체 (Enterprise) 리소스는 본 시스템을 사용하는 업체에 대한 설명입니다.
        업체 조회는 각 업체별 업체 코드, 업체명, 메뉴별 권한을 출력합니다.

        권한은 Integer field이며, 아래와 같은 규칙이 적용됩니다. 각 메뉴 뒤의 숫자는 Integer field의 bit index입니다. 해당 bit가 1이면\
        허용, 0이면 비허용입니다. 현재 23번째 bit까지 사용중에 있습니다. 예를들어 00000000000000000000000000111111 인 경우 기준정보만 \
        허가된 것입니다.

        - 기준정보: 코드마스터 (0), 거래처 기준정보관리 (1), 사용자 기준정보관리 (2), 설비 기준정보관리 (3), 품목 기준정보관리 (4), \
        사용자 권한관리 (5)
        - BOM 관리: BOM 형식생성 (6), BOM 관리 (7), BOM 조회 (8), 생산계획 대비 재고현황 조회 (9)
        - 자재관리: 자재입고 (10), 자재출고 (11), 자재반입 (12), 자재현황조회 (13), 자재재실사 조정 (14)
        - 공정관리: 공정관리 (15), 세부공정관리 (16), 공정진행현황 등록 (17), 공정진행현황 조회 (18)
        - 대여관리: 대여품목 관리 (19), 대여 등록/회수 관리 (20), 대여현황 조회 (21)
        - 모니터링: 온습도 모니터링 관리 (22), 온습도 현황 조회 (23)

        """
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        """
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        업체 조회 (개별)

        업체 하나에 대한 조회입니다.
        """
        return super().retrieve(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """
        업체 수정

        업체별 권한관리 시에 사용되는 함수입니다. 업체 코드와 이름을 변경해도 무방합니다.
        """

        print('신규업체등록에서 수정할때도 여길 타나?')

        pk = kwargs.get('pk', 0)
        permissions = request.data.get('permissions', 0)
        res = UserMaster.objects.filter(enterprise_id=pk, is_master=True)

        if res.count() == 0:
            raise ValidationError('기업 마스터 ID를 먼저 생성하세요.')

        if res.count() != 1:
            raise ValidationError('is_master는 한명만됩니다. 관리자에게 문의하세요.')

        # 권한이 없는 경우
        users = UserMaster.objects.filter(enterprise_id=pk, is_master=False)
        for user in users:
            userpermissions = ""

            for i in range(0, 99):
                if(user.permissions[i] != permissions[i]):
                    userpermissions +="0"
                else:
                    userpermissions +=user.permissions[i]

            user.permissions = userpermissions
            user.save()

        master = res.first()
        master.permissions = permissions
        master.save()

        tokens = Token.objects.filter(user__enterprise_id=pk).all()
        tokens.delete()

        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        업체 삭제

        """
        return super().destroy(request, request, *args, **kwargs)