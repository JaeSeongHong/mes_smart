import json
import os

import requests

from KPI.kpi_level import level2, headers, level1_op, level3
from api.models import Process, Subprocess

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seoulsoft_mes.settings")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from datetime import date, timedelta
from django.db.models import Sum, F, FloatField, Avg, ExpressionWrapper
from django.db.models.functions import Coalesce, ExtractDay

goal = {
    "production": 1000,
    "onTime": 3  # 감소는 현재 기준
}
recent = {
    "production": 500,
    "onTime": 30
}


def login_yu_seong_level3(enterprise_name, companyCode):
    try:
        url = "http://www.ssf-kpi.kr:8080" \
              "/kpiTot/kpiCertKeySelect"
        body = {"schBrn": companyCode}

        res = requests \
            .post(url,
                  headers=headers,
                  data=json
                  .dumps(body,
                         ensure_ascii=False,
                         indent="\t")
                  .encode('utf-8')
                  )
        data = json.loads(res.text)
        # print("response text %r" % res.text)

        kpiCertKey = data[0]['kpiCertKey']

        if kpiCertKey != "":
            level3P_yu_seong(enterprise_name,kpiCertKey)  # 생산성
            level3D_yu_seong(enterprise_name, kpiCertKey)

    except Exception as ex:
        print("login_yu_seong_level3 Exception")
        print(ex)


def login_yu_seong_level2(enterprise_name, companyCode):
    try:
        url = "http://www.ssf-kpi.kr:8080" \
              "/kpiTot/kpiCertKeySelect"
        body = {"schBrn": companyCode}

        res = requests \
            .post(url,
                  headers=headers,
                  data=json
                  .dumps(body,
                         ensure_ascii=False,
                         indent="\t")
                  .encode('utf-8')
                  )
        data = json.loads(res.text)
        # print("response text %r" % res.text)

        kpiCertKey = data[0]['kpiCertKey']

        if kpiCertKey != "":
            level2P_yu_seong(enterprise_name,kpiCertKey)  # 생산성
            level2D_yu_seong(enterprise_name, kpiCertKey)

    except Exception as ex:
        print("login_yu_seong_level2 Exception")
        print(ex)


def login_yu_seong_level1(enterprise_name, companyCode):
    try:
        url = "http://www.ssf-kpi.kr:8080" \
              "/kpiTot/kpiCertKeySelect"
        body = {"schBrn": companyCode}

        res = requests \
            .post(url,
                  headers=headers,
                  data=json
                  .dumps(body,
                         ensure_ascii=False,
                         indent="\t")
                  .encode('utf-8')
                  )
        data = json.loads(res.text)
        # print("response text %r" % res.text)

        kpiCertKey = data[0]['kpiCertKey']

        if kpiCertKey != "":
            level1_op(enterprise_name, kpiCertKey, 37)  # 37 사용 Table 수

    except Exception as ex:
        print("login_yu_seong_level1 Exception")
        print(ex)


def level2P_yu_seong(enterprise_name, kpiCertKey):
    yesterday = date.today() - timedelta(1)
    _year = yesterday.strftime('%Y')
    _month = yesterday.strftime('%m')
    _day = yesterday.strftime("%d")
    qs_result = {}
    qs_day_amount = goal["production"]
    try:
        # 월별
        qs_process_complete = Process.objects \
            .filter(enterprise__name=enterprise_name,
                    complete=True,
                    updated_at__year=_year,
                    updated_at__month=_month,
                    updated_at__day=_day)
        if qs_process_complete:
            amount = qs_process_complete \
                .aggregate(sum=Coalesce(
                    Sum("amount"), 0))
            qs_day_amount = amount['sum']
        qs_result = {
            "kpiCertKey": kpiCertKey,
            "ocrDttm": str(yesterday),
            "kpiFldCd": "P",
            "kpiDtlCd": "B",
            "kpiDtlNm": "생산량 증가",
            "achrt": round( (qs_day_amount - recent["production"]) / recent["production"] * 100,3),
            "trsDttm": str(date.today())
        }
        level2({"KPILEVEL2": [qs_result]})

    except Exception as ex:
        print("level2P_yu_seong Exception")
        print(ex)


