import json
import re
import requests
from datetime import datetime


PAGE_URL = "https://www.xbox.com/en-US/games/browse"

API_URL = (
    "https://emerald.xboxservices.com/"
    "xboxcomfd/browse?locale=en-US"
)

CHANNEL_KEY = "BROWSE_CHANNELID=_FILTERS="

# Start small while testing.
# 5 pages = up to 125 Xbox products.
MAX_PAGES = 700

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


# ============================================================
# LOAD XBOX BROWSE PAGE
# ============================================================

def get_preloaded_state(session):

    response = session.get(
        PAGE_URL,
        timeout=30,
    )

    response.raise_for_status()

    print("✅ Xbox page loaded")

    match = re.search(
        r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});",
        response.text,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError(
            "PRELOADED_STATE not found"
        )

    state = json.loads(match.group(1))

    print("✅ PRELOADED_STATE parsed")

    return state


# ============================================================
# GET BROWSE CHANNEL
# ============================================================

def get_channel(state):

    channel_data = (
        state
        .get("core2", {})
        .get("channels", {})
        .get("channelData", {})
    )

    if CHANNEL_KEY not in channel_data:
        raise RuntimeError(
            f"Browse channel not found: {CHANNEL_KEY}"
        )

    return channel_data[CHANNEL_KEY]


# ============================================================
# REQUEST NEXT PAGE
# ============================================================

def get_next_page(
    session,
    encoded_ct,
    encoded_filters="",
):

    payload = {
        "Filters": encoded_filters,
        "ReturnFilters": False,
        "ChannelKeyToBeUsedInResponse": CHANNEL_KEY,
        "EncodedCT": encoded_ct,
    }

    response = session.post(
        API_URL,
        json=payload,
        timeout=30,
    )

    print(
        "Browse API HTTP Status:",
        response.status_code,
    )

    if response.status_code != 200:
        print("Response:")
        print(response.text[:2000])

    response.raise_for_status()

    return response.json()


# ============================================================
# NORMALIZE XBOX DATA
# ============================================================

def normalize_collection(value):

    """
    Xbox may return some collections as either:

        {
            "PRODUCT_ID": {...}
        }

    or:

        [
            {
                "productId": "PRODUCT_ID",
                ...
            }
        ]

    Convert both forms into a list of dictionaries.
    """

    if isinstance(value, list):

        return [
            item
            for item in value
            if isinstance(item, dict)
        ]

    if isinstance(value, dict):

        result = []

        for key, item in value.items():

            if not isinstance(item, dict):
                continue

            item = dict(item)

            if "productId" not in item:
                item["productId"] = key

            result.append(item)

        return result

    return []


# ============================================================
# GET PRODUCT ID
# ============================================================

def get_product_id(item):

    if not isinstance(item, dict):
        return None

    return (
        item.get("productId")
        or item.get("productID")
        or item.get("ProductId")
        or item.get("ProductID")
    )


# ============================================================
# GET TITLE
# ============================================================

def get_title(product):

    if not isinstance(product, dict):
        return "Unknown"

    return (
        product.get("title")
        or product.get("name")
        or product.get("displayName")
        or product.get("DisplayName")
        or "Unknown"
    )


# ============================================================
# EXTRACT PRICE
# ============================================================

def get_price_data(availability):

    if not isinstance(availability, dict):
        return None

    price = availability.get("price")

    if isinstance(price, dict):
        return price

    # Some Xbox responses may expose the fields directly.
    if any(
        key in availability
        for key in (
            "listPrice",
            "msrp",
            "discountPercentage",
        )
    ):
        return availability

    return None


# ============================================================
# CHECK IF ACTUALLY FREE
# ============================================================

def is_100_percent_off(price):

    if not isinstance(price, dict):
        return False

    list_price = price.get("listPrice")
    msrp = price.get("msrp")
    discount = price.get("discountPercentage")

    # Explicit 100% discount
    if discount is not None:

        try:
            if float(discount) >= 100:
                return True
        except (
            TypeError,
            ValueError,
        ):
            pass

    # Price is zero but MSRP is greater than zero.
    if (
        list_price is not None
        and msrp is not None
    ):

        try:
            if (
                float(list_price) == 0
                and float(msrp) > 0
            ):
                return True
        except (
            TypeError,
            ValueError,
        ):
            pass

    return False


# ============================================================
# PROCESS ONE PAGE
# ============================================================

