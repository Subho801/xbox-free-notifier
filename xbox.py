import requests


URL = "https://reco-public.rec.mp.microsoft.com/channels/Reco/V8.0/Lists/Computed/TopPaid"

PARAMS = {
    "Market": "US",
    "Language": "EN",
    "ItemTypes": "Game",
    "deviceFamily": "Windows.Xbox",
    "count": 10,
    "skipitems": 0,
}


def main():
    print("================================")
    print("Xbox Recommendations API Test")
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
    print(f"URL: {response.url}")
    print()

    response.raise_for_status()

    data = response.json()

    print("SUCCESS")
    print(f"Top-level keys: {list(data.keys())}")
    print()

    print(response.text[:5000])


if __name__ == "__main__":
    main()
