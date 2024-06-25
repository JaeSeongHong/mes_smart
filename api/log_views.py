from urllib import parse

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime

@csrf_exempt
def write_log(request):

    if request.POST:
        user = request.POST.get('user')
        enterprise = request.POST.get('enterprise')
        file = request.POST.get('file')
        filename = parse.unquote(file)

        now = datetime.datetime.now()
        nowDateTime = now.strftime('%Y-%m-%d %H:%M:%S')

        out = "file download [" + filename + "]  form user[" + user + "], enterprise[" + enterprise + "] at [" + nowDateTime + "]"
        print(out)

    return HttpResponse({})