def process_page(data, page_number):

    channel = (
        data
        .get("channels", {})
        .get(CHANNEL_KEY, {})
    )

    products = channel.get("products", [])

    product_summaries = normalize_collection(
        data.get("productSummaries", [])
    )

    sku_summaries = normalize_collection(
        data.get("skuSummaries", [])
    )

    availability_summaries = normalize_collection(
        data.get("availabilitySummaries", [])
    )

    # ============================================================
    # TEMPORARY DEBUG - FIRST PAGE ONLY
    # ============================================================

    if page_number == 1:
        print()
        print("================================")
        print("AVAILABILITY SAMPLE")
        print("================================")

        for availability in availability_summaries[:5]:
            print()
            print(json.dumps(availability, indent=2))

        print()
        print("================================")
        print("END AVAILABILITY SAMPLE")
        print("================================")

    print()
    print("--------------------------------")
    print(f"PAGE {page_number}")
    print("--------------------------------")

    print(
        "Products:",
        len(products),
    )

    print(
        "Product summaries:",
        len(product_summaries),
    )

    print(
        "SKU summaries:",
        len(sku_summaries),
    )

    print(
        "Availability summaries:",
        len(availability_summaries),
    )

    # --------------------------------------------------------
    # Build product lookup
    # --------------------------------------------------------

    product_lookup = {}

    for product in product_summaries:

        product_id = get_product_id(product)

        if product_id:
            product_lookup[product_id] = product

    # --------------------------------------------------------
    # Check availability records
    # --------------------------------------------------------

    found = []

    for availability in availability_summaries:

        product_id = get_product_id(
            availability
        )

        if not product_id:
            continue

        price = get_price_data(
            availability
        )

        if not price:
            continue

        list_price = price.get(
            "listPrice"
        )

        msrp = price.get(
            "msrp"
        )

        discount = price.get(
            "discountPercentage"
        )

        # TEMPORARY DEBUG
        if list_price is not None and float(list_price) == 0:
            print()
            print("🔎 ZERO PRICE CANDIDATE")
            print("Product ID:", product_id)
            print("Title:", get_title(product_lookup.get(product_id, {})))
            print("List Price:", list_price)
            print("MSRP:", msrp)
            print("Discount:", discount)
            print("End Date:", availability.get("endDateUtc"))
            print("Actions:", availability.get("actions"))
            print("--------------------------------")
        if not is_100_percent_off(price):
            continue

        product = product_lookup.get(
            product_id,
            {},
        )

        title = get_title(product)

        availability_id = (
            availability.get("availabilityId")
            or availability.get("id")
            or availability.get("AvailabilityId")
        )

        found.append(
            {
                "title": title,
                "productId": product_id,
                "availabilityId": availability_id,
                "listPrice": list_price,
                "msrp": msrp,
                "discount": discount,
            }
        )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    if found:

        for game in found:

            print()
            print("================================")
            print("🎉 100% OFF GAME FOUND")
            print("================================")

            print(
                "Title:",
                game["title"],
            )

            print(
                "Product ID:",
                game["productId"],
            )

            print(
                "Availability ID:",
                game["availabilityId"],
            )

            print(
                "List Price:",
                game["listPrice"],
            )

            print(
                "MSRP:",
                game["msrp"],
            )

            print(
                "Discount:",
                game["discount"],
            )

    return found


# ============================================================
# MAIN
# ============================================================

def main():

    print("================================")
    print("Xbox 100% OFF PAGINATION TEST")
    print("================================")

    session = requests.Session()

    session.headers.update(
        HEADERS
    )

    # --------------------------------------------------------
    # Load first Xbox page
    # --------------------------------------------------------

    state = get_preloaded_state(
        session
    )

    channel = get_channel(
        state
    )

    encoded_ct = (
        channel
        .get("data", {})
        .get("encodedCT")
    )

    encoded_filters = (
        channel
        .get("data", {})
        .get("encodedFilters", "")
    )

    if not encoded_ct:

        raise RuntimeError(
            "Initial continuation token not found"
        )

    print(
        "Channel:",
        CHANNEL_KEY,
    )

    print(
        "Initial token length:",
        len(encoded_ct),
    )

    print()
    print(
        "Starting pagination..."
    )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    total_found = []

    page = 1

    while page <= MAX_PAGES:

        print()
        print("================================")
        print(
            f"REQUESTING PAGE {page}"
        )
        print("================================")

        data = get_next_page(
            session,
            encoded_ct,
            encoded_filters,
        )

        print(
            "✅ Browse response received"
        )

        # ----------------------------------------------------
        # Process current page
        # ----------------------------------------------------

        found = process_page(
            data,
            page,
        )

        total_found.extend(
            found
        )

        # ----------------------------------------------------
        # Get continuation token
        # ----------------------------------------------------

        channel_response = (
            data
            .get("channels", {})
            .get(CHANNEL_KEY, {})
        )

        next_token = (
            channel_response
            .get("encodedCT")
        )

        total_items = (
            channel_response
            .get("totalItems")
        )

        print()
        print(
            "Total Xbox items:",
            total_items,
        )

        if not next_token:

            print()
            print(
                "No continuation token."
            )

            print(
                "Reached final page."
            )

            break

        print(
            "Next token: YES"
        )

        print(
            "Next token length:",
            len(next_token),
        )

        # ----------------------------------------------------
        # Move to next page
        # ----------------------------------------------------

        encoded_ct = next_token

        page += 1

    # --------------------------------------------------------
    # FINAL RESULTS
    # --------------------------------------------------------

    print()
    print("================================")
    print("PAGINATION FINISHED")
    print("================================")

    print(
        "Pages checked:",
        page
        if page <= MAX_PAGES
        else MAX_PAGES,
    )

    print(
        "100% OFF FOUND:",
        len(total_found),
    )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    unique = {}

    for game in total_found:

        key = (
            game["productId"],
            game["availabilityId"],
        )

        unique[key] = game

    if unique:

        print()
        print("================================")
        print("FREE GAMES")
        print("================================")

        for game in unique.values():

            print()
            print(
                "Title:",
                game["title"],
            )

            print(
                "Product ID:",
                game["productId"],
            )

            print(
                "Price:",
                game["listPrice"],
            )

            print(
                "MSRP:",
                game["msrp"],
            )

            print(
                "Discount:",
                game["discount"],
            )

    else:

        print()
        print(
            "No 100% OFF games found "
            "in the pages checked."
        )

    print()
    print("================================")


if __name__ == "__main__":
    main()
