from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import time

'''
url을 받는 위치는 필요에 의해 배치하고 기능을 연결하시면 됩니다.
현재는 테스트 용으로 사용 중 입니다.
'''

@csrf_exempt
def qrItemIn(request):

    print(request.GET)

    context = '<xml>'

    for tmp in request.GET:
        context += tmp

    context += '<ack>ok</ack>'
    context += '<timestamp>' + str(int(time.time())) + '</timestamp>'
    context += '</xml>'

    return HttpResponse(context)
