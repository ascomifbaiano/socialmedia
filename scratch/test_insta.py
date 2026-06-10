import requests

url = "https://www.instagram.com/ifbaiano/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
}

try:
    response = requests.get(url, headers=headers, timeout=20)
    print("Status Code:", response.status_code)
    print("Response URL:", response.url)
    print("Response Content Length:", len(response.text))
    print("\n--- FIRST 2000 CHARACTERS ---")
    print(response.text[:2000])
    
    # Save full response for inspection
    with open("response.html", "w", encoding="utf-8") as f:
        f.write(response.text)
except Exception as e:
    print("Error:", e)
