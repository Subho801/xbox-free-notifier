import requests


URL = "https://www.xbox.com/en-US/games/all-games"


def main():
    print("================================")
    print("Xbox Store Web Test")
    print("================================")

    response = requests.get(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        },
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    print(f"Final URL: {response.url}")
    print(f"Content Length: {len(response.text)}")
    print()

    print(response.text[:10000])


if __name__ == "__main__":
    main()
