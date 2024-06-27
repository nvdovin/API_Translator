import requests
import urllib.parse
import json
import fake_useragent

ua = fake_useragent.UserAgent()
text_to_translate = "!Меня зовут Илья. > [Я сотрудник чего-то] <@!"
encoded_text = urllib.parse.quote(text_to_translate)

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'Bearer a_25rccaCYcBC9ARqMODx2BV2M0wNZgDCEl3jryYSgYZtF1a702PVi4sxqi2AmZWyCcw4x209VXnCYwesx',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://lingvanex.com',
    'priority': 'u=1, i',
    'referer': 'https://lingvanex.com/',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': ua.random#'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

data = f'from=ru_RU&to=en_US&text={encoded_text}&platform=dp'

response = requests.post('https://api-b2b.backenster.com/b1/api/v3/translate/', headers=headers, data=data)

print(response)
print(response.json())