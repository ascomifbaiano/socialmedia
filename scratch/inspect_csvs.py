import os
import pandas as pd

def inspect():
    print("=== ROOT CSV FILES ===")
    for f in os.listdir("."):
        if f.endswith(".csv"):
            try:
                df = pd.read_csv(f)
                real_posts = df[df['shortcode'].astype(str) != 'placeholder']
                print(f"File: {f} | Total rows: {len(df)} | Real posts: {len(real_posts)}")
                if len(real_posts) > 0:
                    print(real_posts[['campus', 'shortcode', 'data']])
            except Exception as e:
                print(f"Error reading {f}: {e}")

    print("\n=== DATA SUBDIRECTORY CSV FILES ===")
    if os.path.exists("data"):
        for root, dirs, files in os.walk("data"):
            for f in files:
                if f.endswith(".csv"):
                    path = os.path.join(root, f)
                    try:
                        df = pd.read_csv(path)
                        real_posts = df[df['shortcode'].astype(str) != 'placeholder']
                        print(f"File: {path} | Total rows: {len(df)} | Real posts: {len(real_posts)}")
                    except Exception as e:
                        print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    inspect()
