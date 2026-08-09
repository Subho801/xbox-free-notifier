import json
import re
import requests


PAGE_URL = "https://www.xbox.com/en-US/games/browse"

API_URL = (
    "https://emerald.xboxservices.com/"
    "xboxcomfd/browse?locale=en-US"
)

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
    """Load Xbox browse page and extract PRELOADED_STATE."""

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

    state = json.loads(
        match.group(1)
    )

    print("✅ PRELOADED_STATE parsed")

    return state


def get_channel(state):
    """Get the Xbox browse channel."""

    channel_data = (
        state
        .get("core2", {})
        .get("channels", {})
        .get("channelData", {})
    )

    if CHANNEL_KEY not in channel_data:
        print("❌ Browse channel not found")
        print()
        print("Available channels:")

        for key in channel_data:
            print(" -", key)

        raise RuntimeError(
            "Browse channel not found"
        )

    return channel_data[CHANNEL_KEY]


def get_next_page(
    session,
    encoded_ct,
    encoded_filters=None,
):
    """Request the next Xbox catalog page."""

    payload = {
        "Filters": encoded_filters or "",
        "ReturnFilters": False,
        "ChannelKeyToBeUsedInResponse": CHANNEL_KEY,
        "EncodedCT": encoded_ct,
    }

    print()
    print("Requesting Xbox catalog page...")

    response = session.post(
        API_URL,
        json=payload,
        timeout=30,
    )

    print(
        "Browse API HTTP Status:",
        response.status_code,
    )

    response.raise_for_status()

    return response.json()


def normalize_products(product_summaries):
    """
    Convert product summaries into:
    
        {
            product_id: product_object
        }

    Xbox may return this as either a list or dictionary.
    """

    if isinstance(
        product_summaries,
        list,
    ):

        result = {}

        for product in product_summaries:

            if not isinstance(
                product,
                dict,
            ):
                continue

            product_id = product.get(
                "productId"
            )

            if product_id:
                result[product_id] = product

        return result

    if isinstance(
        product_summaries,
        dict,
    ):

        return product_summaries

    return {}


def normalize_availabilities(
    availability_summaries
):
    """
    Convert availability summaries into
    a simple list of availability objects.
    """

    if isinstance(
        availability_summaries,
        list,
    ):

        return [
            item
            for item in availability_summaries
            if isinstance(item, dict)
        ]

    if isinstance(
        availability_summaries,
        dict,
    ):

        result = []

        for key, value in (
            availability_summaries.items()
        ):

            if isinstance(
                value,
                dict,
            ):

                # Preserve the key if the
                # availability object doesn't
                # contain its own ID.
                if "availabilityId" not in value:
                    value = dict(value)
                    value["availabilityId"] = key

                result.append(value)

            elif isinstance(
                value,
                list,
            ):

                for item in value:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    item = dict(item)

                    if "availabilityId" not in item:
                        item["availabilityId"] = key

                    result.append(item)

        return result

    return []


def find_free_games(
    product_summaries,
    availability_summaries,
):
    """Find genuine temporary 100% OFF games."""

    products_by_id = normalize_products(
        product_summaries
    )

    availability_list = normalize_availabilities(
        availability_summaries
    )

    print()
    print("Normalized products:")
    print(len(products_by_id))

    print(
        "Normalized availabilities:"
    )
    print(len(availability_list))

    found_games = []

    for availability in availability_list:

        product_id = availability.get(
            "productId"
        )

        if not product_id:
            continue

        product = products_by_id.get(
            product_id,
            {}
        )

        title = (
            product.get("title")
            or product.get("name")
            or product.get("displayName")
            or "Unknown"
        )

        price = availability.get(
            "price"
        )

        if not isinstance(
            price,
            dict,
        ):
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

        end_date = price.get(
            "endDateUtc"
        )

        # We only want genuine temporary
        # 100% OFF promotions.
        #
        # Permanent free games generally have:
        #
        #     listPrice = 0
        #     msrp = 0
        #
        # A real giveaway should have:
        #
        #     listPrice = 0
        #     msrp > 0
        #     discount ~= 100%

        is_free = (
            list_price == 0
            and isinstance(
                msrp,
                (int, float),
            )
            and msrp > 0
            and isinstance(
                discount,
                (int, float),
            )
            and discount >= 99.9
        )

        if not is_free:
            continue

        game = {
            "title": title,
            "productId": product_id,
            "availabilityId": availability.get(
                "availabilityId"
            ),
            "listPrice": list_price,
            "msrp": msrp,
            "discountPercentage": discount,
            "endDateUtc": end_date,
        }

        found_games.append(game)

    return found_games


def main():

    print("================================")
    print("Xbox 100% OFF Discovery")
    print("================================")

    session = requests.Session()

    session.headers.update(
        HEADERS
    )

    # --------------------------------
    # Load Xbox browse page
    # --------------------------------

    state = get_preloaded_state(
        session
    )

    # --------------------------------
    # Get browse channel
    # --------------------------------

    channel = get_channel(
        state
    )

    channel_data = channel.get(
        "data",
        {}
    )

    encoded_ct = channel_data.get(
        "encodedCT"
    )

    encoded_filters = channel_data.get(
        "encodedFilters",
        ""
    )

    if not encoded_ct:
        raise RuntimeError(
            "Initial continuation token not found"
        )

    print()
    print(
        "Channel:",
        CHANNEL_KEY,
    )

    print(
        "Initial token length:",
        len(encoded_ct),
    )

    # --------------------------------
    # Get next catalog page
    # --------------------------------

    data = get_next_page(
        session,
        encoded_ct,
        encoded_filters,
    )

    print()
    print(
        "✅ Browse response received"
    )

    # --------------------------------
    # Extract returned data
    # --------------------------------

    channels = data.get(
        "channels",
        {}
    )

    browse_channel = channels.get(
        CHANNEL_KEY,
        {}
    )

    products = browse_channel.get(
        "products",
        []
    )

    total_items = browse_channel.get(
        "totalItems"
    )

    next_encoded_ct = browse_channel.get(
        "encodedCT"
    )

    product_summaries = data.get(
        "productSummaries",
        []
    )

    sku_summaries = data.get(
        "skuSummaries",
        []
    )

    availability_summaries = data.get(
        "availabilitySummaries",
        []
    )

    print()
    print("================================")
    print("CATALOG DATA")
    print("================================")

    print(
        "Products:",
        len(products),
    )

    print(
        "Total Xbox items:",
        total_items,
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

    print(
        "Next token:",
        (
            "YES"
            if next_encoded_ct
            else "NO"
        ),
    )

    if next_encoded_ct:

        print(
            "Next token length:",
            len(next_encoded_ct),
        )

    # --------------------------------
    # Search for 100% OFF
    # --------------------------------

    print()
    print("================================")
    print("CHECKING FOR 100% OFF")
    print("================================")

    free_games = find_free_games(
        product_summaries,
        availability_summaries,
    )

    if not free_games:

        print()
        print(
            "No genuine temporary "
            "100% OFF games found."
        )

    else:

        for game in free_games:

            print()
            print("--------------------------------")
            print("🔥 FREE GAME FOUND")
            print("--------------------------------")

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
                game["discountPercentage"],
            )

            print(
                "Ends:",
                game["endDateUtc"],
            )

    print()
    print("================================")
    print(
        "100% OFF FOUND:",
        len(free_games),
    )
    print("================================")


if __name__ == "__main__":
    main()
