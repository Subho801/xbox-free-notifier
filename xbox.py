import requests


URL = "https://displaycatalog.mp.microsoft.com/v7.0/products"

PARAMS = {
    "market": "US",
    "languages": "en-us",
    "bigIds": "9NJRX71M5X9P",
}


def main():
    print("================================")
    print("Xbox Pricing / SKU Test")
    print("================================")

    response = requests.get(
        URL,
        params=PARAMS,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")

    response.raise_for_status()

    data = response.json()
    product = data["Products"][0]

    print(f"Product ID: {product.get('ProductId')}")
    print()

    # Product title
    for prop in product.get("LocalizedProperties", []):
        if prop.get("Language") == "en-us":
            print(f"Title: {prop.get('ProductTitle')}")
            break

    print()
    print("SKUs / AVAILABILITIES")
    print("=====================")

    skus = product.get("DisplaySkuAvailabilities", [])

    print(f"Number of SKUs: {len(skus)}")
    print()

    for index, sku_data in enumerate(skus, 1):

        sku = sku_data.get("Sku", {})

        print(f"SKU #{index}")
        print(f"  SKU ID: {sku.get('SkuId')}")
        print(f"  Trial: {sku.get('Properties', {}).get('IsTrial')}")
        print(f"  Fulfillment: {sku.get('Properties', {}).get('FulfillmentType')}")

        for availability in sku_data.get("Availabilities", []):

            conditions = availability.get("Conditions", {})
            order_data = availability.get("OrderManagementData", {})
            price = order_data.get("Price", {})

            print()
            print("  Availability:")
            print(f"    ID: {availability.get('AvailabilityId')}")
            print(f"    End: {conditions.get('EndDate')}")
            print(f"    Currency: {price.get('CurrencyCode')}")
            print(f"    List Price: {price.get('ListPrice')}")
            print(f"    MSRP: {price.get('MSRP')}")
            print(f"    Actions: {availability.get('Actions')}")

        print()


if __name__ == "__main__":
    main()
