import re

with open("response.html", "r", encoding="utf-8") as f:
    html = f.read()

print("Length of HTML:", len(html))

# Search for any matches of standard instagram paths
p_matches = re.findall(r'/p/[A-Za-z0-9_-]+/', html)
reels_matches = re.findall(r'/reels/[A-Za-z0-9_-]+/', html)
reel_matches = re.findall(r'/reel/[A-Za-z0-9_-]+/', html)

print("Found /p/ matches:", len(p_matches), p_matches[:10])
print("Found /reels/ matches:", len(reels_matches), reels_matches[:10])
print("Found /reel/ matches:", len(reel_matches), reel_matches[:10])

# Search for any link containing instagram.com/p/ or similar
links = re.findall(r'instagram\.com/(?:p|reels|reel)/[A-Za-z0-9_-]+', html)
print("Found full instagram links:", len(links), links[:10])

# Let's search for some raw codes (e.g. shortcodes are 11 chars or similar)
# Instagram embeds data in window._sharedData or script tags
# Let's search for "shortcode" or "code"
shortcodes = re.findall(r'"shortcode"\s*:\s*"([A-Za-z0-9_-]+)"', html)
print("Found 'shortcode' matches:", len(shortcodes), shortcodes[:10])

# Search for "code" in JSON
codes = re.findall(r'"code"\s*:\s*"([A-Za-z0-9_-]+)"', html)
print("Found 'code' matches:", len(codes), codes[:10])

# Search for video/image post links in quotes
any_p = re.findall(r'"/(?:p|reels|reel)/([A-Za-z0-9_-]+)/"', html)
print("Found quoted relative links:", len(any_p), any_p[:10])
