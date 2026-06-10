with open("script_32.js", "r", encoding="utf-8") as f:
    content = f.read()

print("Script 32 Length:", len(content))

import re
matches = list(re.finditer(r'shortcode', content))
print("Found matches for 'shortcode':", len(matches))
for m in matches[:5]:
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 100)
    print("\n--- MATCH ---")
    print(content[start:end])
