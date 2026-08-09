import requests
import re
import json


PAGE_URL = "https://www.xbox.com/en-US/games/browse"

BROWSE_API = "https://emerald.xboxservices.com/xboxcomfd/browse"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def main():

    print("================================")
    print("Xbox Browse API Discovery")
    print("================================")

    # --------------------------------------------------
    # 1. Get Xbox browse page
    # --------------------------------------------------

    response = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=30,
    )

    print(f"Page HTTP Status: {response.status_code}")

    response.raise_for_status()

    # --------------------------------------------------
    # 2. Extract PRELOADED_STATE
    # --------------------------------------------------

    match = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});',
        response.text,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError("PRELOADED_STATE not found")

    state = json.loads(match.group(1))

    print("PRELOADED_STATE parsed")

    # --------------------------------------------------
    # 3. Inspect channels
    # --------------------------------------------------

    core2 = state.get("core2", {})

    channels = core2.get("channels", {})

    print()
    print("core2 channels:")
    print(list(channels.keys()))

    # --------------------------------------------------
    # 4. Find BROWSE_ channel
    # --------------------------------------------------

    browse = channels.get("BROWSE_")

    if not browse:
        print()
        print("❌ BROWSE_ channel not found")
        return

    print()
    print("✅ BROWSE_ channel found")

    print("BROWSE_ keys:")
    print(list(browse.keys()))

    data = browse.get("data")

    if not data:
        print()
        print("❌ BROWSE_ data not found")
        return

    print()
    print("BROWSE_ data keys:")
    print(list(data.keys()))

    # --------------------------------------------------
    # 5. Check for encoded continuation token
    # --------------------------------------------------

    encoded_ct = data.get("encodedCT")

    print()

    if encoded_ct:
        print("✅ encodedCT found")
        print(f"encodedCT length: {len(encoded_ct)}")
        print(f"encodedCT preview: {encoded_ct[:100]}...")
    else:
        print("❌ encodedCT not found")

    # --------------------------------------------------
    # 6. Check products already returned
    # --------------------------------------------------

    products = data.get("productSummaries", [])

    print()
    print(f"Products in BROWSE_ data: {len(products)}")

    for product in products[:5]:
        print()
        print("Product:")
        print(f"  ID:    {product.get('productId')}")
        print(f"  Title: {product.get('title')}")

    # --------------------------------------------------
    # 7. Test browse API if token exists
    # --------------------------------------------------

    if not encoded_ct:
        return

    print()
    print("================================")
    print("Testing Xbox Browse Backend")
    print("================================")

    payload = {
        "ChannelKeyToBeUsedInResponse": "BROWSE_",
        "EncodedCT": encoded_ct,
        "Filters": "e30=",
        "ReturnFilters": False,
    }

    browse_response = requests.post(
        BROWSE_API,
        headers=HEADERS,
        json=payload,
        timeout=30,
    )

    print(
        f"Browse API HTTP Status: "
        f"{browse_response.status_code}"
    )

    print()
    print("Response preview:")
    print(browse_response.text[:5000])


if __name__ == "__main__":
    main()
