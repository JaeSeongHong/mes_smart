import datetime
import requests

from celery import shared_task

from api.models import Sensor, SensorValue
from django.utils.timezone import make_aware

@shared_task
def fetch_sensor_values():
    qs = Sensor.objects.all()
    for sensor in qs:
        try:
            res = requests.get(sensor.api_url)
            if sensor.enterprise.name == '시온테크놀러지':
                items = res.text[1:-1].replace('\"', '').split(',')
                ts = make_aware(datetime.datetime.fromtimestamp(int(items[0])))
                s = SensorValue(master=sensor, temp=int(items[2]) / 10, hue=int(items[1]) / 10, fetch_datetime=ts)
                s.save()
            elif sensor.enterprise.name == 'JA푸드':
                items = res.json()
                ts = make_aware(datetime.datetime.fromtimestamp(int(items['time'])))
                s = SensorValue(master=sensor, temp=float(items['temp']), hue=float(items['hum']), fetch_datetime=ts)
                s.save()
        except:
            continue

