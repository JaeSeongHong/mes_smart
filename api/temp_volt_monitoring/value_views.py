from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter, DateFilter
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import CodeMaster, CustomerMaster, RentalMaster, Rental, Sensor, SensorValue, SensorPCValue, SensorPC
from api.permission import MesPermission
from api.serializers import CodeMasterSerializer, RentalMasterSerializer, RentalSerializer, SensorSerializer, \
    SensorValueSerializer, SensorPCValueSerializer
from api.temp_volt_monitoring.send_mail import send_gmail


class SensorPCValueViewSet(viewsets.ModelViewSet):
    class SensorPCValueFilter(FilterSet):
        created_at = DateFilter()
        created_at_range = DateFromToRangeFilter('created_at')

        class Meta:
            model = SensorPCValue
            fields = ['master__factory__id', 'master__company__id', 'created_at', 'created_at_range']

    queryset = SensorPCValue.objects.all()
    serializer_class = SensorPCValueSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get']     # to remove 'put'
    filter_backends = [DjangoFilterBackend]
    filterset_class = SensorPCValueFilter
    pagination_class = None

    def get_queryset(self):
        return SensorPCValue.objects.filter(master__enterprise=self.request.user.enterprise).all()


class SensorPCValueBPViewSet(viewsets.ModelViewSet):

    queryset = SensorPCValue.objects.all()
    serializer_class = SensorPCValueSerializer
    permission_classes = []
    http_method_names = ['post']     # to remove 'put'

    def get_queryset(self):
        return SensorPCValue.objects.filter(master__enterprise=self.request.user.enterprise).all()

    def create(self, request, *args, **kwargs):
        serial = request.data.get('serial', None)
        temp = float(request.data.get('temp', 0))
        voltage = float(request.data.get('voltage', 0))
        voltage3 = float(request.data.get('v33', 0))
        voltage5 = float(request.data.get('v5', 0))
        voltage12 = float(request.data.get('v12', 0))
        spc = SensorPC.objects.filter(serial=serial).first()
        if spc is None:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        spcv = SensorPCValue(master=spc, temp=temp, voltage=voltage, voltage3=voltage3,
                             voltage5=voltage5, voltage12=voltage12, fetch_datetime=datetime.now())
        spcv.save()

        if spc.alert != 'true':
            return Response({}, status=status.HTTP_201_CREATED)

        abnormal_temp = False
        abnormal_voltage = False
        abnormal_voltage_3v = False
        abnormal_voltage_5v = False
        abnormal_voltage_12v = False

        if spc.temp_threshold_low and spc.temp_threshold_high:
            abnormal_temp = (spc.temp_threshold_low > temp or temp > spc.temp_threshold_high)

        if spc.voltage_threshold_low and spc.voltage_threshold_high:
            abnormal_voltage = (spc.voltage_threshold_low > voltage or voltage > spc.voltage_threshold_high)

        if spc.voltage_3v_threshold_low and spc.voltage_3v_threshold_high:
            abnormal_voltage_3v = (spc.voltage_3v_threshold_low > voltage3 or voltage3 > spc.voltage_3v_threshold_high)

        if spc.voltage_5v_threshold_low and spc.voltage_5v_threshold_high:
            abnormal_voltage_5v = (spc.voltage_5v_threshold_low > voltage5 or voltage5 > spc.voltage_5v_threshold_high)

        if spc.voltage_12v_threshold_low and spc.voltage_12v_threshold_high:
            abnormal_voltage_12v = (spc.voltage_12v_threshold_low > voltage12 or voltage12 > spc.voltage_12v_threshold_high)

        subject, body = "", ""
        # 온도 전압 이상 시
        # if (abnormal_voltage | abnormal_voltage_3v | abnormal_voltage_5v | abnormal_voltage_12v) and abnormal_temp:
        #     subject = spc.name + "에서 온도 전압 이상 발생!"
        #     body = spc.name + "에서 온도 전압 이상 발생!"
        # elif abnormal_voltage | abnormal_voltage_3v | abnormal_voltage_5v | abnormal_voltage_12v:
        #     subject = spc.name + "에서 전압 이상 발생!"
        #     body = spc.name + "에서 전압 이상 발생!"

        if abnormal_voltage_3v | abnormal_voltage_5v | abnormal_voltage_12v:
            subject = spc.name + "에서 전압 이상 발생 "

            if abnormal_voltage_3v:
                body = spc.name + "3.3V 전압: " + str(voltage3) + "이상 발생!" + "\n"

            if abnormal_voltage_5v:
                body += spc.name + "5V 전압: " + str(voltage5) + "이상 발생!" + "\n"

            if abnormal_voltage_12v:
                body += spc.name + "12V 전압: " + str(voltage12) + "이상 발생!" + "\n"

        if abnormal_temp:
            subject += spc.name + "에서 온도 이상 발생!"
            body += spc.name + "에서 온도: " + str(temp) + "이상 발생!"

        else:
            return Response({}, status=status.HTTP_201_CREATED)


        for mail in [spc.admin_email_1, spc.admin_email_2]:
            mail_info = dict(gmail_user='ssmesdev@gmail.com',
                             gmail_password='mes_developer1',
                             send_to=mail, subject=subject, body=body)

            send_gmail(mail_info, None)

        return Response({}, status=status.HTTP_201_CREATED)
