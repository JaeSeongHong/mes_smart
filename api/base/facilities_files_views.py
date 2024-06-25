from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models import FacilitiesMaster, FacilitiesFiles
from api.permission import MesPermission
from api.serializers import FacilitiesMasterSerializer, FacilitiesFilesSerializer


class FacilitiesFilesViewSet(viewsets.ModelViewSet):
    queryset = FacilitiesFiles.objects.all()
    serializer_class = FacilitiesFilesSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['facility', ]
    pagination_class = None

    def get_queryset(self):
        return FacilitiesFiles.objects.filter(facility__enterprise=self.request.user.enterprise).all()

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, request, *args, **kwargs)
