from bs4 import BeautifulSoup
import json
import re

with open("response.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
scripts = soup.find_all("script")
print("Total script tags found:", len(scripts))

# Let's search for script tags containing certain key Instagram JSON fields
keywords = ["edge_owner_to_timeline_media", "shortcode", "display_url", "biography", "profile_pic_url"]

found_any = False
for idx, script in enumerate(scripts):
    content = script.string or script.get_text() or ""
    if not content:
        continue
        
    matched = [kw for kw in keywords if kw in content]
    if matched:
        found_any = True
        print(f"\nScript {idx} (Length: {len(content)}):")
        print("  Matched keywords:", matched)
        print("  Snippet:", content[:500] + "...")
        
        # Let's save this script content for further analysis
        with open(f"script_{idx}.js", "w", encoding="utf-8") as sf:
            sf.write(content)

if not found_any:
    print("\nNo script tag matched the keywords.")
    # Search the raw HTML for any occurrence of the keywords
    for kw in keywords:
        occurrences = [m.start() for m in re.finditer(kw, html)]
        print(f"Occurrences of '{kw}' in raw HTML:", len(occurrences), occurrences[:5])
