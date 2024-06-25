import pandas as pd

from datetime import datetime

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.bom.excel import excel_parser
from api.models import CustomerMaster, CodeMaster, ItemMaster, BomMaster
from api.serializers import BomSerializer, ItemMasterSerializer, CustomerMasterSerializer, CodeMasterSerializer


def excel_basic_customer_parser(path):
    """CustomerMaster 위한 엑셀 파서. 필드만 파싱하여 a list of dictionary 반환. 이후 FK에 대한 매핑 해줘야 함."""
    df = pd.read_excel(path)

    # Retrieve data
    items = []
    for i, row in df.iloc[:].iterrows():
        fields = ('code', 'name', 'owner_name', 'business_conditions', 'business_event', 'office_phone', 'office_fax', 'email', )
        item = {}
        for idx, field in enumerate(fields):
            item[field] = row.iloc[idx]

        items.append(item)

    return items


class CustomerExcelView(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, ]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        excel = request.FILES['excel']

        base = 'data/'
        prefix = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
        path = base + prefix + excel.name
        with open(path, 'wb+') as f:
            for chunk in excel.chunks():
                f.write(chunk)

        items = excel_basic_customer_parser(path)
        insert = []
        for idx, item in enumerate(items):
            one = {}
            for k, v in item.items():
                one[k] = v

            insert.append(one)

        cms = CustomerMasterSerializer(data=insert, many=True, context={'request': request})
        cms.is_valid(raise_exception=True)
        cms.save()

        return Response(status=status.HTTP_200_OK)
