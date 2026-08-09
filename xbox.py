import requests


URL = "https://displaycatalog.mp.microsoft.com/v7.0/products"

PARAMS = {
    "market": "US",
    "languages": "en-us",
    "bigIds": "9NJRX71M5X9P",
}


def main():
    print("================================")
    print("Xbox Microsoft Catalog API Test")
    print("================================")

    response = requests.get(
        URL,
        params=PARAMS,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    print(f"HTTP Status: {response.status_code}")
    print(f"URL: {response.url}")
    print()

    response.raise_for_status()

    data = response.json()

    print("Response received successfully!")
    print(f"Top-level keys: {list(data.keys())}")
    print()

    print("Raw response:")
    print(response.text[:5000])


if __name__ == "__main__":
    main()
