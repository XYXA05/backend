import http.client
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import requests

url = "https://api.piapi.ai/api/luma/v1/video"

payload = {
    "image_url": 'https://i1.static.athome.eu/images/annonces2/image_/ee/03/e7/65ab3e1347fe40a31c380c9f459bf022f35d77c7.png',
    "expand_prompt": True
}
headers = {
    "X-API-Key": "0f5eea9dd96c1eeb1657c3bf55c301490d465093ef03f3d69fc17989bb5e092b",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())