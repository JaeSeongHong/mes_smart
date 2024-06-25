from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models import CodeMaster
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, CodeMasterSelectSerializer
from rest_framework.pagination import PageNumberPagination


class CodeMasterViewSet(viewsets.ModelViewSet):
    class CodeMasterFilter(FilterSet):
        group = CharFilter(field_name='group', method='filter_group')

        def filter_group(self, queryset, name, value, ):
            return queryset.filter(group__code=value)

        class Meta:
            model = CodeMaster
            fields = ['group', 'name', 'enable']

    queryset = CodeMaster.objects.all()
    serializer_class = CodeMasterSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete', ]  # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = CodeMasterFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return CodeMaster.objects.filter(enterprise=self.request.user.enterprise) \
            .order_by('group__code', '-code')

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, request, *args, **kwargs)


class CodeMasterSelectView(viewsets.ModelViewSet):
    class CodeMasterFilter(FilterSet):
        group = CharFilter(field_name='group', method='filter_group')

        def filter_group(self, queryset, name, value, ):
            return queryset.filter(group__code=value)

    queryset = CodeMaster.objects.all()
    serializer_class = CodeMasterSelectSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']  # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = CodeMasterFilter
    pagination_class = None

    def get_queryset(self):
        return CodeMaster.objects.filter(enterprise=self.request.user.enterprise) \
                .order_by('group__code', 'code').all()