def level2D_yu_seong(enterprise_name, kpiCertKey):
    yesterday = date.today() - timedelta(1)
    _year = yesterday.strftime('%Y')
    _month = yesterday.strftime('%m')
    _day = yesterday.strftime("%d")
    qs_result = {}
    onTimeAmount = goal["onTime"]
    try:
        # 월별
        qs_process_complete = Process.objects \
            .filter(enterprise__name=enterprise_name,
                    complete=True,
                    updated_at__year=_year,
                    updated_at__month=_month,
                    updated_at__day=_day)
        if qs_process_complete:
            amount = qs_process_complete \
                .annotate(on_time_day=Coalesce(ExtractDay(F("to_date"))
                                      - ExtractDay(F('actual_to_date'))
                                      + 1,1))\
                .aggregate(Avg("on_time_day"))
            onTimeAmount = amount["on_time_day_Avg"]
        qs_result = {
            "kpiCertKey": kpiCertKey,
            "ocrDttm": str(yesterday),
            "kpiFldCd": "D",
            "kpiDtlCd": "G",
            "kpiDtlNm": "납기준수율",
            "achrt": round( (recent["onTime"] - onTimeAmount)/recent["onTime"] * 100,3),
            "trsDttm": str(date.today())
        }
        level2({"KPILEVEL2": [qs_result]})

    except Exception as ex:
        print("level2D_yu_seong Exception")
        print(ex)


def level3P_yu_seong(enterprise_name, kpiCertKey):
    yesterday = date.today() - timedelta(1)
    _year = yesterday.strftime('%Y')
    _month = yesterday.strftime('%m')
    _day = yesterday.strftime("%d")
    qs_result = {}
    qs_day_amount = goal["production"]
    try:
        # 월별
        qs_process_complete = Process.objects \
            .filter(enterprise__name=enterprise_name,
                    complete=True,
                    updated_at__year=_year,
                    updated_at__month=_month,
                    updated_at__day=_day)
        if qs_process_complete:
            amount = qs_process_complete \
                .aggregate(sum=Coalesce(
                    Sum("amount"), 0))
            qs_day_amount = amount['sum']
        qs_result = {
            "kpiCertKey": kpiCertKey,
            "ocrDttm": str(yesterday),
            "kpiFldCd": "P",
            "kpiDtlCd": "B",
            "kpiDtlNm": "생산량",
            "msmtVl": qs_day_amount,
            "unt": "ea/일",
            "trsDttm": str(date.today())
        }
        level3({"KPILEVEL3": [qs_result]})

    except Exception as ex:
        print("level3P_yu_seong Exception")
        print(ex)


def level3D_yu_seong(enterprise_name, kpiCertKey):
    yesterday = date.today() - timedelta(1)
    _year = yesterday.strftime('%Y')
    _month = yesterday.strftime('%m')
    _day = yesterday.strftime("%d")
    qs_result = {}
    onTimeAmount = goal["onTime"]
    try:
        # 월별
        qs_process_complete = Process.objects \
            .filter(enterprise__name=enterprise_name,
                    complete=True,
                    updated_at__year=_year,
                    updated_at__month=_month,
                    updated_at__day=_day)
        if qs_process_complete:
            amount = qs_process_complete \
                .annotate(on_time_day=Coalesce(ExtractDay(F("actual_to_date"))
                                      - ExtractDay(F('to_date'))
                                      + 1,1)) \
                .filter(on_time_day__gte=1) \
                .aggregate(AvgTime=Avg(F("on_time_day")))
            onTimeAmount = amount["AvgTime"]
        qs_result = {
            "kpiCertKey": kpiCertKey,
            "ocrDttm": str(yesterday),
            "kpiFldCd": "D",
            "kpiDtlCd": "B",
            "kpiDtlNm": "리드타임감소",
            "msmtVl": onTimeAmount,
            "unt": "일",
            "trsDttm": str(date.today())
        }
        level3({"KPILEVEL3": [qs_result]})

    except Exception as ex:
        print("level3D_yu_seong Exception")
        print(ex)
