from bs4 import BeautifulSoup

with open("response.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
title = soup.title.string if soup.title else "No Title"
print("Title:", title)

# Check if there is text like "login" or "entrar" or "cadastrar"
print("Contains 'Entrar':", "entrar" in html.lower())
print("Contains 'Login':", "login" in html.lower())
print("Contains 'Instagram':", "instagram" in html.lower())

# Print some text elements
text_elements = [s.get_text() for s in soup.find_all(['h1', 'h2', 'p'])]
print("\n--- TEXT ELEMENTS ---")
for text in text_elements[:15]:
    if text.strip():
        print("-", text.strip())
