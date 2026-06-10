import requests
from bs4 import BeautifulSoup
import re

url_picuki = "https://picuki.com/profile/ifbaiano"
url_greatfon = "https://greatfon.com/v/ifbaiano"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def analyze_site(url, name):
    print(f"\n=== ANALYZING {name} ===")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print("Status:", response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save HTML for manual review if needed
        with open(f"{name.lower()}_resp.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        # Search for post links
        # Picuki usually embeds links as <a href="https://www.picuki.com/media/..."> or containing '/media/'
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/media/' in href or '/p/' in href or '/reel/' in href:
                links.append((href, a.get_text().strip()[:50]))
        print(f"Found {len(links)} media links. Sample:")
        for l, text in links[:10]:
            print(f"  Href: {l} | Text: {text}")
            
        # Check if there are shortcodes
        # Picuki media links look like: https://www.picuki.com/media/3165243162739198273
        # Greatfon media links look like: /media/3165243162739198273 or similar
        
        # Let's search for snippets/captions
        # In Picuki, the caption is usually in .photo-description or .description
        descriptions = [d.get_text().strip() for d in soup.select('.photo-description, .description, .post-description')]
        print(f"Found {len(descriptions)} descriptions. Sample:")
        for d in descriptions[:3]:
            print(f"  Desc: {d[:100]}...")
            
        # Check for post times
        # In Picuki, time is in .time or .post-time or similar
        times = [t.get_text().strip() for t in soup.select('.time, .post-time, .date')]
        print(f"Found {len(times)} times. Sample:")
        for t in times[:5]:
            print(f"  Time: {t}")
            
    except Exception as e:
        print("Error:", e)

analyze_site(url_picuki, "Picuki")
analyze_site(url_greatfon, "Greatfon")
