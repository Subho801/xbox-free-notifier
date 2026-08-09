import requests
import json


URL = "https://displaycatalog.mp.microsoft.com/v7.0/products"

PARAMS = {
    "market": "US",
    "languages": "en-us",
    "bigIds": "9NJRX71M5X9P",
}


def main():
    print("================================")
    print("Xbox Product Pricing Test")
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

    print("\nPRODUCT:")
    print(json.dumps({
        "ProductId": product.get("ProductId"),
        "LocalizedProperties": product.get("LocalizedProperties"),
        "DisplaySkuAvailabilities": product.get("DisplaySkuAvailabilities"),
    }, indent=2)[:15000])


if __name__ == "__main__":
    main()
