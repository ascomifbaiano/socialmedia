from bs4 import BeautifulSoup

with open("greatfon_resp.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("--- ALL LINKS IN GREATFON ---")
for idx, a in enumerate(soup.find_all('a', href=True)):
    print(f"{idx + 1}: Href: {a['href']} | Text: {a.get_text().strip()}")
    
print("\n--- BODY TEXT ---")
print(soup.body.get_text()[:4000])
