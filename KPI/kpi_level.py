import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seoulsoft_mes.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import json
import requests
from datetime import date, timedelta

headers = {'Content-Type': 'application/json', 'charset': 'UTF-8', 'Accept': '*/*'}


def level1_op(enterprise_name, kpiCertKey, tableCnt):  # 레벨1 운영성과 등록
    try:
        url = "http://www.ssf-kpi.kr:8080/kpiLv1/kpiLv1Insert"
        # print("level1_op %r" % url)
        today = date.today()

        body = {
            "KPILEVEL1": [
            {"kpiCertKey": kpiCertKey, "trsDttm": str(today),
            "ocrDttm": str(today), "systmOprYn": "Y" }
            ]
        }

        res = requests.post(url, headers=headers,
                            data=json.dumps(body, ensure_ascii=True, indent="\t").encode('utf-8'))
        status = res.status_code
        # print(status)
        if status == 200:
            # print("sucess level1")
            pass

    except Exception as ex:
        print(ex)


def level2(body):

    try:
        # print(body)
        url = "http://www.ssf-kpi.kr:8080/kpiLv2/kpiLv2Insert"
        # print("level2_p1 %r" % url)

        res = requests.post(url, headers=headers, data=json.dumps(body, ensure_ascii=True, indent="\t").encode('utf-8'))
        # print("response text %r" % res.text)

        status = res.status_code
        if status == 200:
            pass
            # print("sucess level2")

    except Exception as ex:
        print(ex)

def level3(body):

    try:
        url = "http://www.ssf-kpi.kr:8080/kpiLv3/kpiLv3Insert"
        # print("level3_p1 %r" % url)

        res = requests.post(url, headers=headers,
                            data=json.dumps(body, ensure_ascii=True, indent="\t").encode('utf-8'))
        # print("response text %r" % res.text)

        status = res.status_code
        # print("level3", status)
        if status == 200:
            pass
            # print("sucess level3")

    except Exception as ex:
        print(ex)