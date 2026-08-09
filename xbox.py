import requests
import re


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
    print("Xbox Browse Auth Discovery")
    print("================================")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")
    response.raise_for_status()

    html = response.text

    print(f"HTML length: {len(html)}")
    print()

    # Search for references to the browse backend
    patterns = [
        r"emerald\.xboxservices\.com",
        r"xboxcomfd",
        r"x-s2s-authorization",
        r"x-ms-api-version",
        r"apiVersion",
        r"authorization",
        r"Authorization",
        r"clientId",
        r"client_id",
        r"accessToken",
        r"serviceToken",
    ]

    for pattern in patterns:

        matches = list(
            re.finditer(
                pattern,
                html,
                re.IGNORECASE
            )
        )

        print(
            f"{pattern:30} "
            f"{len(matches)} occurrence(s)"
        )

        # Show context around first few matches
        for match in matches[:3]:

            start = max(0, match.start() - 300)
            end = min(
                len(html),
                match.end() + 500
            )

            print()
            print(
                html[start:end]
                .replace("\\u002F", "/")
                .replace("\\u003A", ":")
            )

            print()
            print("-" * 70)


if __name__ == "__main__":
    main()
