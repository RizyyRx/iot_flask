import requests

url = "http://iotcloud.selfmade.technology/api/motion/capture"

payload = {}
files=[
  ('file',('ao2.jpg',open('ao2.jpg','rb'),'image/jpeg'))
]
headers = {
  'X-Authorization': 'Bearer 6ca10fa2-443f-4725-b7d3-4bc302ff5c31',
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)