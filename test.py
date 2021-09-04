import requests

r = requests.post('http://localhost:8000/apps/pixeled/pi_connect', json={'ha': 'ho'})
print(r.content)
#
# r = requests.get('http://localhost:8000/apps/pixeled')
# print(r.content)