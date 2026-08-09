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
    print("Xbox Browse State Analysis")
    print("================================")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    response.raise_for_status()

    match = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});',
        response.text,
        re.DOTALL
    )

    if not match:
        print("PRELOADED_STATE not found")
        return

    state = json.loads(match.group(1))

    print("PRELOADED_STATE parsed")
    print()

    # Search the entire state for strings related to
    # deals, discounts and free games.
    keywords = [
        "deal",
        "deals",
        "discount",
        "discounts",
        "free",
        "sale",
        "special",
        "promotion",
        "offer",
    ]

    state_text = json.dumps(state).lower()

    print("Keyword occurrences:")
    print("--------------------")

    for keyword in keywords:
        print(f"{keyword:12} {state_text.count(keyword)}")

    print()

    # Find dictionaries containing useful combinations
    # such as productId + price + discount.
    matches = []

    def walk(obj, path="root"):
        if isinstance(obj, dict):

            keys = {str(k).lower() for k in obj.keys()}

            has_product = "productid" in keys
            has_price = any(
                k in keys
                for k in ["price", "listprice", "msrp"]
            )
            has_discount = any(
                k in keys
                for k in ["discount", "discountpercentage"]
            )

            if has_product and (has_price or has_discount):
                matches.append((path, obj))

            for key, value in obj.items():
                walk(value, f"{path}.{key}")

        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                walk(value, f"{path}[{i}]")

    walk(state)

    print(f"Objects containing product + pricing fields: {len(matches)}")
    print()

    for i, (path, obj) in enumerate(matches[:20], 1):

        print("=" * 70)
        print(f"OBJECT #{i}")
        print(f"PATH: {path}")
        print("=" * 70)

        for key, value in obj.items():

            key_lower = str(key).lower()

            if any(term in key_lower for term in [
                "product",
                "title",
                "name",
                "price",
                "msrp",
                "discount",
                "sale",
                "deal",
                "offer",
                "availability",
            ]):
                print(f"{key}: {value}")

        print()


if __name__ == "__main__":
    main()
