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
    print("Xbox 100% OFF Test")
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
        f"Products: {len(product_summaries)}"
    )

    print(
        f"Availabilities: {len(availability_summaries)}"
    )

    print()
    print("100% OFF CANDIDATES")
    print("===================")

    found = 0

    for product_id, sku_data in availability_summaries.items():

        for sku_id, availability_data in sku_data.items():

            for availability_id, availability in availability_data.items():

                price = availability.get("price", {})

                list_price = price.get("listPrice")
                msrp = price.get("msrp")
                discount = price.get("discountPercentage")
                end_date = price.get("endDateUtc")

                # Genuine temporary free candidate:
                #
                # MSRP > 0
                # Current price == 0
                # Discount >= 99.9%
                # Has a finite end date

                if (
                    isinstance(msrp, (int, float))
                    and msrp > 0
                    and list_price == 0
                    and isinstance(discount, (int, float))
                    and discount >= 99.9
                    and end_date
                    and "9998" not in end_date
                    and "9999" not in end_date
                ):

                    product = product_summaries.get(
                        product_id,
                        {}
                    )

                    title = (
                        product.get("title")
                        or product.get("name")
                        or "Unknown"
                    )

                    found += 1

                    print()
                    print("--------------------------------")
                    print(f"Title:      {title}")
                    print(f"Product ID: {product_id}")
                    print(f"SKU:        {sku_id}")
                    print(f"Availability: {availability_id}")
                    print(f"Current:    {list_price}")
                    print(f"MSRP:       {msrp}")
                    print(f"Discount:   {discount}%")
                    print(f"Ends:       {end_date}")

    print()
    print("===================")
    print(f"100% OFF found: {found}")


if __name__ == "__main__":
    main()
