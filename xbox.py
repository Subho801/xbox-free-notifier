import requests


URL = "https://reco-public.rec.mp.microsoft.com/channels/Reco/V8.0/Lists/Computed/Deal"

PARAMS = {
    "Market": "US",
    "Language": "EN",
    "ItemTypes": "Game",
    "deviceFamily": "Windows.Xbox",
    "count": 20,
    "skipitems": 0,
}


def main():
    print("================================")
    print("Xbox Store API Test")
    print("================================")

    response = requests.get(
        URL,
        params=PARAMS,
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    print(f"URL: {response.url}")
    print()

    response.raise_for_status()

    data = response.json()

    print("Response received successfully!")
    print(f"Top-level keys: {list(data.keys())}")

    items = data.get("Items", [])

    print(f"Items found: {len(items)}")
    print()

    for item in items[:5]:
        print("--------------------------------")
        print(f"ID: {item.get('Id')}")
        print(f"Title: {item.get('Title')}")
        print(f"Type: {item.get('ItemType')}")


if __name__ == "__main__":
    main()
