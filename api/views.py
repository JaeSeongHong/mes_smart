import time
import traceback

import requests
import speech_recognition as sr
import pyaudio
import numpy as np

from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from api.models import SensorH2Value, Process, Subprocess, CodeMaster, ItemMaster


@csrf_exempt
def checkIn(request):
    context = '<xml>'
    context += '<root>'
    context += '<ack>ok</ack>'
    context += '<timestamp>' + str(int(time.time())) + '</timestamp>'
    context += '<offset-ch1>' + '0.0' + '</offset-ch1>'
    context += '<offset-ch2>' + '0.0' + '</offset-ch2>'
    context += '<sample-mode>' + '0.0' + '</sample-mode>'
    context += '</root>'
    context += '</xml>'

    return HttpResponse(context)


'''
    mac : 장치의 mac 어드레스를 의미합니다.
    sig :  WIFI 신호 세기로 RSSI값입니다. (dbm) : 0 번부터 -150까지 가능하고 -70이상이면 좋은 상태입니다.
    bat : RN400의 배터리 상태 정보입니다.  0~255 값이 가능하고, 5가 되면 배터리 교체가 필요합니다.
          값이 -1 인경우는 DC 전원을 공급하고 있는 경우 입니다.
    volt : 현재 배터리 정보를 전달합니다. <battery type>|<current voltage>
           <Battery Type> 0: 1.5V X 2EA , 1: 3.6V X 1 EA |  <Current Voltage> 2.95
    SMODEL: RN400의 상세 모델 번호를 전달합니다. RN400H2EX
    Cxxx :  센서의 정보를 보내줍니다. 
            C000 = 타임스탬프 | Ch.1(온도) | Ch.2 | Ch.3 | Ch.4
    Pxxx  :  센서의 정보를 보내줍니다. <timestamp>|<ch1센서값>|<ch2센서값|<ch3센서값>|......
    * 센서값: NULL : 센서없음.
'''


@csrf_exempt
def dataIn(request):
    print(request.POST)

    # Get Sensor Info
    mac = request.POST['mac']
    bat = request.POST['bat']
    volt = str(request.POST['volt']).split('|')
    batteryType = volt[0]
    currentVoltage = volt[1]
    SMODEL = request.POST['SMODEL']

    try:
        C000 = str(request.POST['C000']).split('|')

        timestamp = float(C000[0])
        ch1 = C000[1]
        ch2 = C000[2]
        doorContact = C000[3]
        LoadDC30V1A = C000[4]

        print('mac', mac)
        print('bat', bat)

        print('batteryType', batteryType)
        print('currentVoltage', currentVoltage)

        print('SMODEL', SMODEL)

        from datetime import datetime
        print('timestamp', datetime.fromtimestamp(timestamp))
        print('ch1', ch1)
        print('ch2', ch2)
        print('doorContact', doorContact)
        print('LoadDC30V1A', LoadDC30V1A)

        # DB 기록
        if ch1 == 'NULL':
            nCh1 = 0
        else:
            nCh1 = float(ch1)

        if ch2 == 'NULL':
            nCh2 = 0
        else:
            nCh2 = float(ch2)

        obj = SensorH2Value.objects.create(mac=mac,
                                           temp=nCh1,
                                           hue=nCh2,
                                           fetch_datetime=datetime.fromtimestamp(timestamp),
                                           )


    except Exception as e:
        print('SensorH2 ', mac, ' , Exception ', e)

    context = '<xml>'
    context += '<root>'
    context += '<ack>ok</ack>'
    context += '</root>'
    context += '</xml>'

    return HttpResponse(context)


@csrf_exempt
def getVolt(request):
    print(request.POST)

    # Get Sensor Info
    subprocess_id = request.POST['subprocess']

    try:
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print('subprocess:', subprocess_id)

        # DB 기록

        subprocess = Subprocess.objects.get(id=subprocess_id)
        process = subprocess.process

        if subprocess:
            # TODO: 생산수량 초과해도 등록은 가능해야함
            # print(subprocess.id)
            # if subprocess.complete_amount == subprocess.amount:
            #     print("생산수량을 초과했습니다")
            #     try:
            #         requests.get('http://192.168.0.222/getprocess?subprocess_id=' + subprocess_id, timeout=3)
            #
            #     except Exception as e:
            #         process.is_connection = False
            #         process.save()
            #
            #     context = '<xml>'
            #     context += '<root>'
            #     context += '<ack>ok</ack>'
            #     context += '</root>'
            #     context += '</xml>'
            #
            #     return HttpResponse(context)

            # 2번 신호가 들어왔을 때 한개의 카운트가 되도록 해야함
            if subprocess.complete_check == 0:
                subprocess.complete_check += 1

            else:
                subprocess.complete_amount += 1
                print(subprocess.complete_amount)
                subprocess.remain_amount = subprocess.amount - subprocess.complete_amount
                subprocess.complete_check = 0

            subprocess.save()

    except Exception as e:
        print('product_name ', subprocess_id, ' , Exception ', e)
        print(traceback.format_exc())

    context = '<xml>'
    context += '<root>'
    context += '<ack>ok</ack>'
    context += '</root>'
    context += '</xml>'

    return HttpResponse(context)


