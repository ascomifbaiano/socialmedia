from bs4 import BeautifulSoup
import re

def inspect_saved_html(filename):
    print(f"\n=== INSPECTING {filename} ===")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
            
        print("Length:", len(html))
        soup = BeautifulSoup(html, 'html.parser')
        
        # Let's print all <a> tags hrefs (first 30)
        hrefs = []
        for a in soup.find_all('a', href=True):
            hrefs.append(a['href'])
        print(f"Total links: {len(hrefs)}")
        print("Sample Hrefs:", hrefs[:20])
        
        # Check if there are images
        imgs = [img['src'] for img in soup.find_all('img', src=True)]
        print(f"Total images: {len(imgs)}")
        print("Sample Images:", imgs[:10])
        
        # Let's find any text matching instagram post links
        # Instagram post shortcodes are alphanumeric, e.g., C-dXirGvz5l
        # Let's search for "ifbaiano" in the text
        print("Occurrences of 'ifbaiano':", html.lower().count("ifbaiano"))
        
        # Let's see if the page is a block page or a search page
        # Print the title and first 1000 characters of text
        print("Title:", soup.title.string if soup.title else "No Title")
        
        # Print body text (first 500 chars)
        text = soup.get_text()
        print("Text preview:", repr(text.strip()[:500]))
        
    except Exception as e:
        print("Error:", e)

inspect_saved_html("picuki_resp.html")
inspect_saved_html("greatfon_resp.html")
