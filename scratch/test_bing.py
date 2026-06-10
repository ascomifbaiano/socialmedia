import requests
from bs4 import BeautifulSoup
import re

username = "ifbaiano"
query = f"site:instagram.com/{username}"

url = f"https://www.bing.com/search?q={query}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=20)
    print("Status Code:", response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Print all links that contain instagram.com
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'instagram.com' in href:
            links.append(href)
            
    print("Found Instagram links:", len(links))
    for l in set(links):
        print("  -", l)
except Exception as e:
    print("Error:", e)
