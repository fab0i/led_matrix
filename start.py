import json
import os
import requests

print("Starting...")

faboi_url = 'https://faboinet.herokuapp.com'

#os.system("./ngrok http 80")
os.system("curl http://localhost:4040/api/tunnels > tunnels.json")

print("Creating temporary tunnels.json...")
with open('tunnels.json') as f:
    tunnels = json.load(f)

public_urls = []
for i in tunnels['tunnels']:
    public_urls.append(i['public_url'])

print("Public URLs:")
print(public_urls)

if os.path.exists("tunnels.json"):
    os.remove("tunnels.json")
print("\nRemoved tunnels.json.")

url = public_urls[-1]

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
    with open("pixeled_connection", "w") as f:
        n = f.write(code)
    post_data2 = {"action": 'confirm', 'success': True, 'code': code}
    response2 = requests.post(pi_connect, json=post_data2, headers=headers)
    data2 = response2.json()
    if 'success' in data2 and data2['success']:
        print("SUCCESS")
    else:
        print("HORRIBLE FAILURE!!", data2)
