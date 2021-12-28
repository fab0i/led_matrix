import json
import os
import requests
from server.RgbMatrix import RgbMatrix
import time
from pyngrok import ngrok

print("Starting...")

#faboi_url = 'https://faboinet.herokuapp.com'
faboi_url = 'https://192.168.1.67:8000'


#public_urls = [1]
#print(public_urls)
#url = public_urls[-1]


http_tunnel = ngrok.connect(5000)
print(http_tunnel)
print(ngrok.get_tunnels())
exit();

post_data = {'action': "create", 'url': url}
headers = {'Referer': url}
pi_connect = faboi_url + '/apps/pixeled/pi_connect'
response = requests.post(pi_connect, json=post_data, headers=headers)
print(response)
print(response.content)
data = response.json()
print("RESPONSE DATA:", data)
# @TODO First confirm it's code 200...
if data['success']:
    if 'code' not in data:
        print("INVALID RESPONSE DATA")
        print(data)
        print("EXITING....")
        exit(0)

    code = data['code']
    code_json = {'code': code, 'connected': False}

    with open("pixeled_connection", "w") as f:
        json.dump(code_json, f)

    post_data2 = {"action": 'confirm', 'success': True, 'code': code}
    response2 = requests.post(pi_connect, json=post_data2, headers=headers)
    data2 = response2.json()
    if 'success' in data2 and data2['success']:
        print("SUCCESS")
    else:
        print("HORRIBLE FAILURE!!", data2)
