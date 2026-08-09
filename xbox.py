import requests
import re
from urllib.parse import urljoin


PAGE_URL = "https://www.xbox.com/en-US/games/browse"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def main():

    print("================================")
    print("Xbox Browse Authorization Trace")
    print("================================")

    r = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    scripts = re.findall(
        r'<script[^>]+src=["\']([^"\']+)["\']',
        r.text,
        re.I
    )

    scripts = list(dict.fromkeys(
        urljoin(PAGE_URL, x)
        for x in scripts
    ))

    print(f"JavaScript files: {len(scripts)}")

    keywords = [
        "addAuthorization:!0",
        "addAuthorization:true",
        "MsApiVersion",
        "EmeraldXbetService",
        "getOrFetchXboxToken",
        "xboxToken",
    ]

    for script_number, url in enumerate(scripts, 1):

        try:

            js_response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            if js_response.status_code != 200:
                continue

            js = js_response.text

            for keyword in keywords:

                positions = [
                    m.start()
                    for m in re.finditer(
                        re.escape(keyword),
                        js,
                        re.I
                    )
                ]

                if not positions:
                    continue

                print()
                print("=" * 100)
                print(f"SCRIPT #{script_number}")
                print(url)
                print(f"KEYWORD: {keyword}")
                print(f"OCCURRENCES: {len(positions)}")
                print("=" * 100)

                for pos in positions[:10]:

                    start = max(0, pos - 4000)
                    end = min(
                        len(js),
                        pos + 6000
                    )

                    print(js[start:end])
                    print()
                    print("-" * 100)

        except Exception as e:

            print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
