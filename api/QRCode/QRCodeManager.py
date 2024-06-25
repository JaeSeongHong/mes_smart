import io
import os
import random
import time
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
import PIL

from django.http import HttpResponse
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage

from seoulsoft_mes.settings import MEDIA_URL

'''
qrcode 설치 필요 (7.2버전, requirements.txt 참고)
적용 sample 
class ItemInViewSet(viewsets.ModelViewSet):
'''

def QRCodeGen (dict, categoris, path=None):
    # categoris는 사용할 API주소를 분리하기 위하여 사용한다.
    # 예를들면 입고처리인 경우 import 와 같이 정의하여 사용하면 된다.

    # dict 구조로 url에 파라미터로 사용될 key 와 value를 담는다.

    # path 값이 넘어온 경우 기존파일 삭제 후 생성

    if path is not None:
        if default_storage.exists(path):
            default_storage.delete(path)

    # server_url = "http://127.0.0.1:8000/"
    server_url = MEDIA_URL
    url = server_url + "qrcode/" + categoris + "/?"

    # get방식으로 dict 정리
    for key in dict:
        valueToStr = str(dict[key])
        url += key + "=" + valueToStr
        url += "&"

    print(url)
    qrcode_imgFile = qrcode.make(url)

    # PIL 이미지 변환
    im_resize = qrcode_imgFile.resize((qrcode_imgFile.pixel_size, qrcode_imgFile.pixel_size))
    buf = io.BytesIO()
    im_resize.save(buf, format='PNG')
    byte_im = buf.getvalue()

    filename = str(int(time.time())) + '.png'
    path = default_storage.save('uploads/qrcodeIMG/' + filename, ContentFile(byte_im))

    return filename


def QRCodeGen_Code (code, path=None):
    # categoris는 사용할 API주소를 분리하기 위하여 사용한다.
    # 예를들면 입고처리인 경우 import 와 같이 정의하여 사용하면 된다.

    # dict 구조로 url에 파라미터로 사용될 key 와 value를 담는다.

    # path 값이 넘어온 경우 기존파일 삭제 후 생성

    if path is not None:
        if default_storage.exists(path):
            default_storage.delete(path)

    qrcode_imgFile = qrcode.make(code)

    # PIL 이미지 변환
    im_resize = qrcode_imgFile.resize((qrcode_imgFile.pixel_size, qrcode_imgFile.pixel_size))
    buf = io.BytesIO()
    im_resize.save(buf, format='PNG')
    byte_im = buf.getvalue()

    filename = str(int(time.time())) + '.png'
    path = default_storage.save('uploads/qrcodeIMG/' + filename, ContentFile(byte_im))

    return filename


def BarcodeGen(code, path=None):
    if path is not None:
        if default_storage.exists(path):
            default_storage.delete(path)

    barcode_img = Code128(code, writer=ImageWriter())

    barcode_imgfile = barcode_img.save('barcode')
    resize_barocde = Image.open('barcode.png')

    newSize = (500, 500)  # new size will be 500 by 300 pixels, for example

    im_resize = resize_barocde.resize(newSize, resample=PIL.Image.NEAREST)
    buf = io.BytesIO()
    im_resize.save(buf, format='PNG')
    byte_im = buf.getvalue()

    filename = str(int(time.time())) + '.png'
    path = default_storage.save('uploads/qrcodeIMG/' + filename, ContentFile(byte_im))

    return filename


def DeleteQRCode (_filename):
    # path 값이 넘어온 경우 기존파일 삭제 후 생성
    path = 'uploads/qrcodeIMG/' + _filename

    if (_filename != '' and _filename != None ):
        if default_storage.exists(path):
            default_storage.delete(path)

def QRCodeTestURL(request):
    print(request.GET)

    context = '<xml>'

    for tmp in request.GET:
        context += tmp

    context += '<ack>ok</ack>'
    context += '<timestamp>' + str(int(time.time())) + '</timestamp>'
    context += '</xml>'

    dict_qr = {'id': 0, 'item': 'item'}
    QRCodeGen(dict_qr, 'ItemIn')

    return HttpResponse(context)


