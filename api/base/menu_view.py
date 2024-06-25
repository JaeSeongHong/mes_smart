import json

from django.core import serializers
from django.db import transaction
from django.db.models import F, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.views import View

from api.models import Menu_Auth, MenuMaster, UserMaster, ColumnMaster
from api.serializers import ColumnSerializer


def getLmenuList(request):
    user_id = request.GET.get('user_id')
    client = request.GET.get('client')
    qs = MenuMaster.objects.filter(menuauth__enterprise=client
                                   , menuauth__user=user_id
                                   , menuauth__use_flag='Y'
                                   , menuauth__del_flag='N'
                                   , menuauth__parent_id=0
                                   ).annotate(alias=Coalesce('menuauth__alias', F('name'))
                                              # ).annotate(alias=F('menuauth__alias')
                                              ).values('id', 'code', 'alias', 'path', 'type', 'comment', 'i_class'
                                                       , 'created_by_id', 'created_at', 'updated_by_id', 'updated_at'
                                                       , 'del_flag').order_by('menuauth__order')

    qs_json = list(qs)

    context = {}
    context['results'] = qs_json
    return JsonResponse(context)


def getSubMenuList(request):
    menutype = ['S']
    try:
        userId = request.GET.get('user_id')

        enterpriseId = request.GET.get('client')
        parent_id = request.GET.get('parent_id')
    except KeyError:
        userId = None

    if userId:
        user = UserMaster.objects.get(id=userId)

    if user.is_superuser:
        menutype.append('M')

    if enterpriseId:
        enterprise = enterpriseId
    else:
        enterprise = request.COOKIES['enterprise_id']

    if parent_id:
        parent = parent_id
    else:
        parent = 0

    qs = MenuMaster.objects.filter(menuauth__enterprise=enterprise
                                   , menuauth__user=user
                                   , menuauth__parent_id=parent
                                   , menuauth__del_flag='N'
                                   , type__in=menutype
                                   ).annotate(alias=Coalesce('menuauth__alias', F('name'))
                                              ).values('id', 'code', 'alias', 'path', 'type', 'comment', 'i_class'
                                                       , 'created_by_id', 'created_at', 'updated_by_id', 'updated_at'
                                                       , 'del_flag').order_by('menuauth__order').distinct()

    ql = MenuMaster.objects.filter(type__in=menutype)

    # 직렬화된 JSON 문자열로 변환 (인코딩 설정-한글깨짐방지)

    qs_json = list(qs)
    ql_json = serializers.serialize('json', ql)
    ql_json = ql_json.encode('utf-8').decode('unicode_escape')
    ql_json = json.dumps(json.loads(ql_json), ensure_ascii=False)
    context = {}
    context['usesubmenu'] = qs_json
    context['allsubmenu'] = ql_json

    return JsonResponse(context)


class Menuauth(View):
    queryset = Menu_Auth.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        qs = Menu_Auth.objects.all()
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        menulist = request.POST.getlist('menuid[]', '')
        aliaslist = request.POST.getlist('alias[]', '')
        userId = request.POST.get('user_id', '')
        client = request.POST.get('client', '')
        parentId = request.POST.get('parent_id', '')

        user = UserMaster.objects.get(id=request.COOKIES['user_id'])

        if not parentId:
            parentId = 0  # 대메뉴이기 때문에 0으로 고정
            cnt = 100
            auto = 100
        else:
            orders = self.get_queryset().filter(menu_id=parentId, user_id=userId).values('order').first()
            if orders:
                cnt = orders['order'] + 5

            auto = 5

        # 등록되어있는 메뉴들을 삭제한다.

        self.get_queryset().filter(use_flag='Y', parent_id=parentId,
                                   enterprise_id=client, user_id=userId).delete()

        for index, unit in enumerate(menulist):
            alias = aliaslist[index] if index < len(aliaslist) else None

            authObj = Menu_Auth.objects.create(
                menu_id=unit,
                alias=alias,
                enterprise_id=client,
                user_id=userId,
                order=cnt,
                parent_id=parentId,
                use_flag='Y',
                del_flag='N',
                created_by=user,
                created_at=user,
                updated_by=user,
                updated_at=user
            )

            cnt += auto

        return JsonResponse({'success': True}, status=status.HTTP_200_OK)


class CustomPagination(PageNumberPagination):
    page_size = 1000  # 페이지당 가져올 항목 수


class columnViewSet(viewsets.ModelViewSet):
    queryset = ColumnMaster.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    serializer_class = ColumnSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        menu_id = self.request.query_params['menu_id']
        qs = ColumnMaster.objects.filter(Q(menu__menuauth__enterprise_id=self.request.COOKIES['enterprise_id']) &
                                         Q(menu__menuauth__user_id=self.request.COOKIES['user_id']) &
                                         Q(menu=menu_id) &
                                         Q(use_flag=True)
                                         ).select_related('menu').annotate(code=F('menu__code')).order_by('position')

        # qs = qs.filter(visual_flag=True)

        return qs

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, request, *args, **kwargs)

    def paginate_queryset(self, queryset):
        """
        페이지네이션을 수행하여 요청된 페이지의 항목을 반환합니다.
        """
        if self.paginator is None:
            return None

        return self.paginator.paginate_queryset(queryset, self.request, view=self)
