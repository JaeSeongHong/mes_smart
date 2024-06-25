import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer

from api.models import CodeMaster, CustomerMaster, GroupCodeMaster
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, GroupCodeMasterSerializer


class GroupCodeMasterViewSet(viewsets.ModelViewSet):
    queryset = GroupCodeMaster.objects.all()
    serializer_class = GroupCodeMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch']  # to remove 'put'
    pagination_class = None

    def get_queryset(self):
        return GroupCodeMaster.objects.filter(enterprise=self.request.user.enterprise) \
            .order_by('code').all()

    def list(self, request, *args, **kwargs):
        """
        코드마스터 - 그룹코드 조회

        그룹코드 조회 함수로, 1.2 그룹코드관리 (팝업창) 설계화면의 아래쪽 테이블 내용에 들어가게 될 내용들입니다.
        """
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        코드마스터 - 그룹코드 생성

        그룹코드 생성 함수입니다. 1.2 그룹코드관리 - "그룹코드 추가" 버튼을 누르면, 결과적으로 이 함수가 호출되어야 합니다.
        """
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        코드마스터 - 상세코드 조회 (개별)

        그룹코드 하나에 대한 조회입니다. 당장 설계서에는 필요하지 않은 함수입니다.
        """
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        코드마스터 - 상세코드 수정

        그룹코드 수정 함수입니다. 1.2 그룹코드관리 - "그룹코드 수정" 버튼을 누르면, 결과적으로 이 함수가 호출되어야 합니다.
        """
        return super().partial_update(request, request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['foo'] = 'bar'
        return context


# 코드마스터 초기 기본값 세팅
class GenerateCodeMaster(viewsets.ModelViewSet):
    queryset = GroupCodeMaster.objects.all()
    serializer_class = GroupCodeMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch']  # to remove 'put'
    pagination_class = None

    def get_queryset(self):
        return GroupCodeMaster.objects.filter(enterprise=self.request.user.enterprise) \
            .order_by('code').all()

    def list(self, request, *args, **kwargs):
        """
        코드마스터 - 그룹코드 조회

        그룹코드 조회 함수로, 1.2 그룹코드관리 (팝업창) 설계화면의 아래쪽 테이블 내용에 들어가게 될 내용들입니다.
        """
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # 내 enterprise_id
        now = datetime.datetime.now()
        list_codemaster = []
        list_codemaster.append({'code': 104, 'name': '공장구분'})
        list_codemaster.append({'code': 105, 'name': '단위'})
        list_codemaster.append({'code': 106, 'name': '용기타입'})
        list_codemaster.append({'code': 107, 'name': '창고구분'})
        list_codemaster.append({'code': 108, 'name': '거래구분'})
        list_codemaster.append({'code': 109, 'name': '공정구분(세부공정)'})
        list_codemaster.append({'code': 110, 'name': '작업장구분'})
        list_codemaster.append({'code': 111, 'name': '설비구분'})
        list_codemaster.append({'code': 112, 'name': '사용자(고용)구분'})
        list_codemaster.append({'code': 113, 'name': '부서구분'})
        list_codemaster.append({'code': 114, 'name': '직위(직급)구분'})
        list_codemaster.append({'code': 115, 'name': '품종(품목)구분'})
        list_codemaster.append({'code': 116, 'name': '모델'})
        list_codemaster.append({'code': 117, 'name': '버전구분'})
        list_codemaster.append({'code': 118, 'name': '자재분류(품목구분)'})
        list_codemaster.append({'code': 119, 'name': '칼라구분'})
        list_codemaster.append({'code': 122, 'name': '대여품구분'})
        list_codemaster.append({'code': 123, 'name': '온습도관리구분'})
        list_codemaster.append({'code': 124, 'name': '현황(작업진행현황)구분'})
        list_codemaster.append({'code': 900, 'name': '입고현황'})
        qs = self.queryset.filter(enterprise=self.request.user.enterprise)
        # 차후 코드가 추가된 경우 추가 코드만 넣을 수 있도록 개별 처리
        # 코드 마스터가 유니크 처리가 안되어 있으므로 개별 검사 후 처리
        for a in range(0, len(list_codemaster)):
            # 이름이 수정되었을 수도 있으므로, 코드만 비교
            if qs.filter(code=list_codemaster[a]['code']).count() == 0:
                # 생성
                GroupCodeMaster.objects.create(
                    code=list_codemaster[a]['code'], name=list_codemaster[a]['name'],
                    enable=True, created_at=now, updated_at=now,
                    created_by=request.user, enterprise_id=request.user.enterprise_id, updated_by=request.user
                )
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        코드마스터 - 상세코드 조회 (개별)

        그룹코드 하나에 대한 조회입니다. 당장 설계서에는 필요하지 않은 함수입니다.
        """
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        코드마스터 - 상세코드 수정

        그룹코드 수정 함수입니다. 1.2 그룹코드관리 - "그룹코드 수정" 버튼을 누르면, 결과적으로 이 함수가 호출되어야 합니다.
        """
        return super().partial_update(request, request, *args, **kwargs)
