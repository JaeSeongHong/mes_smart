import datetime
import threading

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seoulsoft_mes.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from KPI.KPI_2022.do_yu_seong import login_yu_seong_level1, login_yu_seong_level2, login_yu_seong_level3


import time


def KPICALL():
    class Worker(threading.Thread):
        def __init__(self, name):
            super().__init__()
            self.name = name  # thread 이름 지정

        def run(self):
            print("sub thread start ", threading.currentThread().getName())
            kpi_main()
            print("sub thread end ", threading.currentThread().getName())


    def kpi_do():
        # 업체별 KPI 수행
        _today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        login_yu_seong_level1("유성산업",
                              "1391069096")

        login_yu_seong_level2("유성산업",
                              "1391069096")

        login_yu_seong_level3("유성산업",
                              "1391069096")

        print("kpi_do in : today = ", _today)

        # hjlim 시간 될때 do_업체.py 각각의 날짜 지정에, 시간을 여기서 세팅하도록 함수 재설정
        # yesterday = date.today() - timedelta(1)


    def kpi_main():

        complete = False

        while True:
            this_time = datetime.datetime.now().strftime('%H')
            print("check kpi, %H:", this_time, ", complete:", complete)

            # 매일 한시에 실행 Start
            # if ( (this_time == '01') and (complete == False)):
            #     complete = True
            #     kpi_do()
            #
            # elif (this_time != '01'):
            #     complete = False
            #
            # time.sleep(15*60)
            # 매일 한시에 실행 End

            # 6시간마다 전송
            kpi_do()
            time.sleep(24 * 60 * 60)

    # kpi_main()
    t = Worker("kpi")
    t.daemon = False  # sub thread 생성
    t.start()
    print("main thread init")

