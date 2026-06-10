import requests
import json

username = "ifbaiano"
url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "X-IG-App-ID": "936619743392459",
    "Referer": f"https://www.instagram.com/{username}/",
    "X-Requested-With": "XMLHttpRequest"
}

try:
    response = requests.get(url, headers=headers, timeout=20)
    print("Status Code:", response.status_code)
    print("Headers:", dict(response.headers))
    print("Content Length:", len(response.text))
    if response.status_code == 200:
        data = response.json()
        user_info = data.get('data', {}).get('user', {})
        print("Username:", user_info.get('username'))
        print("Full Name:", user_info.get('full_name'))
        timeline = user_info.get('edge_owner_to_timeline_media', {})
        posts = timeline.get('edges', [])
        print(f"Found {len(posts)} posts in timeline!")
        for idx, post in enumerate(posts[:3]):
            node = post.get('node', {})
            print(f"\nPost {idx + 1}:")
            print("  Shortcode:", node.get('shortcode'))
            print("  Type:", node.get('__typename'))
            caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
            caption = caption_edges[0].get('node', {}).get('text') if caption_edges else "No caption"
            print("  Caption:", caption[:100] + "...")
            print("  Link:", f"https://www.instagram.com/p/{node.get('shortcode')}/")
    else:
        print("Response Text (first 500 chars):", response.text[:500])
except Exception as e:
    print("Error:", e)
