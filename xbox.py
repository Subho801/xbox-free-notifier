import json
import re
import requests


PAGE_URL = "https://www.xbox.com/en-US/games/browse"
API_URL = "https://emerald.xboxservices.com/xboxcomfd/browse?locale=en-US"

CHANNEL_KEY = "BROWSE_CHANNELID=_FILTERS="

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-ms-api-version": "1.1",
    "MS-CV": "XboxFreeNotifier.1",
}


def get_preloaded_state(session):
    response = session.get(PAGE_URL, timeout=30)
    response.raise_for_status()

    print("✅ Xbox page loaded")

    match = re.search(
        r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});",
        response.text,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError("PRELOADED_STATE not found")

    state = json.loads(match.group(1))

    print("✅ PRELOADED_STATE parsed")

    return state


def get_channel(state):
    channel_data = (
        state["core2"]
        ["channels"]
        ["channelData"]
    )

    if CHANNEL_KEY not in channel_data:
        raise RuntimeError("Browse channel not found")

    return channel_data[CHANNEL_KEY]


def get_next_page(session, encoded_ct, encoded_filters=None):
    payload = {
        "Filters": encoded_filters or "",
        "ReturnFilters": False,
        "ChannelKeyToBeUsedInResponse": CHANNEL_KEY,
        "EncodedCT": encoded_ct,
    }

    response = session.post(
        API_URL,
        json=payload,
        timeout=30,
    )

    print("Browse API HTTP Status:", response.status_code)

    response.raise_for_status()

    return response.json()


def main():
    print("================================")
    print("Xbox 100% OFF Discovery")
    print("================================")

    session = requests.Session()
    session.headers.update(HEADERS)

    state = get_preloaded_state(session)

    channel = get_channel(state)

    encoded_ct = channel["data"]["encodedCT"]
    encoded_filters = channel["data"].get("encodedFilters", "")

    print("Channel:", CHANNEL_KEY)
    print("Initial token length:", len(encoded_ct))

    print()
    print("Requesting Xbox catalog page...")

    data = get_next_page(
        session,
        encoded_ct,
        encoded_filters,
    )

    print("✅ Browse response received")

    products = data.get("channels", {}).get(CHANNEL_KEY, {}).get("products", [])

    product_summaries = data.get("productSummaries", {})
    sku_summaries = data.get("skuSummaries", {})
    availability_summaries = data.get("availabilitySummaries", {})

    print("Products:", len(products))
    print("Product summaries:", len(product_summaries))
    print("SKU summaries:", len(sku_summaries))
    print("Availability summaries:", len(availability_summaries))

    print()
    print("================================")
    print("CHECKING FOR 100% OFF")
    print("================================")

    found = 0

    for product_id, product in product_summaries.items():

        title = (
            product.get("title")
            or product.get("name")
            or product.get("displayName")
            or "Unknown"
        )

        # Search all availability records belonging to this product
        for availability_id, availability in availability_summaries.items():

            if availability.get("productId") != product_id:
                continue

            price = availability.get("price", {})

            list_price = price.get("listPrice")
            msrp = price.get("msrp")
            discount = price.get("discountPercentage")

            if list_price is None:
                continue

            is_free = (
                discount == 100
                or (
                    list_price == 0
                    and msrp is not None
                    and msrp > 0
                )
            )

            if not is_free:
                continue

            found += 1

            print()
            print("--------------------------------")
            print("FREE GAME FOUND")
            print("--------------------------------")
            print("Title:", title)
            print("Product ID:", product_id)
            print("Availability ID:", availability_id)
            print("List Price:", list_price)
            print("MSRP:", msrp)
            print("Discount:", discount)

    print()
    print("================================")
    print("100% OFF FOUND:", found)
    print("================================")


if __name__ == "__main__":
    main()
