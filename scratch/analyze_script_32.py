import re
import json

with open("script_32.js", "r", encoding="utf-8") as f:
    content = f.read()

print("Script 32 Length:", len(content))

# Find all occurrences of shortcode in script_32.js
# Let's search for "shortcode":"..." or similar patterns
shortcodes = re.findall(r'"shortcode"\s*:\s*"([A-Za-z0-9_-]+)"', content)
print("Found shortcodes by simple regex:", len(shortcodes), shortcodes)

# Let's try to search for the pattern of links or post IDs
# Instagram post IDs can also be in different structures
# Let's print some occurrences of shortcode with surrounding text
for match in re.finditer(r'"shortcode"', content):
    start = max(0, match.start() - 100)
    end = min(len(content), match.end() + 100)
    print("\nMatch Context:")
    print(content[start:end])
