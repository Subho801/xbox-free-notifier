import requests
import re
import json


PAGE_URL = "https://www.xbox.com/en-US/games/browse"
API_URL = "https://emerald.xboxservices.com/xboxcomfd/browse?locale=en-US"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "x-ms-api-version": "1.1",
}


def get_page_state():

    response = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    match = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});',
        response.text,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError("PRELOADED_STATE not found")

    return json.loads(match.group(1))


def main():

    print("================================")
    print("Xbox Browse Pagination Test")
    print("================================")

    state = get_page_state()

    print("✅ Xbox page loaded")

    # Current Xbox structure:
    channel_data = (
        state
        .get("core2", {})
        .get("channels", {})
        .get("channelData", {})
    )

    # Find the BROWSE channel dynamically
    browse_data = None

    for key, value in channel_data.items():

        if "BROWSE_" in key:
            browse_data = (
                value
                .get("data", {})
            )

            print(f"✅ Found channel: {key}")
            break

    if not browse_data:
        raise RuntimeError(
            "BROWSE channel data not found"
        )

    encoded_ct = browse_data.get("encodedCT")

    if not encoded_ct:
        raise RuntimeError(
            "encodedCT not found"
        )

    print(f"Current token length: {len(encoded_ct)}")

    # --------------------------------------------------
    # Request next page
    # --------------------------------------------------

    payload = {
        "ChannelKeyToBeUsedInResponse": "BROWSE_",
        "EncodedCT": encoded_ct,
        "Filters": "e30=",
        "ReturnFilters": False,
    }

    print()
    print("Requesting next page...")

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=30,
    )

    print(
        f"Browse API HTTP Status: "
        f"{response.status_code}"
    )

    print()

    response.raise_for_status()

    data = response.json()

    print("✅ Page 2 received")
    print()
    print("Top-level keys:")
    print(list(data.keys()))

    # --------------------------------------------------
    # Products
    # --------------------------------------------------

    products = data.get(
        "productSummaries",
        []
    )

    print()
    print(
        f"Products returned: "
        f"{len(products)}"
    )

    for product in products:

        print(
            f"{product.get('productId')} | "
            f"{product.get('title')}"
        )

    # --------------------------------------------------
    # Next continuation token
    # --------------------------------------------------

    channels = data.get(
        "channels",
        {}
    )

    browse_channel = channels.get(
        "BROWSE_",
        {}
    )

    next_data = browse_channel.get(
        "data",
        {}
    )

    next_token = next_data.get(
        "encodedCT"
    )

    print()

    if next_token:
        print("✅ Next continuation token received")
        print(
            f"Next token length: "
            f"{len(next_token)}"
        )
    else:
        print(
            "❌ No next continuation token"
        )


if __name__ == "__main__":
    main()
