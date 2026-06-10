import requests
from bs4 import BeautifulSoup

urls = [
    "https://www.picuki.com/profile/ifbaiano",
    "https://www.picuki.com/profile/instagram",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        print(f"\nURL: {url}")
        print("Final URL:", response.url)
        print("Status:", response.status_code)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Title:", soup.title.string if soup.title else "No Title")
        
        # Check if there are post links on picuki
        # Picuki post link pattern is usually '/media/'
        links = [a['href'] for a in soup.find_all('a', href=True) if '/media/' in a['href']]
        print("Found media links:", len(links))
        if links:
            print("Sample link:", links[0])
            
    except Exception as e:
        print(f"Error on {url}: {e}")