# def sendSubProcessInfo(request):
#     print(request.GET)
#
#     # 연동 중인 것이 있을 경우 리턴
#     subprocess_id = request.GET['subprocess_id']
#     enterprise_id = 0
#
#     row = Subprocess.objects.get(id=subprocess_id)
#     if row:
#         enterprise_id = row.enterprise_id
#     else:
#         enterprise_id = 0
#
#     if enterprise_id != 0:
#         qs = Process.objects.filter(enterprise_id=enterprise_id)
#         qs = qs.filter(is_connection=True)
#         if qs:
#             a = 1
#
#
#     requests.get('http://192.168.0.222/getprocess?subprocess_id=' + request.GET['subprocess_id'], timeout=3)
#
#     context = '<xml>'
#     context += '<root>'
#     context += '<ack>ok</ack>'
#     context += '</root>'
#     context += '</xml>'
#
#     return HttpResponse(context)


def sendSubProcessInfo(request):
    print(request.GET)
    context = {}

    # 연동 중인 것이 있을 경우 리턴
    subprocess_id = request.GET['subprocess_id']
    process_id = request.GET['process_id']
    process = None

    if subprocess_id == '':
        # 연동 중지
        # pass
        process = Process.objects.get(id=process_id)
        if process:
            pre = Subprocess.objects.filter(process=process)
            if pre:
                pre_last = pre.last()
                pre_last.is_connection = True
                pre_last.save()

    else:
        enterprise_id = 0
        row = Subprocess.objects.get(id=subprocess_id)

        if row:
            enterprise_id = row.enterprise_id
        else:
            enterprise_id = 0

        if enterprise_id == 0:
            pass

        else:
            qs = Process.objects.filter(enterprise_id=enterprise_id)
            qs = qs.filter(is_connection=True)
            row.is_connection = True
            if qs:
                # 연동중이 있는 경우
                context['result'] = 'connecting'
                return JsonResponse(context)

    try:
        # requests.get('http://192.168.0.222/getprocess?subprocess_id=' + subprocess_id, timeout=3)
        requests.get('http://1.215.87.131:8239/getprocess?subprocess_id=' + subprocess_id, timeout=3)

        context['result'] = 'ok'
        return JsonResponse(context)
    except Exception as e:
        print(e)
        print(traceback.format_exc())

        if process:
            process.is_connection = False
            process.save()

        context['result'] = 'error'
        return JsonResponse(context)


from dal import autocomplete


class CodeAutoComplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = ItemMaster.objects.filter(
            enterprise__name=self.request.COOKIES['enterprise_name'],
        )

        if self.q:
            qs = qs.filter(name__contains=self.q).order_by('-id')

        return qs


def getAlivecheck(request):
    try:
        response = requests.get('http://192.168.0.125:8254/common/alive-check')
        print(response)
    except requests.exceptions.RequestException as e:
        print('요청 예외가 발생했습니다:', e)

    return JsonResponse({'results': str(response)})

    # if response.status_code == 200:
    #    data = response.json()
    #    print(data)
    #    return JsonResponse({'message': 'success', 'data': data})
    # else:
    #    print('Error:', response.status_code)


def recognize(request):
    CHUNK = 1024  # 음성 데이터를 처리할 단위 크기
    RATE = 44100  # 샘플링 레이트 (Hz)
    RECORD_SECONDS = 5  # 음성 데이터를 수집할 시간

    # PyAudio 객체 생성
    audio = pyaudio.PyAudio()

    # 마이크 입력 스트림 열기
    stream = audio.open(format=pyaudio.paInt16, channels=2, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("음성인식을 시작합니다.")

    # RECORD_SECONDS 동안 마이크에서 입력받은 음성데이터를 출력
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        decoded = np.frombuffer(data, dtype=np.int16)
        print(decoded)

    print("음성인식이 종료되었습니다.")

    # 스트림과 객체 닫기
    stream.stop_stream()
    stream.close()
    audio.terminate()

    return JsonResponse({'results': str(decoded)})


# 마이크로부터 스트림을 읽어오는 함수
def get_audio_input_stream(self):
    stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    return stream


# 음성인식을 수행하는 함수
def recognize_speech(self):
    with self.get_audio_input_stream() as stream:
        # 마이크로부터 입력된 오디오 스트림을 실시간으로 읽어와 Recognizer 객체의 record() 함수에 전달
        audio_data = self.r.record(stream, duration=5)  # 5초간 음성 입력을 받음

    # 구글 음성인식 API를 사용하여 음성을 텍스트로 변환
    try:
        text = self.r.recognize_google(audio_data, language='ko-KR')
        print("인식 결과:", text)
    except sr.UnknownValueError:
        print("음성을 인식할 수 없습니다.")
    except sr.RequestError as e:
        print("구글 음성인식 API에 접근할 수 없습니다. {0}".format(e))

    return JsonResponse({'results': str(text)})
