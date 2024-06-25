from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.models import Bom, ItemMaster, CustomerMaster, CodeMaster
from api.permission import MesPermission
from api.serializers import BomSerializer
from api.pagination import PostPageNumberPagination5
from rest_framework.exceptions import ValidationError


class BomViewSet(viewsets.ModelViewSet):
    queryset = Bom.objects.all()
    serializer_class = BomSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['id', 'master__id', 'master__product_name', 'master__model_name', 'master__version',
                        'manufacturer__name', 'customer__name', 'created_at']
    search_fields = ['master__detail__name', 'master__shape', 'master__item_group__name', "master__brand__name", "product_name", "bom_number", "nice_number"]
    pagination_class = PostPageNumberPagination5

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "BomViewSet", "get_queryset", False)
        return Bom.objects.filter(enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        """
        BOM 조회

        BOM 조회 함수로, 해당 BOM 포함되는 자재들을 반환합니다. 2.2.1 BOM 관리 설계화면의 아래쪽 테이블에 사용되는 함수입니다.

        본 설계방식은 하나의 Bom 형식에 여러 Bom 행들이 들어가는 형태입니다. Bom 행들에는 각각의 형식 내용(열)에 따른 값들이 들어갑니다.

        기존의 is_root를 이용한 생산제품명 등을 얻는 방식은 Bom의 일부 필드가 BomMaster로 병합됨에 따라서 사라졌습니다. \
        BomMaster를 이용하시길 바랍니다.
        """
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "BomViewSet", "create", False)
        """
        BOM - 자재추가

        BOM의 자재추가 함수로, 2.2.1 BOM 관리 설계화면의 "자재추가"에 사용됩니다.
        """
        if request.data['item'] == request.data['master']:
            raise ValidationError("BOM과 같은 품목은 등록할 수 없습니다. (" + request.data['item'] + ")")
        elif ItemMaster.objects.filter(id__iexact=request.data['item']):
            return super().create(request, request, *args, **kwargs)
        elif ItemMaster.objects.filter(code__iexact=request.data['item']):
            _mutable = request.data._mutable
            request.data._mutable = True

            qs = ItemMaster.objects.filter(code=request.data['item'])
            for item in qs:
                request.data['item'] = item.id
                request.data['item_name'] = item.name

            if request.data['customer'] != '':
                if CustomerMaster.objects.filter(name=request.data['customer'], enterprise_id=self.request.user.enterprise):
                    qs = CustomerMaster.objects.filter(name=request.data['customer'], enterprise_id=self.request.user.enterprise)
                    for customer in qs:
                        print(customer)
                        request.data['customer'] = customer.id
                else:
                    raise ValidationError("품번 : " + str(request.data['item']) + " / 존재하지 않는 고객사입니다. : " + request.data['customer'])

            if request.data['manufacturer'] != '':
                if CustomerMaster.objects.filter(name=request.data['manufacturer'], enterprise_id=self.request.user.enterprise):
                    qs = CustomerMaster.objects.filter(name=request.data['manufacturer'], enterprise_id=self.request.user.enterprise)
                    for manufacturer in qs:
                        print(manufacturer)
                        request.data['manufacturer'] = manufacturer.id
                else:
                    raise ValidationError("품번 : " + str(request.data['item']) + " / 존재하지 않는 협력사입니다. : " + request.data['manufacturer'])

            if request.data['storage'] != '':
                if CodeMaster.objects.filter(name=request.data['storage'], enterprise_id=self.request.user.enterprise):
                    qs = CodeMaster.objects.filter(name=request.data['storage'], enterprise_id=self.request.user.enterprise)
                    for storage in qs:
                        print(storage)
                        request.data['storage'] = storage.id
                else:
                    raise ValidationError("품번 : " + str(request.data['item']) + " / 존재하지 않는 생산공정(창고)입니다. : " + request.data['storage'])
            request.data._mutable = _mutable

            return super().create(request, request, *args, **kwargs)
        else:
            raise ValidationError("존재하지 않는 품목 번호입니다. : " + request.data['item'])

    def retrieve(self, request, *args, **kwargs):
        """
        BOM - 자재 조회

        BOM의 개별 자재를 조회하는 함수입니다.
        """
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "BomViewSet", "partial_update", False)
        """
        BOM - 자재 수정

        BOM의 자재수정 함수로, 2.2.1 BOM 관리 설계화면의 "자재수정"에 사용됩니다.
        """
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "BomViewSet", "destroy", False)
        """
        BOM - 자재 삭제

        BOM의 자재삭제 함수로, 2.2.1 BOM 관리 설계화면의 "자재삭제"에 사용됩니다.
        """
        return super().destroy(request, request, *args, **kwargs)

class BomSelectViewSet(viewsets.ModelViewSet):
    queryset = Bom.objects.all()
    serializer_class = BomSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'master__id', 'master__product_name', 'master__model_name', 'master__version',
                        'manufacturer__name', 'customer__name', 'created_at']
    pagination_class = None

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "BomViewSet", "get_queryset", False)
        return Bom.objects.filter(enterprise=self.request.user.enterprise).all()