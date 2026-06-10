import requests

viewers = [
    "https://greatfon.com/v/ifbaiano",
    "https://picuki.com/profile/ifbaiano",
    "https://imgsed.com/ifbaiano/",
    "https://save-insta.com/",
    "https://storiesig.info/pt/ifbaiano/",
    "https://dumpor.com/v/ifbaiano",
    "https://instanavigation.com/user-profile/ifbaiano",
    "https://iganony.io/profile/ifbaiano",
    "https://www.picnob.com/profile/ifbaiano/"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

for url in viewers:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url} -> Status: {response.status_code}, Length: {len(response.text)}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
