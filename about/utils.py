import json
import urllib.request

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh;'
                    'Intel Mac OS X 11_4)'
                    'AppleWebKit/605.1.15 '
                    '(KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Origin': 'https://yandex.ru',
    'Referer': 'https://yandex.ru/',
}

API_URL = 'https://zeapi.yandex.net/lab/api/yalm/text3'


def get_balaboba_text(start_text):
    payload = {"query": f"{start_text}", "intro": 0, "filter": 1}
    params = json.dumps(payload).encode('utf8')
    req = urllib.request.Request(API_URL, data=params, headers=headers)
    response = urllib.request.urlopen(req)
    text = response.read().decode(
        'unicode-escape').split('"text": "')[1].split('", "error"')[0]
    return text
