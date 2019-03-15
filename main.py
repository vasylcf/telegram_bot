from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
import requests
import json
import datetime
import re
from dateutil.parser import parse

URL='https://api.telegram.org/bot680631631:AAEoxBhUxXMM1KsDkfZDTqZP9hluW-bLMu0/'

app=Flask(__name__)
SSLify(app)

def main():
    app.run()


def write_json(data,file='example.json'):
    with open(file,'w') as f:
         json.dump(data,f, indent=2, ensure_ascii=False)

def get_updates(url=URL):
    r=requests.get(url+'getUpdates')
    return r.json()

def last_update():
    return get_updates()['result'][-1]

def send_message(chat_id,text='Привет, я вернулся'):
    #answ=requests.get(URL+'sendMessage',params={'chat_id':chat_id,'text':text})
    url=URL+'sendMessage'
    answ={'chat_id':chat_id,'text':text}
    r=requests.post(url,json=answ)
    return answ

def parse_text(text):
    pattern= r'/\w+'
    cur=re.search(pattern,text).group()
    return cur[1:]

def get_rates(currency,url='https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode={}&date={}&json'):
    date=str(datetime.datetime.today().strftime("%Y%m%d"))
    r=requests.get(url.format(currency,date))
    data=r.json()[0]
    return (data['exchangedate']+' '+data['cc']+ ' ' + str(data['rate']))


def get_weather(city='Dnepropetrovsk'):
    url=f'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22{city}%22)and%20u%3D%22c%22&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys'
    data=requests.get(url).json()
    forecast_data=data['query']['results']['channel']['item']['forecast']
    forecast=[]
    forecast_print=[]
    for i in forecast_data:
        forecast.append({
            'date': parse (i['date']).strftime('%d.%m.%Y'),
            'high temp': i['high']+u'\u2103'
        }
        )
        forecast_print.append((parse (i['date']).strftime('%d.%m.%Y'),i['high']+u'\u2103'))
    return str(forecast_print)


@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':

        now=datetime.datetime.now()

        r=request.get_json()
        #write_json(r)
        chat_id=r['message']['chat']['id']
        message=r['message']['text']




        if r'/' in message:

            if parse_text(message).upper() in ['USD','EUR']:
                currency=parse_text(message).upper()
                res=get_rates(currency)
                send_message (chat_id,res)
            elif parse_text(message).lower()== 'погода':
                weather=get_weather()
                send_message (chat_id,weather)

            else:
                send_message (chat_id,message)

        else:
            if 'привет' in message.lower():
                send_message (chat_id,'Привет, я люблю Альбину')







        return jsonify(r)
    else:
        return 'Hello, I am bot'

#webhook:
# https://api.telegram.org/bot680631631:AAEoxBhUxXMM1KsDkfZDTqZP9hluW-bLMu0/setWEbhook?url=https://vasylcf.pythonanywhere.com/

if __name__=='__main__':
    main()
    #app.run()
