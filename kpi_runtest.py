#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import datetime
import time
from KPI.KPI_2022.do_yu_seong import login_yu_seong_level1, login_yu_seong_level2, login_yu_seong_level3



def kpi_do():
    # 업체별 KPI 수행
    _today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    print("kpi_do in : today = ", _today)

    # hjlim 시간 될때 do_업체.py 각각의 날짜 지정에, 시간을 여기서 세팅하도록 함수 재설정
    # yesterday = date.today() - timedelta(1)

    login_yu_seong_level1("유성산업",
                          "1391069096")

    login_yu_seong_level2("유성산업",
                          "1391069096")

    login_yu_seong_level3("유성산업",
                          "1391069096")

def kpi_main():
    complete = False
    this_time = 100
    while True:
        if this_time == datetime.datetime.now().strftime("%H"):
            complete = False
        if complete == False:
            kpi_do()
            complete = True
            this_time = datetime.datetime.now().strftime('%H')
        print("check kpi, %H:", this_time, ", complete:", complete)
        time.sleep(24 * 60 * 60)  # 24시간마다 전송


if __name__ == '__main__':
    kpi_main()
