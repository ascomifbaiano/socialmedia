import requests
from bs4 import BeautifulSoup
import re

def get_data_duckduckgo(username):
    url = f"https://html.duckduckgo.com/html/?q=site:instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    all_results = []
    print(f"  [DuckDuckGo] Buscando: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print("Failed with status code:", response.status_code)
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.select('.result__body')
        for item in results:
            url_tag = item.select_one('.result__url')
            if not url_tag:
                continue
            
            link = url_tag.get_text().strip()
            if not link.startswith('http'):
                link = 'https://' + link
                
            if 'instagram.com' in link and any(x in link for x in ['/p/', '/reels/', '/reel/']):
                snippet_tag = item.select_one('.result__snippet')
                snippet = snippet_tag.get_text().strip() if snippet_tag else ""
                
                # Date extraction
                date_match = re.search(r'on ([A-Za-z]+ \d+, \d{4})', snippet)
                if not date_match:
                    date_match = re.search(r'(?:on|em) (\d+ de [A-Za-z]+ de \d{4})', snippet)
                date_str = date_match.group(1) if date_match else ""
                
                all_results.append({
                    'link': link,
                    'snippet': snippet,
                    'date': date_str
                })
        print(f"  [DuckDuckGo] {len(all_results)} resultados encontrados.")
        return all_results
    except Exception as e:
        print(f"  [DuckDuckGo] Erro: {e}")
        return []

res = get_data_duckduckgo("ifbaiano")
for r in res[:5]:
    print("\nLink:", r['link'])
    print("Date extracted:", r['date'])
    print("Snippet:", r['snippet'][:100] + "...")
