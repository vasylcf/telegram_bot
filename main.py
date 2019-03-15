from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
import requests
import json
import datetime
import re
from dateutil.parser import parse
import time, uuid, urllib
import hmac, hashlib
from base64 import b64encode

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
    def edit_date(a):
        return datetime.date(1970, 1, 1) + datetime.timedelta((a/3600)/24)

    """
    Basic info
    """
    url = 'https://weather-ydn-yql.media.yahoo.com/forecastrss'
    method = 'GET'
    app_id = 'YNmvxS4q'
    consumer_key = 'dj0yJmk9ZVpNZW94QXNEdUZmJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTBh'
    consumer_secret = '20a64525b515ec0bb49ddb7424ff50fcf69eafcc'
    concat = '&'
    query = {'location': 'Dnepropetrovsk', 'format': 'json'}
    oauth = {
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_version': '1.0'
    }

    """
    Prepare signature string (merge all params and SORT them)
    """
    merged_params = query.copy()
    merged_params.update(oauth)
    sorted_params = [k + '=' + urllib.request.quote(merged_params[k], safe='') for k in sorted(merged_params.keys())]
    signature_base_str =  method + concat + urllib.request.quote(url, safe='') + concat + urllib.request.quote(concat.join(sorted_params), safe='')

    """
    Generate signature
    """
    composite_key = urllib.request.quote(consumer_secret, safe='') + concat
    oauth_signature = b64encode(hmac.new(str.encode(composite_key), str.encode(signature_base_str), hashlib.sha1).digest())

    """
    Prepare Authorization header
    """
    oauth['oauth_signature'] = oauth_signature.decode()
    auth_header = 'OAuth ' + ', '.join(['{}="{}"'.format(k,v) for k,v in oauth.items()])

    """
    Send request
    """
    url = url + '?' + urllib.parse.urlencode(query)
    request = urllib.request.Request(url)
    request.add_header('Authorization', auth_header)
    request.add_header('X-Yahoo-App-Id', app_id)
    response = urllib.request.urlopen(request).read()
    data=json.loads(response)

    forecast_data=data['forecasts']
    forecast=[]
    forecast_print=[]
    for i in forecast_data:
        forecast.append({
            'date': edit_date (i['date']),
            'high temp': str(i['high'])+u'\u2103'
        }
        )
        forecast_print.append((edit_date (i['date']),str(i['high'])+u'\u2103'))
    return str(forecast_print)

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        now=datetime.datetime.now()
        r=request.get_json()
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
