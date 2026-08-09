import requests
import re
import json


URL = "https://www.xbox.com/en-US/games/browse"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def main():
    print("================================")
    print("Xbox Product Data Discovery")
    print("================================")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    response.raise_for_status()

    html = response.text

    match = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});',
        html,
        re.DOTALL
    )

    if not match:
        print("❌ PRELOADED_STATE not found")
        return

    state = json.loads(match.group(1))

    print("✅ PRELOADED_STATE parsed")

    # Recursively find dictionaries containing productId
    found = []

    def walk(obj, path="root"):
        if isinstance(obj, dict):

            keys_lower = {str(k).lower() for k in obj.keys()}

            if "productid" in keys_lower:
                found.append((path, obj))

            for key, value in obj.items():
                walk(value, f"{path}.{key}")

        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, f"{path}[{index}]")

    walk(state)

    print(f"\nFound {len(found)} objects containing productId\n")

    for index, (path, obj) in enumerate(found[:10], 1):

        print("=" * 70)
        print(f"PRODUCT OBJECT #{index}")
        print(f"Path: {path}")
        print("=" * 70)

        # Print only useful fields
        for key, value in obj.items():

            key_lower = str(key).lower()

            if any(term in key_lower for term in [
                "product",
                "title",
                "name",
                "price",
                "msrp",
                "discount",
                "availability",
                "sku",
                "url",
                "slug"
            ]):
                print(f"{key}: {value}")

        print()


if __name__ == "__main__":
    main()
