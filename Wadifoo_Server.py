# 라이브러리 충돌 방지
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

# GPU 초기화
import torch
import gc
gc.collect()
torch.cuda.empty_cache()

from flask import Flask, redirect, request, Response, render_template, jsonify
import base64
import io

from flask_cors import CORS
from werkzeug.serving import run_simple

import easyocr
import numpy as np
import cv2
import random
import matplotlib.pyplot as plt
from PIL import ImageFont, ImageDraw, Image

import sys
import requests
import urllib.request
import json
from collections import OrderedDict
from time import sleep
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

def configure():
    load_dotenv()

# 파파고 api
def get_translate(text, lan):
    encText = urllib.parse.quote(text)
    data = "source=ko&target="+lan+"&text=" + encText

    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)

    request.add_header("X-Naver-Client-Id", os.getenv('client_id'))
    request.add_header("X-Naver-Client-Secret", os.getenv('client_secret'))
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()

    if(rescode==200):
        response_body = response.read()
        decode = json.loads(response_body.decode('utf-8'))
        res = decode['message']['result']['translatedText']
    else:
        res = ("Error Code:", rescode)

    return res

# 딕셔너리
global dic

# 안드로이드에서 이미지 받아와서 OCR로 메뉴 이름 인식
@app.route("/getImage", methods=['POST']) 
def image():
    configure()
    global dic
    if request.method == 'POST':
        #안드로이드에서 'image'변수에 base64로 변환된 bitmap이미지
        one_data = request.form['image']
        #base64로 인코딩된 이미지 데이터를 디코딩하여 byte형태로 변환
        imgdata = base64.b64decode(one_data)
        #byte형태의 이미지 데이터를 이미지로 변환
        image = Image.open(io.BytesIO(imgdata))
        #이미지 사이즈 조정
        img_resize = image.resize((int(image.width / 2), int(image.height / 2)))
        #EasyOCR에서 이미지를 불러오기 위해 저장
        print("저장 시작")
        img_resize.save('C:/Users/HANSUNG/Image/test.png')
        print("저장 완료")
        # 번역할 언어
        lan = request.form['lang']
        #print(lan)
         #EasyOCR
        #한글과 영어를 인식
        print("인식 시작")
        reader = easyocr.Reader(['ko'], gpu = True)
        #번역할 사진
        result = reader.readtext('C:/Users/HANSUNG/Image/test.png')
        #np.random.seed(42)
        # COLORS = np.random.randint(0, 255, size=(256, 3),dtype="uint8") 
            
        dic = dict()
        korean = []
        translate = []
        top = []
        bottom = []
        textX = []
        textY = []
        for i in result :
            x = i[0][0][0] 
            y = i[0][0][1] 
            w = i[0][1][0] - i[0][0][0] 
            h = i[0][2][1] - i[0][1][1]
            
            color = [0,0,255] # 파란색
            # 번역 결과
            #print("번역 결과 :" + i[1])
            print(i[1])
            trans = get_translate(i[1], lan)
            
            #결과값 리스트에 저장
            korean.append(i[1])
            translate.append(trans)
            top.append(str(x)+","+str(y))
            bottom.append(str(x+w)+","+str(y+h))
            textX.append(str(int(x)+20))
            textY.append(str(y-40))
            
        size=len(korean)

        dic={
            "kor" : korean[0:],
            "trans" : translate[0:],
            "rectangleLeftTop":top[0:],
            "rectangleRightBottom":bottom[0:],
            "textX":textX[0:],
            "textY":textY[0:],
            "size":str(size)
        }
      
    return 'true'

# 결과
@app.route("/deliverImage", methods=['GET'])
def imageSite():
    return jsonify(dic) # json 형식으로 전달

if __name__ == "__main__":
    run_simple('223.194.131.88', 80, app)
