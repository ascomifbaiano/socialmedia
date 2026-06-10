import requests

instances = [
    "https://rsshub.app",
    "https://rsshub.rssbuddy.com",
    "https://rsshub.feed.ren",
    "https://rsshub.icu",
    "https://rss.irif.fr",
    "https://hub.keyb.dev",
    "https://rss.sw.io",
    "https://rss.bloof.xyz",
    "https://rsshub.moe",
    "https://uneven.moe"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

for base in instances:
    url = f"{base}/instagram/user/ifbaiano"
    try:
        response = requests.get(url, headers=headers, timeout=12)
        print(f"Instance: {base} -> Status: {response.status_code}, Length: {len(response.text)}")
        if response.status_code == 200:
            print(f"SUCCESS! Preview of response from {base}:")
            print(response.text[:500])
            break
    except Exception as e:
        print(f"Instance: {base} -> Error: {e}")
