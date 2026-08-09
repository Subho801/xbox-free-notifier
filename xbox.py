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
    print("Xbox Preloaded State Test")
    print("================================")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    print(f"Content Length: {len(response.text)}")

    response.raise_for_status()

    html = response.text

    # Find the preloaded state
    match = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});',
        html,
        re.DOTALL
    )

    if not match:
        print("\n❌ PRELOADED_STATE not found")
        return

    raw_state = match.group(1)

    print("\n✅ PRELOADED_STATE found")
    print(f"State size: {len(raw_state)} characters")

    try:
        state = json.loads(raw_state)
    except json.JSONDecodeError as e:
        print("\n❌ Could not parse JSON")
        print(e)
        return

    print("\n✅ JSON parsed successfully")

    print("\nTop-level keys:")
    for key in state.keys():
        print(f"  - {key}")

    # Save a small summary of keys recursively
    print("\nSearching for interesting fields...")

    interesting = [
        "productId",
        "productID",
        "ProductId",
        "product_id",
        "title",
        "name",
        "price",
        "Price",
        "msrp",
        "MSRP",
        "discount",
        "Discount",
        "sale",
        "availability",
    ]

    state_text = json.dumps(state)

    for term in interesting:
        count = state_text.lower().count(term.lower())
        if count:
            print(f"  {term}: {count} occurrence(s)")


if __name__ == "__main__":
    main()
