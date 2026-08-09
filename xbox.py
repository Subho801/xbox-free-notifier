import requests


URL = "https://eds.xboxlive.com/media/en-US/browse"


PARAMS = {
    "q": "",
    "maxItems": 50,
    "skipItems": 0,
    "desiredMediaItemTypes": "Game",
    "fields": "DisplayName,ProductId,ProductType",
}


def main():
    print("================================")
    print("Xbox EDS Browse API Test")
    print("================================")

    response = requests.get(
        URL,
        params=PARAMS,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    print(f"URL: {response.url}")
    print()

    response.raise_for_status()

    print(response.text[:10000])


if __name__ == "__main__":
    main()
