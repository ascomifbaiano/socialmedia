import requests
from bs4 import BeautifulSoup

url = "https://imginn.com/ifbaiano/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    print("Status:", response.status_code)
    print("Length:", len(response.text))
    
    soup = BeautifulSoup(response.text, 'html.parser')
    print("Title:", soup.title.string if soup.title else "No Title")
    
    # Save HTML for inspection
    with open("imginn_resp.html", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    # Search for post links
    # Imginn post links usually contain '/p/' or '/reel/' or are in a specific grid class
    links = [a['href'] for a in soup.find_all('a', href=True) if '/p/' in a['href'] or '/reel/' in a['href']]
    print("Found links:", len(links))
    for l in links[:5]:
        print("  -", l)
except Exception as e:
    print("Error:", e)
