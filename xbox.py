import requests
import re
import json


PAGE_URL = "https://www.xbox.com/en-US/games/browse"

CATALOG_URL = "https://displaycatalog.mp.microsoft.com/v7.0/products"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def get_product_ids():
    response = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    match = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});',
        response.text,
        re.DOTALL
    )

    if not match:
        raise RuntimeError("PRELOADED_STATE not found")

    state = json.loads(match.group(1))

    product_ids = []

    def walk(obj):
        if isinstance(obj, dict):

            for key, value in obj.items():

                if str(key).lower() == "productid":
                    if isinstance(value, str):
                        product_ids.append(value)

                walk(value)

        elif isinstance(obj, list):
            for value in obj:
                walk(value)

    walk(state)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(product_ids))


def get_catalog(product_ids):
    params = {
        "market": "US",
        "languages": "en-us",
        "bigIds": ",".join(product_ids),
    }

    response = requests.get(
        CATALOG_URL,
        params=params,
        headers=HEADERS,
        timeout=30,
    )

    print(f"Catalog HTTP Status: {response.status_code}")

    response.raise_for_status()

    return response.json()


def main():

    print("================================")
    print("Xbox Product Discovery Test")
    print("================================")

    product_ids = get_product_ids()

    print(f"Found {len(product_ids)} unique product IDs")
    print()

    # Test only first 10 for now
    test_ids = product_ids[:10]

    print("Testing these IDs:")
    for product_id in test_ids:
        print(f"  {product_id}")

    print()

    data = get_catalog(test_ids)

    products = data.get("Products", [])

    print(f"Catalog returned {len(products)} products")
    print()

    for product in products:

        product_id = product.get("ProductId")

        title = "Unknown"

        for prop in product.get("LocalizedProperties", []):
            if prop.get("Language") == "en-us":
                title = (
                    prop.get("ProductTitle")
                    or prop.get("Title")
                    or "Unknown"
                )
                break

        print("=" * 60)
        print(f"Product ID: {product_id}")
        print(f"Title:      {title}")

        skus = product.get("DisplaySkuAvailabilities", [])

        for sku_data in skus:

            sku = sku_data.get("Sku", {})
            sku_id = sku.get("SkuId")

            print(f"SKU:        {sku_id}")

            for availability in sku_data.get("Availabilities", []):

                conditions = availability.get("Conditions", {})
                order_data = availability.get(
                    "OrderManagementData",
                    {}
                )
                price = order_data.get("Price", {})

                print(
                    f"  Price: {price.get('ListPrice')} "
                    f"{price.get('CurrencyCode')}"
                )

                print(
                    f"  MSRP:  {price.get('MSRP')} "
                    f"{price.get('CurrencyCode')}"
                )

                print(
                    f"  End:   "
                    f"{conditions.get('EndDate')}"
                )

        print()


if __name__ == "__main__":
    main()
