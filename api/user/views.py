from django.db.models import F
from django.db.models.functions import Coalesce
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from api.models import UserMaster, MenuMaster, CodeMaster
from api.serializers import UserMasterSerializer, MenuSerializer
from rest_framework import status, viewsets


# from api.user.authentication import get_expire_time


class CustomObtainAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        location = CodeMaster.objects.filter(name='입고창고', enterprise_id=user.enterprise_id).first()
        if location:
            location_id = location.id
        else:
            location_id = 1;
            #raise Exception('입고창고 레코드를 찾을 수 없습니다.')

        #         Token.objects.filter(user=user, created__lt=get_expire_time()).delete()

        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key, 'user': UserMasterSerializer(user).data, 'location': location_id}, status=status.HTTP_200_OK)


class MenuHandler(viewsets.ModelViewSet):
    queryset = MenuMaster.objects.all()
    serializer_class = MenuSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        # 해당 유저의 메뉴 정보 가져오기
        qs = MenuMaster.objects.filter(menuauth__enterprise_id=self.request.user.enterprise_id
                                       , menuauth__user_id=self.request.user.id,
                                       menuauth__del_flag='N'
                                       ).annotate(alias=Coalesce('menuauth__alias', F('name'))
                                                  ).values('id', 'code', 'alias', 'path', 'type', 'comment', 'i_class'
                                                           , 'created_by_id', 'created_at', 'updated_by_id',
                                                           'updated_at'
                                                           , 'del_flag').order_by('menuauth__order')

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
