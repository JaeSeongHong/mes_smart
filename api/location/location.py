from django.db.models import F, Sum

from KPI.kpi_views import kpi_log
from api.models import ItemIn, ItemOut, ItemMaster, CodeMaster, GroupCodeMaster

from django.db import transaction
from django.http import JsonResponse
from django.views import View
from rest_framework.permissions import IsAuthenticated
from api.permission import MesPermission
from api.serializers import ItemMasterSerializer


class LocationItemCalculateView(View):
    permission_classes = [IsAuthenticated, MesPermission]

    def get(self, request, *args, **kwargs):
        location_id = GroupCodeMaster.objects.all().filter(code=107,
                                                           enterprise__name=request.COOKIES['enterprise_name'])
        locations = CodeMaster.objects.all().filter(group_id__in=location_id)
        item = request.GET.get('item', "")
        if item == "":
            context = []
            items = ItemMaster.objects.all().filter(enterprise__name=request.COOKIES['enterprise_name'])
            for i, item in enumerate(items):
                context.append({})
                context[i] = {}
                context[i]['storage'] = []
                context[i]['total'] = 0;
                total = 0;
                receive_amount = ItemIn.objects.filter(item_id=item.id,
                                                       enterprise__name=request.COOKIES['enterprise_name']).exclude(
                    location_id__in=locations).aggregate(Sum('receive_amount'))
                out_amount = ItemOut.objects.filter(item_id=item.id,
                                                    enterprise__name=request.COOKIES['enterprise_name']).exclude(
                    location_id__in=locations).aggregate(Sum('out_amount'))
                if receive_amount['receive_amount__sum'] == None:
                    receive_amount['receive_amount__sum'] = 0
                if out_amount['out_amount__sum'] == None:
                    out_amount['out_amount__sum'] = 0
                amount = receive_amount['receive_amount__sum'] - out_amount['out_amount__sum']
                total += amount
                context[i]['storage'].append({'location': '입고창고', 'location_id': "", 'amount': amount})
                for location in locations:
                    receive_amount = ItemIn.objects.filter(item_id=item.id,
                                                           enterprise__name=request.COOKIES['enterprise_name'],
                                                           location_id=location.id).aggregate(Sum('receive_amount'))
                    out_amount = ItemOut.objects.filter(item_id=item.id,
                                                        enterprise__name=request.COOKIES['enterprise_name'],
                                                        location_id=location.id).aggregate(Sum('out_amount'))
                    if receive_amount['receive_amount__sum'] == None:
                        receive_amount['receive_amount__sum'] = 0
                    if out_amount['out_amount__sum'] == None:
                        out_amount['out_amount__sum'] = 0
                    amount = receive_amount['receive_amount__sum'] - out_amount['out_amount__sum']
                    total += amount
                    context[i]['storage'].append(
                        {'location': location.name, 'location_id': location.id, 'amount': amount})
                data = ItemMasterSerializer(item).data
                context[i]['item'] = data
                context[i]['total'] = total
            return JsonResponse(context, safe=False)
        else:
            context = {}
            context['result'] = []
            receive_amount = ItemIn.objects.filter(item_id=item,
                                                   enterprise__name=request.COOKIES['enterprise_name']).exclude(
                location_id__in=locations).aggregate(Sum('receive_amount'))
            out_amount = ItemOut.objects.filter(item_id=item,
                                                enterprise__name=request.COOKIES['enterprise_name']).exclude(
                location_id__in=locations).aggregate(Sum('out_amount'))
            if receive_amount['receive_amount__sum'] == None:
                receive_amount['receive_amount__sum'] = 0
            if out_amount['out_amount__sum'] == None:
                out_amount['out_amount__sum'] = 0
            amount = receive_amount['receive_amount__sum'] - out_amount['out_amount__sum']
            context['result'].append({'location': '입고창고', 'location_id': "", 'amount': amount})
            for location in locations:
                receive_amount = ItemIn.objects.filter(item_id=item,
                                                       enterprise__name=request.COOKIES['enterprise_name'],
                                                       location_id=location.id).aggregate(Sum('receive_amount'))
                out_amount = ItemOut.objects.filter(item_id=item, enterprise__name=request.COOKIES['enterprise_name'],
                                                    location_id=location.id).aggregate(Sum('out_amount'))
                if receive_amount['receive_amount__sum'] == None:
                    receive_amount['receive_amount__sum'] = 0
                if out_amount['out_amount__sum'] == None:
                    out_amount['out_amount__sum'] = 0
                amount = receive_amount['receive_amount__sum'] - out_amount['out_amount__sum']
                context['result'].append({'location': location.name, 'location_id': location.id, 'amount': amount})
            return JsonResponse(context, safe=False)
