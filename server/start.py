import json
import os
import requests

print("Starting...i")

#os.system("../ngrok http 80")

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


r = requests.get('faboinet.herokuapp.com')

print(r.content)