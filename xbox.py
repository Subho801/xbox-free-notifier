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
    print("Xbox Current Deals Test")
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
        re.DOTALL,
    )

    if not match:
        raise RuntimeError("PRELOADED_STATE not found")

    state = json.loads(match.group(1))

    core2 = state.get("core2", {})
    products = core2.get("products", {})

    product_summaries = products.get(
        "productSummaries",
        {}
    )

    availability_summaries = products.get(
        "availabilitySummaries",
        {}
    )

    print(
        f"Product summaries: "
        f"{len(product_summaries)}"
    )

    print(
        f"Availability summaries: "
        f"{len(availability_summaries)}"
    )

    print()
    print("DISCOUNTED PRODUCTS")
    print("===================")

    found = 0

    for product_id, sku_data in availability_summaries.items():

        for sku_id, availability_data in sku_data.items():

            for availability_id, availability in availability_data.items():

                price = availability.get("price", {})

                discount = price.get(
                    "discountPercentage",
                    0
                )

                list_price = price.get(
                    "listPrice"
                )

                msrp = price.get(
                    "msrp"
                )

                end_date = price.get(
                    "endDateUtc"
                )

                # Only genuine discounts
                if (
                    isinstance(discount, (int, float))
                    and discount > 0
                    and isinstance(msrp, (int, float))
                    and msrp > 0
                ):

                    product = product_summaries.get(
                        product_id,
                        {}
                    )

                    title = product.get(
                        "title",
                        "Unknown"
                    )

                    found += 1

                    print()
                    print("--------------------------------")
                    print(f"Title:      {title}")
                    print(f"Product ID: {product_id}")
                    print(f"SKU:        {sku_id}")
                    print(f"Price:      {list_price}")
                    print(f"MSRP:       {msrp}")
                    print(f"Discount:   {discount}%")
                    print(f"Ends:       {end_date}")

    print()
    print("===================")
    print(f"Discounted found: {found}")


if __name__ == "__main__":
    main()
